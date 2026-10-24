from database import DatabaseConnection

def insertNotesRecord(userid:int,title:str,content:str):
    try:
        db = DatabaseConnection()
        cursor = db.cursor()
        # hashed_password 
        sql = "INSERT INTO notes (userid, title, content) VALUES (%s, %s, %s);"
        values = (userid, title, content)
        cursor.execute(sql, values)
        db.commit()
        return True, "Notes Added"
    
    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: insertNotesRecord- {e}"
    finally:
        if db:
            cursor.close()
            db.close()

# get notes by userid
def getNotesByUserid(userid:int,title=None):
    try:
        db = DatabaseConnection()
        cursor = db.cursor(dictionary=True)
        # hashed_password 
        sql = "SELECT * FROM notes WHERE userid = %s"
        values = [userid]
        if title:
            sql += " and title like %s"
            values.append(f"%{title}%")
        sql += "  ORDER BY updated_at desc;"
        cursor.execute(sql, tuple(values))
        notes = cursor.fetchall()
        db.commit()
        return True, notes
    
    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: getNotesByUserid- {e}"
    finally:
        if db:
            cursor.close()
            db.close()

def getNotesByNotesid(notesid: int, userid: int):
    db = None
    cursor = None

    try:
        db = DatabaseConnection()
        cursor = db.cursor(dictionary=True)

        sql = """
            SELECT *
            FROM notes
            WHERE notesid = %s AND userid = %s;
        """

        cursor.execute(sql, (notesid, userid))
        note = cursor.fetchone()

        return True, note

    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: getNotesByNotesid - {e}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def deleteNotesByNotesid(notesid: int, userid: int):
    db = None
    cursor = None

    try:
        db = DatabaseConnection()
        cursor = db.cursor(dictionary=True)

        sql = """
            DELETE 
            FROM notes
            WHERE notesid = %s AND userid = %s;
        """

        cursor.execute(sql, (notesid, userid))
        db.commit()

        return True, "Note Deleted"

    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: getNotesByNotesid - {e}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def checkFileDuplicate(filename: int, userid: int):
    db = None
    cursor = None

    try:
        db = DatabaseConnection()
        cursor = db.cursor(dictionary=True)

        sql = """
            SELECT * FROM files WHERE 
            storedname = %s AND userid = %s;
        """

        cursor.execute(sql, (filename, userid))
        file = cursor.fetchone()
        if file:
            return False, "File already exists!"
        else:
            return True, "File Not Exists"

    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: checkFileDuplicate - {e}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def insertFileMetaDataRecord(filemetadata:tuple[str]):
    db = None
    cursor = None

    try:
        db = DatabaseConnection()
        cursor = db.cursor()

        sql = """
            INSERT INTO files(userid,originalname,storedname,mimetype,size,filepath)
            VALUES(%s,%s,%s,%s,%s,%s);
        """

        cursor.execute(sql, filemetadata)
        db.commit()
        
        return True, "File Saved"

    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: insertFileMetaDataRecord - {e}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def getFileByUserID(userid,title=None):
    try:
        db = DatabaseConnection()
        cursor = db.cursor(dictionary=True)
        # hashed_password 
        sql = "SELECT * FROM files WHERE userid = %s"
        values = [userid]
        if title:
            sql += "AND title LIKE %s"
            values.append(f"%{title}%")
        sql += " ORDER BY created_at desc;"
        cursor.execute(sql, tuple(values))
        files = cursor.fetchall()
        db.commit()
        return True, files
    
    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: getFilesByUserID- {e}"
    finally:
        if db:
            cursor.close()
            db.close()

def getFileByFileID(fileid: int, userid: int):
    db = None
    cursor = None

    try:
        db = DatabaseConnection()
        cursor = db.cursor(dictionary=True)

        sql = """
            SELECT *
            FROM files
            WHERE fileid = %s AND userid = %s;
        """

        cursor.execute(sql, (fileid, userid))
        file = cursor.fetchone()
        if file:
            return True, file
        else:
            return False, "File Found"

    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: getFileByFileID - {e}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def deleteFileByFileid(fileid: int, userid: int):
    db = None
    cursor = None

    try:
        db = DatabaseConnection()
        cursor = db.cursor(dictionary=True)

        sql = """
            DELETE 
            FROM files
            WHERE fileid = %s AND userid = %s;
        """

        cursor.execute(sql, (fileid, userid))
        db.commit()

        return True, "File Deleted"

    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: deleteFileByFileid - {e}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def totalFilesAndNotes(userid):
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.cursor()

        sql = """
            SELECT COUNT(*) 
            FROM files
            WHERE userid = %s;
        """
        cursor.execute(sql, (userid,))
        files_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM notes WHERE userid = %s;",(userid,))
        notes_count = cursor.fetchone()[0]
        db.commit()
        return (files_count,notes_count) 

    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: totalFilesAndNotes - {e}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()




def recentNotes(userid:int):
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.cursor()

        sql = """
            SELECT *
            FROM notes
            WHERE userid = %s ORDER BY updated_at DESC LIMIT 3;
        """
        cursor.execute(sql,(userid,))
        recent_notes = cursor.fetchall()
        db.commit()
        return True, recent_notes

    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: recentNotes - {e}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def updatePassword(email:str,hashpassword:str):
    try:
        db = DatabaseConnection()
        cursor = db.cursor()
        # hashed_password 
        sql = """UPDATE users 
        SET hashpassword = %s
        WHERE email = %s;"""
        values = (hashpassword,email)
        cursor.execute(sql, values)
        db.commit()
        return True, "Password Updated Successfully"
    
    except Exception as e:
        return False, f"Something wrong in database/utilsDB.py: updatePassword- {e}"
    finally:
        if db:
            cursor.close()
            db.close()