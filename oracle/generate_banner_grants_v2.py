import sys, re, os, subprocess, cx_Oracle, creds

#########################
###### CHANGE THIS ######
#########################
users = ["user1", "user2", "user3"]
randompassword = "randompasswordgoeshere"
ADSList = """ENRL-EXT-GENERAL
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


#########################
###### DON'T TOUCH ######
##### ANYTHING BELOW ####
#########################

try:
    import creds
except ModuleNotFoundError:
    print("ERROR:\n============\nYou need to create a creds.py file")
    exit(1)


class BannerGenerator:
    def __init__(self, ADSList):
        database = "BANPROD"

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

        self.__verifyADSList(ADSList)

    # Add the classes from the ADS List
    def __addClasses(self):
        for c in self.classes:
            cmd = (
                "insert into bansecr.gurucls (GURUCLS_USERID, GURUCLS_CLASS_CODE, GURUCLS_ACTIVITY_DATE, GURUCLS_USER_ID)"
                "VALUES ('{0}', '{1}', CURRENT_DATE, 'BANSECR')"
            ).format(self.user, c)

            try:
                self.cur.execute(cmd)
                print("Added " + self.user + " to " + c)
            except cx_Oracle.IntegrityError:
                self.errors.append(self.user + " is already in " + c)

        return

    # Add the groups from the ADS List
    def __addGroups(self):
        for g in self.groups:
            cmd = (
                "insert into bansecr.gurugrp (GURUGRP_USER, GURUGRP_SGRP_CODE, GURUGRP_ACTIVITY_DATE, GURUGRP_USER_ID)"
                " VALUES ('{0}', '{1}', CURRENT_DATE, 'BANSECR')"
            ).format(self.user, g)

            try:
                self.cur.execute(cmd)
                print("Added " + self.user + " to " + g)
            except cx_Oracle.IntegrityError:
                self.errors.append(self.user + " is already in " + g)

        return

    # Create a user if they don't already exist.
    def __createUser(self):
        self.newuser = True
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
            print(x)

        return

    # Grant proxy if they don't have it already
    def __grantProxy(self, user, BANPROXY, BANJSPROXY):
        cur = self.cur

        if BANPROXY == False:
            cur.execute("alter user %s grant connect through BANPROXY" % user)
            print("Granted connect through BANPROXY")

        if BANJSPROXY == False:
            cur.execute("alter user %s grant connect through BANJSPROXY" % user)
            print("Granted connect through BANJSPROXY")

        return

    # Verify someone's proxy access
    def __verifyProxy(self):
        user = self.user
        BANJSPROXY = False
        BANPROXY = False
        cur = self.cur
        cur.execute("SELECT PROXY, CLIENT from proxy_users where CLIENT = '%s'" % user)
        for row in cur:
            if row[0] == "BANPROXY":
                BANPROXY = True
            elif row[0] == "BANJSPROXY":
                BANJSPROXY = True

        if BANPROXY == False or BANJSPROXY == False:
            self.__grantProxy(user, BANPROXY, BANJSPROXY)
        else:
            print("%s already has connect through BANPROXY and BANJSPROXY" % user)

        return

    # Verify the user exists
    def __verifyUser(self):
        user = self.user
        if self.user == "":
            print("ERROR:\n============\nProvide a valid user to grant permissions to")

        #########################
        ##### Validate user #####
        #########################
        cur = self.cur
        cur.execute("SELECT username FROM dba_users WHERE username = '%s'" % user)
        results = len(cur.fetchall())

        if results == 1:
            print("%s already has a Banner account." % user)
        elif results == 0:
            self.__createUser()
        else:
            print("Too many results for the username query")
            raise ValueError()
        return

    # Validate the groups/classes provided are valid
    def __verifyADSList(self, ADSList):
        ###################################
        ##### Validate groups/classes #####
        ###################################
        cur = self.cur
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

    def __grantPerms(self):
        ###################################
        ##########  Add Groups  ###########
        ##########  Add Classes ###########
        ###################################

        # Implicit boolean (only runs if list not empty)
        if self.groups:
            self.__addGroups()
        else:
            print("No groups to add to %s" % user)

        # Implicit boolean (only runs if list not empty)
        if self.classes:
            self.__addClasses()
        else:
            print("No classes to add to %s" % user)

        print("Done with %s. Be sure to add them to the Banner-9 AD group.\n\n" % user)

    def commitAndComplete(self):
        ###################################
        ######## Print any errors #########
        ###################################
        if self.errors:
            print("\nErrors:\n=================")
            for e in self.errors:
                print(e)

        ###################################
        #### Commit and close DB stuff ####
        ###################################
        self.cur.close()
        self.con.commit()
        self.con.close()

    # This is what the script actually calls to do things
    def doTheThing(self, user, randompassword):
        self.user = user
        self.randompassword = randompassword

        # Verify user exists; creates them if not
        self.__verifyUser()

        # Verify user has proxy permissions, else grant them
        # Skip this step if the user was just created
        if not hasattr(self, "newuser"):
            self.__verifyProxy()

        # Grant the permissions after verifying the account
        self.__grantPerms()


if __name__ == "__main__":
    # Must provide an ADSList object to initialize the object
    x = BannerGenerator(ADSList)
    for user in users:
        x.doTheThing(user.upper(), randompassword)

    x.commitAndComplete()
