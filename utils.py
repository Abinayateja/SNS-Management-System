import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSKEY = os.getenv('SENDER_PASSKEY')
SMTP_SERVER = os.getenv('SMTP_SERVER')
PORT = int(os.getenv('SMTP_PORT'))
print(SENDER_EMAIL)
print(SENDER_PASSKEY)
def sendEmail(to_email,subject,body):
    msg = MIMEMultipart()

    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'plain'))
    print(1)
    try:
        server = smtplib.SMTP(SMTP_SERVER,PORT)
        print(2)
        server.starttls() # start server
        server.login(SENDER_EMAIL,SENDER_PASSKEY)
        print(3)
        server.sendmail(SENDER_EMAIL,to_email,msg.as_string())
        print(4)
        server.quit()
        return True, "Email Sent"
    except Exception as e:
        return False, f"Something wrong in email sending:{e}"

def generateHashPassword(password):
    hash_password = bcrypt.hashpw(password=password.encode('utf-8'),
                                  salt=bcrypt.gensalt(4))
    return hash_password

# verify hash password
def verifyHashPassword(user_pasword:str,hash_password:str):
    status = bcrypt.checkpw(user_pasword.encode('utf-8'),hash_password.encode('utf-8'))
    return status
    