import cx_Oracle
import os


class OracleDB:
    """
    Generic Class for interacting with Oracle DBs
    """
    def __init__(self, database):
        try:
            import creds
            try:
                u_ora = creds.user
            except AttributeError:
                print(
                    "ERROR:",
                    "============",
                    ("Specify a user attribute in a creds.py "
                     "file in the same directory as this script"),
                    sep="\n",
                )
                exit(1)

            try:
                p_ora = creds.password
            except AttributeError:
                print(
                    "ERROR:",
                    "============",
                    ("Specify a password attribute in a creds.py "
                     "file in the same directory as this script"),
                    sep="\n",
                )
                exit(1)
        except ModuleNotFoundError:
            try:
                u_ora, p_ora = self.get_creds(database)
            except:  # noqa: E722
                print("ERROR:\n============\nYou need to create a creds.py "
                      "file or setup use the OS credential locker")
                exit(1)

        self.con = cx_Oracle.connect(u_ora, p_ora, database)
        self.cur = self.con.cursor()
        self.errors = []

    def close(self):
        """
        Close cursor, commit transaction, close connection.
        """
        # Print any errors
        if self.errors:
            print("\nErrors:\n=================")
            for err in self.errors:
                print(err)

        # Commit and close DB stuff
        self.cur.close()
        self.con.commit()
        self.con.close()

    def get_creds(self, service):
        import toml
        import keyring
        config_path = os.path.join(os.path.dirname(__file__), 'config.toml')
        config = toml.load(config_path)
        user = config['username']
        ring = keyring.get_keyring()
        password = ring.get_password(service, user)
        if password is None:
            import getpass
            print(f"Password for {user} is not on file. "
                  "Please provide {service} password...")
            password = getpass.getpass()
            ring.set_password(service, user, password)
            password = ring.get_password(service, user)
        return user, password
