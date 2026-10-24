import mysql.connector as SQLC

def DatabaseConnection():
    try:
        db_config = SQLC.connect(
            host = "localhost",
            user = "root",
            password = "root",
            database = "sns_management"
        )
        return db_config
    except Exception as e:
        return f"Something wrongin database/connection.py:{e}"