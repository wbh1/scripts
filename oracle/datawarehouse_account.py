"""
This script is intended to be used to create new users
in the data warehouse.
"""
import argparse

from oracle_db import OracleDB

import cx_Oracle
from cx_Oracle import DatabaseError

RANDOMPASSWORD = "DzKY9aMdU#9gDxTm"
DATABASE = "WHPROD"

#########################
###### DON'T TOUCH ######
##### ANYTHING BELOW ####
#########################

# Parse command line arguments
PARSER = argparse.ArgumentParser(prog="WHPRD User Generator")

PARSER.add_argument("user", type=str, help="Specify the user to create")
PARSER.add_argument(
    "-m",
    "--mirrored_user",
    type=str,
    required=False,
    help="Specify a user whose permissions should be mirrored",
)
PARSER.add_argument(
    "-r",
    "--roles",
    nargs="+",
    required=False,
    type=str,
    help="comma separated list of roles to grant",
)
ARGS = PARSER.parse_args()

USER = ARGS.user
MIRRORED_USER = ARGS.mirrored_user
ROLES = ARGS.roles


class WHPRDGenerator(OracleDB):
    """
    Class used to interface with WHPRD
    """

    def __init__(self, user, database):
        super().__init__(database)
        self.user = user

    def create_user(self):
        """
        Creates a new user, if they do not already exist.
        """
        cur = self.cur
        user = self.user

        # Check if user exists already
        cur.execute(
            "SELECT username FROM dba_users WHERE username = '%s'" % user.upper()
        )
        if len(cur.fetchall()) == 1:
            print("User already exists in WHPRD")
            return

        # Create basic user
        # pylint: disable=line-too-long,bad-continuation
        statements = (
            f"""
            CREATE USER {USER} DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE "TEMP_ADHOC_GROUP" IDENTIFIED BY {RANDOMPASSWORD} PROFILE USERS
            GRANT LU_STANDARD_USER TO {USER}
            ALTER USER {USER} quota 200M ON USERS
            ALTER USER {USER} password expire"""
        )

        commands = [x for x in statements.split("\n") if x != ""]


        for cmd in commands:
            print(cmd.replace(RANDOMPASSWORD, "<redacted>"))
            cur.execute(cmd)

    def mirror_from(self, user2):
        """
        Mirror the permissions of the user provided as an argument
        """
        cur = self.cur
        user = self.user

        cmd = (
            "SELECT granted_role FROM dba_role_privs "
            "WHERE grantee = '{1}' and granted_role not in "
            "(select granted_role from dba_role_privs where grantee = '{0}')"
        ).format(user.upper(), user2.upper())
        cur.execute(cmd)

        results = cur.fetchall()

        for row in results:
            cmd = "grant " + row[0] + " to " + user
            try:
                cur.execute(cmd)
                print(cmd)
            # pylint: disable=broad-except
            except DatabaseError as ex:
                self.errors.append(cmd + " (" + str(ex) + ")")

        cmd = (
            "select owner, table_name, privilege from dba_tab_privs "
            "where grantee = '{1}' and owner != 'SYS'"
            "MINUS select owner, table_name, privilege from dba_tab_privs "
            "where grantee = '{0}' "
            "order by owner, table_name"
        ).format(user.upper(), user2.upper())
        cur.execute(cmd)

        results = cur.fetchall()

        for row in results:
            cmd = "grant " + row[2] + " on " + \
                row[0] + "." + row[1] + " to " + user
            try:
                cur.execute(cmd)
                print(cmd)
            # pylint: disable=broad-except
            except DatabaseError as ex:
                self.errors.append(cmd + " (" + str(ex) + ")")

    def indiv_roles(self, user, roles):
        """
        Grant roles that were specified on the command line.
        """
        for role in roles:
            cmd = "grant " + role + " to " + user
            print(cmd)
            self.cur.execute(cmd)


if __name__ == "__main__":
    WG = WHPRDGenerator(USER, DATABASE)
    WG.create_user()

    if ROLES:
        WG.indiv_roles(USER, ROLES)
    if MIRRORED_USER:
        WG.mirror_from(MIRRORED_USER)

    WG.close()
