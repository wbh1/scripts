import cx_Oracle

# pylint: disable=too-few-public-methods
class OracleDB:
    """
    Generic Class for interacting with Oracle DBs
    """
    def __init__(self, database):
        self.errors = []

        try:
            import creds
        except ModuleNotFoundError:
            print("ERROR:\n============\nYou need to create a creds.py file")
            exit(1)

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
