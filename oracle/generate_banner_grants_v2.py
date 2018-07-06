import sys, re, os, subprocess, cx_Oracle, creds

#########################
###### CHANGE THIS ######
#########################
user            = "WBHEGEDUSK2030"
randompassword  = "randompasswordgoeshere"
ADSList         = (
    """ENRL-EXT-GENERAL
    FINC-EXT-GENERAL
    REGR-EXT-GENERAL 
    FAID-EXT-GENERAL 
    ACCR-EXT-GENERAL
    GENL-M-LETTER
    GENL-M-POPSEL
    GENL-M-QUICKFLOW-CONFIG
    GENL-M-REQUIRED
    GENL-Q-EVENTS
    GENL-Q-IDEN
    GENL-Q-INTL
    GENL-Q-MED
    GENL-Q-POPSEL-CONFIG
    GENL-Q-SURVEY"""
)


#########################
###### DON'T TOUCH ######
##### ANYTHING BELOW ####
#########################


class BannerGenerator:

    def __init__(self):
        database = "BANTEST"

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

    def createUser(self):
        statements = """create user {0} identified by {1}
        alter user {0} temporary tablespace TEMP
        grant LU_DEFAULT_CONNECT, BAN_DEFAULT_CONNECT to {0}
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

        return

    def addGroups(self):
        for g in self.groups:
            cmd = (
                "insert into bansecr.gurugrp (GURUGRP_USER, GURUGRP_SGRP_CODE, GURUGRP_ACTIVITY_DATE, GURUGRP_USER_ID)"
                " VALUES ('{0}', '{1}', CURRENT_DATE, 'BANSECR')"
            ).format(self.user, g)

            try:
                self.cur.execute(cmd)
            except cx_Oracle.IntegrityError:
                self.errors.append(self.user + " is already in " + g)

        return

    def addClasses(self):
        for c in self.classes:
            cmd = (
                "insert into bansecr.gurucls (GURUCLS_USERID, GURUCLS_CLASS_CODE, GURUCLS_ACTIVITY_DATE, GURUCLS_USER_ID)"
                "VALUES ('{0}', '{1}', CURRENT_DATE, 'BANSECR')"
            ).format(self.user, c)

            try:
                self.cur.execute(cmd)
            except cx_Oracle.IntegrityError:
                self.errors.append(self.user + " is already in " + c)

        return

    def verify(self, user, ADSList):
        self.user = user.upper()
        if self.user == "":
            print("ERROR:\n============\nProvide a valid user to grant permissions to")

        #########################
        ##### Validate user #####
        #########################
        cur = self.cur
        cur.execute("SELECT username FROM dba_users WHERE username = '%s'" % user)
        results = len(cur.fetchall())

        if results == 1:
            user_exists = True
        elif results == 0:
            user_exists = False
        else:
            print("Too many results for the username query")
            raise ValueError()

        ###################################
        ##### Validate groups/classes #####
        ###################################
        array = ADSList.replace(" ", "").split("\n")
        for i in array:
            cmd = (
                "select distinct GURCGRP_SGRP_CODE from bansecr.gurcgrp where GURCGRP_SGRP_CODE = '%s'"
                % i
            )
            cur.execute(cmd)
            if len(cur.fetchall()) == 1:
                self.groups.append(i)
            else:
                cmd = (
                    "select distinct GURUCLS_CLASS_CODE from bansecr.gurucls where GURUCLS_CLASS_CODE = '%s'"
                    % i
                )
                cur.execute(cmd)
                if len(cur.fetchall()) == 1:
                    self.classes.append(i)
                else:
                    self.errors.append(i + " is not a valid group/class")

        ###################################
        ##########  Create User ###########
        ##########  Add Groups  ###########
        ##########  Add Classes ###########
        ###################################
        if user_exists == False:
            self.createUser()

        # Implicit boolean (only runs if list not empty)
        if self.groups:
            self.addGroups()
        else:
            print("No groups to add")

        # Implicit boolean (only runs if list not empty)
        if self.classes:
            self.addClasses()
        else:
            print("No classes to add")

        ###################################
        #### Commit and close DB stuff ####
        ###################################
        self.cur.close()
        self.con.commit()
        self.con.close()

        print("Complete")
        if self.errors:
            print("\nErrors:\n=================")
            for e in self.errors:
                print(e + "\n")

    def generate(self, user, randompassword, ADSList):
        self.randompassword = randompassword
        self.verify(user, ADSList)


if __name__ == "__main__":
    x = BannerGenerator()
    x.generate(user, randompassword, ADSList)
