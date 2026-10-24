from database import DatabaseConnection

def total_users():
    try:
        db = DatabaseConnection()
        cursor = db.cursor()
        sql = "SELECT COUNT(*) FROM accounts"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
    except Exception as e:
        print(f"Something wrong in utility.py: totalUsers - {e}")
    finally:
        if db:
            cursor.close()
            db.close()


def retrieve_data(email):
    try:
        db = DatabaseConnection()
        cursor = db.cursor()
        sql = "SELECT * FROM users WHERE email = %s;"
        values = (email,)
        cursor.execute(sql, values)
        user = cursor.fetchone()
        if not user:   # if record not found 
            return True
        else:
            return False
    except Exception as e:
        print(f"Something wrong in database/getQueries.py: retrieveData - {e}")
    finally:
        if db:
            cursor.close()
            db.close()

def get_user_by_email(email,data = False):
    try:
        db = DatabaseConnection()
        cursor = db.cursor(dictionary=True)

        sql = "SELECT * FROM users WHERE email = %s;"
        values = (email,)

        cursor.execute(sql, values)

        user = cursor.fetchone()
        # cursor.close()
        # db.close()
        if data == True:
            if user:
                return True,user
            else:
                return False, "Check your user credentials"
        if not user: # if record not found
            return True # user not exists
        

    except Exception as e:
        print(f"Something wrong in database/getQueries.py: get_user_by_email - {e}")
        return None

    finally:
        if db:
            cursor.close()
            db.close()