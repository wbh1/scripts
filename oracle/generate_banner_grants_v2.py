"""
This script is intended to be used to add users to
a list of security groups & classes that is usually provided by ADS
in New Hire Checklist tickets and other permissions requests.

If the user does not exist, it will create them with the same grants
that would otherwise be given during creation in the Banner Admin
web interface.
"""

import cx_Oracle
from oracle_db import OracleDB
import password

# Change this
DATABASE = "BANPROD"
USERS = ["user1", "user2", "user3"]
GROUPS_AND_CLASSES = """REGR-EMP-ACADEMIC-EVAL-01
ENRL-EXT-GENERAL
GENL-M-REQUIRED
REGR-EMP-GENERAL
GENL-EXT-GENERAL
GENL-Q-IDEN"""


# Don't touch anything below
class BannerGenerator(OracleDB):
    """
    This class is used to interface with the Banner database
    by creating users and adding security groups/classes.
    """

    # List of roles all Banner users should have
    ROLES = [
        "LU_DEFAULT_CONNECT",
        "BAN_DEFAULT_CONNECT",
        "BAN_DEFAULT_M",
        "BAN_DEFAULT_MR",
        "BAN_DEFAULT_Q",
    ]

    # All Banner users should have one of these default roles
    DEFAULT_ROLES = ["LU_DEFAULT_CONNECT", "BAN_DEFAULT_CONNECT", "DBA"]

    def __init__(self, ADSList, database):
        super().__init__(database)

        self.classes = []
        self.groups = []
        self.errors = []
        self.user_exists = False
        self.randompassword = password.generate()
        self.user = ""
        self._verify_ADS_list(ADSList)

    # Add the classes from the ADS List
    def _add_classes(self):
        for c in self.classes:
            cmd = (
                "insert into bansecr.gurucls "
                "(GURUCLS_USERID, GURUCLS_CLASS_CODE, GURUCLS_ACTIVITY_DATE, GURUCLS_USER_ID) "
                "VALUES ('{0}', '{1}', CURRENT_DATE, 'BANSECR')"
            ).format(self.user, c)

            try:
                self.cur.execute(cmd)
                print("Added " + self.user + " to " + c)
            except cx_Oracle.IntegrityError:
                self.errors.append(self.user + " is already in " + c)

    # Add the groups from the ADS List
    def _add_groups(self):
        for g in self.groups:
            cmd = (
                "insert into bansecr.gurugrp "
                "(GURUGRP_USER, GURUGRP_SGRP_CODE, GURUGRP_ACTIVITY_DATE, GURUGRP_USER_ID) "
                "VALUES ('{0}', '{1}', CURRENT_DATE, 'BANSECR')"
            ).format(self.user, g)

            try:
                self.cur.execute(cmd)
                print("Added " + self.user + " to " + g)
            except cx_Oracle.IntegrityError:
                self.errors.append(self.user + " is already in " + g)

    # Create a user if they don't already exist.
    def _create_user(self):
        statements = """create user {0} identified by {1}
        alter user {0} temporary tablespace TEMP
        grant LU_DEFAULT_CONNECT, BAN_DEFAULT_CONNECT, BAN_DEFAULT_M, BAN_DEFAULT_MR, BAN_DEFAULT_Q to {0}
        alter user {0} default role LU_DEFAULT_CONNECT, BAN_DEFAULT_CONNECT
        alter user {0} default tablespace users
        alter user {0} profile default
        alter user {0} grant connect through BANJSPROXY
        alter user {0} grant connect through BANPROXY""".format(
            self.user, self.randompassword
        )

        array = statements.split("\n")

        for x in array:
            cur = self.cur
            cur.execute(x)
            print(x.replace(self.randompassword, "<redacted>"))

    # Grant proxy if they don't have it already
    def _grant_proxy(self, user, BANPROXY, BANJSPROXY):
        cur = self.cur

        if not BANPROXY:
            cur.execute("alter user %s grant connect through BANPROXY" % user)
            print("Granted connect through BANPROXY")

        if not BANJSPROXY:
            cur.execute(
                "alter user %s grant connect through BANJSPROXY" % user)
            print("Granted connect through BANJSPROXY")

    def _add_roles(self, roles: list):
        for role in roles:
            STMT = f"GRANT {role} to {self.user}"
            self.cur.execute(STMT)
            print(STMT)

    def _verify_roles(self):
        user = self.user
        cur = self.cur
        roles = []
        default_roles = []
        missing_roles = []

        SELECT_ROLES = (
            "SELECT GRANTED_ROLE, DEFAULT_ROLE from dba_role_privs"
            f" WHERE grantee = '{user}'"
        )

        cur.execute(SELECT_ROLES)

        for role, default in cur.fetchall():
            roles.append(role)
            if default == "YES":
                default_roles.append(role)

        # This intersects the lists. Everything in self.ROLES should be in 'roles'
        # So it should return empty and therefore be False
        missing_roles = set(self.ROLES).difference(roles)
        if missing_roles:
            print(f"{user} is missing the roles: {missing_roles}. Fixing...")
            self._add_roles(missing_roles)
        else:
            print(f"{user} has all the correct database roles required for Banner.")

        if not set(default_roles).intersection(self.DEFAULT_ROLES):
            print(f"{user} does not have a valid default role. Fixing...")
            STMT = f"alter user {user} default role LU_DEFAULT_CONNECT, BAN_DEFAULT_CONNECT"
            self.cur.execute(STMT)
            print(STMT)
        else:
            print(f"{user} has a valid default database role.")

    def _verify_proxy(self):
        """Verify someone's proxy access"""
        user = self.user
        BANJSPROXY = False
        BANPROXY = False
        cur = self.cur
        cur.execute(
            "SELECT PROXY, CLIENT from proxy_users where CLIENT = '%s'" % user)
        for row in cur:
            if row[0] == "BANPROXY":
                BANPROXY = True
            elif row[0] == "BANJSPROXY":
                BANJSPROXY = True

        if not BANPROXY or not BANJSPROXY:
            self._grant_proxy(user, BANPROXY, BANJSPROXY)
        else:
            print("%s already has connect through BANPROXY and BANJSPROXY" % user)

    def _verify_user_exists(self):
        """
        Verifies that the user exists.
        Returns True if they do; False if not.
        """
        user = self.user
        if self.user == "":
            print(
                "ERROR:",
                "============",
                "Provide a valid user to grant permissions to",
                sep="\n",
            )

        # Validate user
        cur = self.cur
        cur.execute(
            "SELECT username FROM dba_users WHERE username = '%s'" % user)
        results = len(cur.fetchall())

        if results == 1:
            print("%s already has a Banner account." % user)
            return True

        if results == 0:
            print("%s does not have an existing Banner account. Creating..." % user)
            return False

        # If neither of the above 'if' statements return,
        # then too many usernames returned.
        print("Too many results for the username query")
        raise ValueError()

    def _verify_ADS_list(self, ADSList):
        """Validate the groups/classes provided are valid"""
        cur = self.cur
        array = ADSList.replace(" ", "").split("\n")

        # TODO: Rewrite to check all groups at once.
        for i in array:
            cmd = (
                "select distinct GURCGRP_SGRP_CODE "
                "from bansecr.gurcgrp where GURCGRP_SGRP_CODE = '%s'" % i
            )
            cur.execute(cmd)
            if len(cur.fetchall()) == 1:
                self.groups.append(i)
            else:
                cmd = (
                    "select distinct GURUCLS_CLASS_CODE "
                    "from bansecr.gurucls where GURUCLS_CLASS_CODE = '%s'" % i
                )
                cur.execute(cmd)
                if len(cur.fetchall()) == 1:
                    self.classes.append(i)
                else:
                    self.errors.append(i + " is not a valid group/class")

    def _grant_perms(self):
        """add groups and classes"""
        # Implicit boolean (only runs if list not empty)
        if self.groups:
            self._add_groups()
        else:
            print("No groups to add to %s" % self.user)

        # Implicit boolean (only runs if list not empty)
        if self.classes:
            self._add_classes()
        else:
            print("No classes to add to %s" % self.user)

        print(
            "\nDone with %s. Be sure to add them to the Banner-9 AD group.\n\n"
            % self.user
        )

    # This is what the script actually calls to do things
    def doTheThing(self, user):
        """
        Verifies user exists in Banner. Creates them otherwise.
        Grants the user permissions in Banner.
        Fixes their proxy access if needed.
        """
        self.user = user

        # Verify user exists; creates them if not
        self.user_exists = self._verify_user_exists()
        if not self.user_exists:
            self._create_user()

        # Verify user has proxy permissions, else grant them
        # Verify user has correct roles/default roles, else grant them
        # Skip this step if the user was just created
        if self.user_exists:
            self._verify_proxy()
            self._verify_roles()

        # Grant the permissions after verifying the account
        print()
        self._grant_perms()


if __name__ == "__main__":
    # Must provide an ADSList object to initialize the object
    BG = BannerGenerator(GROUPS_AND_CLASSES, DATABASE)
    for u in USERS:
        BG.doTheThing(u.upper())
    BG.close()
