from database.connection import DatabaseConnection

def CreateTables():
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        user_table_query = """CREATE TABLE IF NOT EXISTS users(
                            userid BIGINT AUTO_INCREMENT,
                            username VARCHAR(50) NOT NULL,
                            email VARCHAR(50) NOT NULL UNIQUE,
                            hashpassword VARCHAR(255) NOT NULL,
                            is_active BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY(userid)
                        );"""
        notes_table_query = """CREATE TABLE IF NOT EXISTS notes(
                            notesid BIGINT AUTO_INCREMENT,
                            userid BIGINT,
                            title VARCHAR(255) NOT NULL,
                            content TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            PRIMARY KEY(notesid),
                            FOREIGN KEY(userid) REFERENCES users(userid) ON DELETE CASCADE
                        );"""
        files_table_query = """CREATE TABLE IF NOT EXISTS files(
                            fileid BIGINT AUTO_INCREMENT,
                            userid BIGINT,
                            originalname VARCHAR(255),
                            storedname VARCHAR(255),
                            mimetype VARCHAR(255),
                            size INT,
                            filepath VARCHAR(255),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY(fileid),
                            FOREIGN KEY(userid) REFERENCES USERS(userid) ON DELETE CASCADE
                        );"""
        cursor.execute(user_table_query)
        cursor.execute(notes_table_query)
        cursor.execute(files_table_query)
        cursor.close()
        db_config.close()
        return "Tables Created"
    except Exception as e:
        return f"Something wrong in database/tablesDB:{e}"