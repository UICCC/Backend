import mysql.connector

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "school",
    "port": 3306,
}

def get_db():
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)
    try:
        yield cursor, db
    finally:
        cursor.close()
        db.close()
