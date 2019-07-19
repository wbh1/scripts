"""
This script is intended to be used to create new users
in the data warehouse.
"""
import argparse

import cx_Oracle
from cx_Oracle import DatabaseError

RANDOMPASSWORD = "randompasswordgoeshere"

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

try:
    import creds
except ModuleNotFoundError:
    print("ERROR:\n============\nYou need to create a creds.py file")
    exit(1)


class WHPRDGenerator:
    """
    Class used to interface with WHPRD
    """

    def __init__(self, user):
        database = "WHPROD"
        self.user = user
        self.errors = []

        try:
            u_ora = creds.user
        except AttributeError:
            print(
                "ERROR:",
                "============",
                "Specify a user attribute in a creds.py file in the same directory as this script",
                sep="\n",
            )
            exit(1)

        try:
            p_ora = creds.password
        except AttributeError:
            print(
                "ERROR:",
                "============",
                "Specify a user attribute in a creds.py file in the same directory as this script",
                sep="\n",
            )
            exit(1)

        self.con = cx_Oracle.connect(u_ora, p_ora, database)
        self.cur = self.con.cursor()

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
        statements = """CREATE USER {0} IDENTIFIED BY {1} DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE \"TEMP_ADHOC_GROUP\"
            GRANT LU_STANDARD_USER to {0}
            ALTER USER {0} quota 200M ON USERS
            ALTER USER {0} password expire""".format(
            USER, RANDOMPASSWORD
        )

        commands = statements.split("\n")

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
                self.errors.append(cmd + " (" + str(ex) +")")

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
            cmd = "grant " + row[2] + " on " + row[0] + "." + row[1] + " to " + user
            try:
                cur.execute(cmd)
                print(cmd)
            # pylint: disable=broad-except
            except DatabaseError as ex:
                self.errors.append(cmd + " (" + str(ex) +")")

    def indiv_roles(self, user, roles):
        """
        Grant roles that were specified on the command line.
        """
        for role in roles:
            cmd = "grant " + role + " to " + user
            print(cmd)
            self.cur.execute(cmd)

    def close(self):
        """
        Close cursor, commit transaction, close connection.
        """
        ###################################
        ######## Print any errors #########
        ###################################
        if self.errors:
            print("\nErrors:\n=================")
            for err in self.errors:
                print(err)

        ###################################
        #### Commit and close DB stuff ####
        ###################################
        self.cur.close()
        self.con.commit()
        self.con.close()


if __name__ == "__main__":
    WG = WHPRDGenerator(USER)
    WG.create_user()

    if ROLES:
        WG.indiv_roles(USER, ROLES)
    if MIRRORED_USER:
        WG.mirror_from(MIRRORED_USER)

    WG.close()
