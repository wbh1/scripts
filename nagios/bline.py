import csv, logging, mysql.connector

logger = logging.getLogger('bline.py')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s || [%(levelname)s] || %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

mydb = mysql.connector.connect(
  host="nagios.liberty.edu",
  user="wbhegedus",
  passwd="",
  database="nagiosql"
)

cursor = mydb.cursor()

with open("/Users/wbhegedus/Desktop/bline.csv") as csvfile:
  reader = csv.reader(csvfile)
  changes = 0
  for row in reader:
    try:
      stmt = ("UPDATE tbl_host set address = '{1}' where lower(host_name) like lower('{0}%')").format(row[0], row[1])
      cursor.execute(stmt)
      logger.info("Updated IP for {0}".format(row[0]))
      changes += 1
    except Exception as e:
      logger.error("Unable to execute: {0} -- {1}".format(stmt, e))

mydb.commit()
print(changes, "records affected")
cursor.close()
