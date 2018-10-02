import cx_Oracle
import creds
import time

username = creds.user
password = creds.password

groups = """ENRL-EMP-ADMISSIONS-01
ENRL-EMP-GENERAL
REGR-EXT-ADMISSIONS-01
REGR-EXT-GENERAL"""
g_array = groups.split("\n")

users = """cmmoore6"""
array = users.split("\n")

database = "BANPROD"


class DBExecute:
    def __init__(self, database):
        try:
            self.con = cx_Oracle.connect(username, password, database)
        except cx_Oracle.DatabaseError:
            raise

        ## Create the cursor and execute the query
        self.cur = self.con.cursor()

    def runCmd(self, cmd):
        cur = self.cur
        cur.execute(cmd)

    def cleanUp(self):
        self.cur.close()
        self.con.commit()
        self.con.close()


DB = DBExecute(database)

for user in array:
    for group in g_array:
        cmd = (
            "DELETE FROM bansecr.gurugrp WHERE gurugrp_sgrp_code = '%s' AND gurugrp_user = '%s'"
            % (group, user.upper())
        )
        DB.runCmd(cmd)
        print("Removed %s from %s" % (group, user.upper()))

DB.cleanUp()
