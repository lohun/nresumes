import mysql
import mysql.connector


db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "nresume"
)

def initialize():
    return db.cursor()