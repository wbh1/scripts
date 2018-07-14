import sys, re, os, subprocess, cx_Oracle, creds, argparse

randompassword  = "randompasswordgoeshere"

#########################
###### DON'T TOUCH ######
##### ANYTHING BELOW ####
#########################

# Parse command line arguments
parser = argparse.ArgumentParser(prog='PROG',formatter_class=argparse.MetavarTypeHelpFormatter)

parser.add_argument('-u', '--user',type=str, required=True, help='Specify the user to create')
parser.add_argument('-m','--mirror', type=bool, required=False, help='Copy another user\'s permissions')
parser.add_argument('-u2', '--user2',type=str, required=False, help='User to copy perms from')
args = parser.parse_args()

if args.mirror:
    if args.user2 is None:
        parser.error("Must specify a user to copy from with '-u2' or '--user2'.")
    else:
        user2 = args.user2

user = args.user
mirror = args.mirror

try:
    import creds
except ModuleNotFoundError:
    print("ERROR:\n============\nYou need to create a creds.py file")
    exit(1)


class WHPRDGenerator:

    def __init__(self):
        database = "WHPROD"

        try:
            u_ora = creds.user
        except:
            print(
                "ERROR:\n============\nSpecify a user attribute in a creds.py file in the same directory as this script"
            )
            exit(1)

        try:
            p_ora = creds.password
        except:
            print(
                "ERROR:\n============\nSpecify a user attribute in a creds.py file in the same directory as this script"
            )
            exit(1)

        self.classes = []
        self.groups = []
        self.errors = []

        try:
            self.con = cx_Oracle.connect(u_ora, p_ora, database)
            self.cur = self.con.cursor()
        except cx_Oracle.DatabaseError:
            raise

    def create(self, user):
        cur = self.cur
        
        # Check if user exists already
        cur.execute("SELECT username FROM dba_users WHERE username = '%s'" % user.upper())
        if len(cur.fetchall()) == 1:
            print("ERROR: User already exists in WHPRD")
            exit(1)

        # Create basic user
        commands = [
            "CREATE USER {0} IDENTIFIED BY {1} DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE \"TEMP_ADHOC_GROUP\"",
            "GRANT LU_STANDARD_USER to {0}",
            "ALTER USER {0} quota 200M ON USERS",
            "ALTER USER {0} password expire"
        ]

        for cmd in commands:
            cmd = cmd.format(user, randompassword)
            print(cmd)
            cur.execute(cmd)

    def mirror(self, user, user2):
        cur = self.cur

        cmd = (
            "SELECT granted_role FROM dba_role_privs "
            "WHERE grantee = '{1}' and granted_role not in "
            "(select granted_role from dba_role_privs where grantee = '{0}')"
        ).format(user.upper(), user2.upper())
        cur.execute(cmd)

        results = cur.fetchall()

        for row in results:
            cmd = "grant " +row[0]+ " to " + user
            try:
                cur.execute(cmd)
                print(cmd)
            except:
                print("Could not execute " + cmd)

        cmd = (
            "select owner, table_name, privilege from dba_tab_privs "
            "where grantee = '{1}' "
            "MINUS select owner, table_name, privilege from dba_tab_privs "
            "where grantee = '{0}' "
            "order by owner, table_name"
        ).format(user.upper(), user2.upper())
        cur.execute(cmd)

        results = cur.fetchall()

        for row in results:
            cmd = "grant " +row[2]+ " on " +row[0]+"."+row[1]+ " to " +user
            try:
                cur.execute(cmd)
                print(cmd)
            except:
                print("Could not execute " + cmd)
    
    def close(self):
        self.cur.close()
        self.con.close()


if __name__ == "__main__":
    if not mirror:
        x = WHPRDGenerator()
        x.create(user)
        x.close()
    else:
        x = WHPRDGenerator()
        x.create(user)
        x.mirror(user,user2)
        x.close()
