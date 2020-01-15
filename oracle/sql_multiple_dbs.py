import cx_Oracle
import creds

username = creds.user
password = creds.password

DBs = ["BANPPRD", "BANTEST", "APPDEV", "FINDEV"]

COMMANDS = """CREATE USER USERNAMEHERE IDENTIFIED BY passwordgoeshere DEFAULT TABLESPACE USERS
GRANT DBA TO USERNAMEHERE
ALTER USER USERNAMEHERE DEFAULT ROLE DBA"""


def connectandrun(database):
    try:
        con = cx_Oracle.connect(username, password, database)
    except cx_Oracle.DatabaseError:
        print("Failed to connect to %s" % database)
        raise

    # Create the cursor and execute the query
    cur = con.cursor()
    print("\n######### " + database + " #########\n")
    for cmd in COMMANDS.split("\n"):
        try:
            print(cmd)
            cur.execute(cmd)
        except Exception:
            print("Failed to execute on %s\n%s" % (database, cmd))

    cur.close()
    con.close()


for db in DBs:
    connectandrun(db)
