from database import DatabaseConnection

# insert user data into table

def add_user(name,email,password):
    try:
        username = name
        email = email
        password = password
        db = DatabaseConnection()
        cursor = db.cursor()
        # hashed_password 
        sql = "INSERT INTO users (username, email, hashpassword, is_active) VALUES (%s, %s, %s,%s)"
        values = (username, email, password,1)
        cursor.execute(sql, values)
        db.commit()
        return True, "User Successfully Registered!"

    except Exception as e:
        return False, f"Something wrong in database/insetQueries.py:- {e}"
    finally:
        if db:
            cursor.close()
            db.close()

