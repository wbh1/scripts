import cx_Oracle
import creds
import time

username = creds.user
password = creds.password
tables = """saturn.srtpers
saturn.srttest
saturn.srtiden
saturn.srtprel
zsaturn.sztdata
saturn.srtaddr
saturn.srtemal
saturn.srthsch
saturn.srtints
saturn.srtpers
saturn.srtprel
saturn.srttele
saturn.stvtesc"""

array = tables.split("\n")

DBs = ['BANTEST']

def connectandrun(database):
    try:
        con = cx_Oracle.connect (username,password,database)
    except cx_Oracle.DatabaseError:
        raise

    ## Create the cursor and execute the query
    cur = con.cursor()
    print("\n######### " + database + " #########\n")
    cmd = "create user leads_Bannertest identified by insertpasswordhere"
    cur.execute(cmd)
    time.sleep(1)
    
    for table in array:
        try:
            cmd = "grant select on %s to leads_Bannertest" % table
            print(cmd)
            cur.execute(cmd)
            time.sleep(1)
        except Exception as e:
            print("FAILED: " + cmd + "\n" + str(e))
    
    cur.close()
    con.close()

for db in DBs:
    connectandrun(db)