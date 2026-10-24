from flask import Flask,request,redirect,render_template, session, url_for,flash,send_file
from database import CreateTables, retrieve_data,get_user_by_email,insertNotesRecord,getNotesByUserid,getNotesByNotesid,deleteNotesByNotesid,checkFileDuplicate
import random
from database import insertFileMetaDataRecord
from utils import sendEmail,generateHashPassword,verifyHashPassword
from email_templates import EmailTemplates
import os 
import sys
from werkzeug.utils import secure_filename
import mimetypes
from database import add_user,getFileByUserID,getFileByFileID,deleteFileByFileid,totalFilesAndNotes
from database import *
from itsdangerous import TimedSerializer,BadTimeSignature,URLSafeTimedSerializer,BadSignature,SignatureExpired




# flask instance
app = Flask(__name__)

# session secret key
app.secret_key = "gaddamabinayateja@gmail.com"
serializer = URLSafeTimedSerializer(app.secret_key)

# create upload folder if not exist
if not os.path.exists('uploads'):
    os.mkdir('uploads')

# ========================================
#               Auth Routes
# ========================================
# home route
@app.route("/")
def home():
    if request.method == 'GET':
        return render_template('register.html') 
    return render_template('registerś.html')
        

@app.route("/register", methods = ['GET','POST'])
def register():
    # GET Request
    if request.method == 'GET':
        return render_template('register.html') 
    # POST Request
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # check password match
        if password != confirm_password:
            # password miss match
            flash("Passwords do not match!", "err")
            return redirect('/register')
        # check whether user exists in the database
        if retrieve_data(email=email):
            # if user not exists
            # verify otp
            OTP = random.randint(1000,9999)
            # store otp in session
            session['otp'] = OTP
            session['username'] = username
            session['email'] = email
            session['password'] = password

            # send otp to mail
            status, msg = sendEmail(to_email=email,
                                    subject="SNS - OTP Verification for Register",
                                    body=EmailTemplates.OTPEmailTemplate(username = username,otp = OTP)
                                    )
            if status == True:
                # redirect to verify otp page
                # flask msg Email sent
                return redirect(url_for('verifyOTP'))
        else:
            flash("Email already registered. Please login.", "err")
            return redirect(url_for('register'))
        return msg
        
# verify OTP
@app.route("/verify-otp", methods = ['GET','POST'])
def verifyOTP():
    if 'otp' not in session:
        return redirect(url_for('register'))
    if request.method == 'GET':
        return render_template('verify_otp.html')
    if request.method == 'POST':
        otp = int(request.form.get('otp'))
        if otp == session['otp']:
            # store user data in users table
            hash_password = generateHashPassword(password=session['password'])
            status,msg = add_user(name=session['username'],
                                  email=session['email'],
                                  password=hash_password)
            # redirect to login page
            if status == True:
                flash("OTP sent successfully to your email!", "msg")
                return redirect(url_for('login'))
            else:
                flash(f"Failed to send OTP: {msg}", "err")
                return msg
        flash(f"Enter Valid OTP ", "err")
        return redirect(url_for('verifyOTP'))
    pass

@app.route("/login", methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # check whether user already exists
        status, data = get_user_by_email(email=email,data=True)
        if status == False: # if user not exists
            flash(data, "err")
            return redirect(url_for('login'))
        # if user exists
        print(data)
        hash_password = data['hashpassword']
        if verifyHashPassword(password,hash_password=hash_password):
            # Adding credentials to session
            session.clear()
            session['userid'] = data['userid']
            session['username'] = data['username']
            session['email'] = data['email']
            # redirect to dash board
            flash(f"Hello, {data['username']}, Welcome to SNS Management", "msg")
            return redirect(url_for('dashboard'))
        flash("Check your password", "err")
        return redirect(url_for('login'))

# generate token
def generate_token(email:str):
    token = serializer.dumps(email,salt="forgot_password")
    return token

# verify token
def verifyToken(token):

    try:
        data = serializer.loads(
            token,
            max_age=600,
            salt="forgot_password"
        )

        return data

    except SignatureExpired:
        flash("URL time expired", "err")
        return redirect('/login')

    except BadTimeSignature:
        flash("Invalid URL", "err")
        return redirect('/login')

# forgot password route
@app.route("/forgot-password", methods =['GET','POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template("forgot_password.html")
    if request.method == 'POST':
        email= request.form.get('email')
        status,user = get_user_by_email(email=email,data=True)
        if status == False:
            flash(user,'err')
            return(redirect(url_for('forgot_password')))
        # generate token
        reset_token = generate_token(email=email)
        reset_link = url_for('reset_password',token = reset_token,_external=True)
        status,msg = sendEmail(to_email=email,subject="SNS App Password Reset",
                               body=EmailTemplates.ResetPasswordTemplate(
                                   link=reset_link,
                                   username=user['username']
                               ))
        if status == True:
            flash("Password Reset link sent to registered email",'msg')
            return redirect(url_for('login'))
        else:
            flash(msg,'err')
            return redirect(url_for('login'))


# reset password route
@app.route("/reset-password/<token>",methods = ['GET','POST'])
def reset_password(token):
    # verify token
    email = verifyToken(token=token)

    if request.method == 'GET':
        return render_template('reset_password.html',token=token)
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirmpassword')
        print(password,confirm_password)
        if password != confirm_password:
            flash("Password miss match",'err')
            return redirect(f"/reset-password/{token}")
        # generate hashpassword
        hash_password = generateHashPassword(password=password)
        # update passsword in database by using email
        status,msg = updatePassword(email=email,hashpassword=hash_password)
        if status == False:
            flash(msg,'err')
            return redirect('/login')
        flash(msg,'msg')
        return redirect('/login')




# files route
@app.route('/files',methods = ['GET','POST'])
def files():
    if "userid" not in session:
        return redirect(url_for('login'))
    userid = session.get('userid')
    if request.method == "GET":
        # get the files by using userid
        title = request.args.get('search')
        status,files = getFileByUserID(userid=userid,title=title)
        if status == True:
            return render_template('files.html',files = files)
        else:
            flash(files,"err")
            return render_template('files.html')
    
        


# upload file
@app.route('/files/uploadfile', methods = ['GET','POST'])
def uploadfile():
    if 'userid' not in session:
        return redirect(url_for('login'))
    userid = session.get('userid')
    if request.method == 'GET':
        return render_template('uploadfile.html')
    if request.method == 'POST':
            file = request.files.get('file')
            # get file meta data
            original_filename = file.filename
            # generate secure file name
            filename_secure = secure_filename(filename=original_filename)
            # check file in allowed exstension
            file_type = filename_secure.split(".")[-1].strip()
            alloed_types = ['png','jpg','jpeg','pdf','csv','doc']
            if file_type not in alloed_types:
                flash("Invalid File type", "err")
                return redirect(url_for('uploadfile'))
            
            # check file duplicate file exist or not
            status, msg = checkFileDuplicate(filename=filename_secure,userid=userid)

            if status == False:
                flash(msg,"err")
                return redirect(url_for('files'))
            

            # file path
            file_path = os.path.join('uploads',filename_secure)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            file_mime_type =  mimetypes.guess_type(file_path)[0]
            
            # print("------------------File meta data---------------")
            # print("Original name :",original_filename)
            # print("Secure name :",filename_secure)
            # print("File type :",file_type)
            # print("File path :",file_path)
            # print("File size :",file_size)
            # print("File mime type :",file_mime_type)
            data = (userid,original_filename,filename_secure,file_mime_type,file_size,file_path)
            status,msg = insertFileMetaDataRecord(filemetadata=data)
            if status == True:
                flash(msg,"msg")
                return redirect(url_for('files'))
            else:
                flash(msg,"err")
                return redirect(url_for('uploadfile'))

# view file
@app.route('/files/view/<fileid>')
def viewfile(fileid):
    if 'userid' not in session:
        return redirect(url_for('login'))
    userid = session['userid']
    # get filedata using fileid
    status, file = getFileByFileID(fileid=fileid,userid=userid)
    if status == False:
        flash(file, 'err')
        return redirect(url_for('files'))
    filepath = file['filepath']
    mime_type = file['mimetype']
    return send_file(path_or_file=filepath,mimetype=mime_type,as_attachment=False)

# delete file
@app.route('/files/delete/<int:file_id>')
def deleteFile(file_id):
    if 'userid' not in session:
        return redirect(url_for('login'))
    userid = session.get('userid')
    
    status, msg = deleteFileByFileid(
        fileid=file_id,
        userid=userid
    )
    if status:
        flash(msg,"msg")
        return redirect(url_for('files'))
    else:
        flash(msg,"err")

    flash("File not found!", "err")
    return redirect(url_for('files'))

# notes route
@app.route('/notes')
def notes():
    if 'userid' not in session:
        return redirect(url_for('login'))
    userid = session.get('userid')
    if request.method == "GET":
        # get notes by userid
        title = request.args.get('search')

        userid = session.get('userid')
        notes = getNotesByUserid(userid=userid,title=title)
        print(notes)
        return render_template('notes.html',notes = notes[1])

@app.route('/notes/<int:notes_id>')
def noteByID(notes_id):
    if 'userid' not in session:
        return redirect(url_for('login'))

    userid = session.get('userid')

    status, note = getNotesByNotesid(
        notesid=notes_id,
        userid=userid
    )

    if status and note:
        return render_template(
            'detailed_note.html',
            note=note
        )

    flash("Note not found!", "err")
    return redirect(url_for('notes'))

@app.route('/notes/edit')
def editNotes(notes_id):
    if 'userid' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        status,notes = getNotesByNotesid(notesid=notes_id)
        return render_template('edit-notes.html')


@app.route('/notes/delete/<int:notes_id>')
def deleteNotes(notes_id):
    if 'userid' not in session:
        return redirect(url_for('login'))
    userid = session.get('userid')
    
    status, msg = deleteNotesByNotesid(
        notesid=notes_id,
        userid=userid
    )
    if status:
        flash(msg,"msg")
        return redirect(url_for('notes'))
    else:
        flash(msg,"err")

    flash("Note not found!", "err")
    return redirect(url_for('notes'))


# dashboard route
@app.route("/dashboard")
def dashboard():
    if "userid" not in session:
        return redirect(url_for('login'))
    userid = session.get('userid')
    files_count,notes_count = totalFilesAndNotes(userid=userid)
    status, recent_notes = recentNotes(userid=userid)
    if status == False:
        recent_notes = []
    return render_template('dashboard.html',username = session.get('username'),notes_count=notes_count,files_count=files_count,recent_notes=recent_notes)

# profile route
@app.route('/profile')
def profile():
    return "P R O F I L E  P A G E"

# logout route
@app.route('/logout')
def logout():
    return 'LOG OUT PAGE'


@app.route('/add-notes',methods = ['GET','POST'])
def addNotes():
    if request.method == 'GET':
        return render_template('add-notes.html')
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        # store notes in table
        status,msg = insertNotesRecord(userid=session.get('userid'),title=title,content=body)
        # redirect to notes dashboard
        if status == True:
            flash(msg,"msg")
            return redirect(url_for('notes'))
        else:
            flash(msg, "err")
            return redirect(url_for('notes'))
# main
if __name__ == "__main__":
    print(CreateTables())
    app.run(debug=True,port=8000)