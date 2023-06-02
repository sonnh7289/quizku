import mysql.connector
import smtplib
import hashlib
import requests 
import threading
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from getpass import getpass
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

config = {
    'user': 'root',
    'password': 'S@1989',
    'host': 'localhost',
    'port': 3306,
    'database': 'fakelocation'
}


app = Flask(__name__)

@app.route('/sigup', methods=['POST'])
def register_user(email, password):
    cred = firebase_admin.credentials.Certificate('fir-sigup-b773e-firebase-adminsdk-anunx-f6abbb59a1.json')
    firebase_admin.initialize_app(cred)
    try:
        user = auth.create_user(
            email=email,
            password=password,
            email_verified=False
        )
        send_verification_email(email)
        return user
    except firebase_admin.auth.EmailAlreadyExistsError:
        print("Địa chỉ email đã tồn tại.")
        return None
    except Exception as e:
        print("Lỗi: ", e)
        return None

# Gửi email xác minh
def send_verification_email(email):
    #day la gmail mac dinh de gui den tat ca gmail khac va can phai bat xac thuc 2 yeu to
    from_address = "devmobilepro1888@gmail.com" 
    password = "zibzvfmidbmufdso"  

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = email
    msg['Subject'] = "Xác minh địa chỉ email"

    body = """
    Xin chào,

    Cảm ơn bạn đã đăng ký tài khoản. Vui lòng xác minh địa chỉ email của bạn bằng cách nhấp vào liên kết sau:
    <a href="https://yourwebsite.com/verify_email?email={0}">Xác minh email</a>

    Trân trọng,
    Đội ngũ quản trị
    """

    msg.attach(MIMEText(body.format(email), 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_address, password)
        server.sendmail(from_address, email, msg.as_string())

    email = input("Please enter your Email: ")
    password = getpass("Enter your password: ")
    user = register_user(email, password)
    if user:
        print("Tài khoản đã được đăng ký thành công.")

def save_user_to_mysql(email):
    connection= mysql.connector.connect(**config)
    cursor = connection.cursor()
    insert_user_query = "INSERT INTO user (email) VALUES (%s)"
    cursor = connection.cursor()
    cursor.execute(insert_user_query, (email,))
    connection.commit()
    firebase_admin.delete_app(firebase_admin.get_app())
    email = "example@example.com"
    password = "password123"
    new_user = register_user(email, password)
    print("Tài khoản mới đã được tạo:", new_user.uid)

@app.route('/reset', methods=['POST'])
def reset_password():
    username = request.form.get('username')

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "SELECT email FROM user WHERE username = %s"
    values = (username,)
    
    cursor.execute(query, values)
    result = cursor.fetchone()

    if result is not None:
        email = result[0]

        new_password = "new_password"

        update_query = "UPDATE users SET password = %s WHERE username = %s"
        update_values = (new_password, username)
        cursor.execute(update_query, update_values)
        connection.commit()

        send_email(email, new_password)

        print('Đã reset mật khẩu thành công và gửi email!')
    else:
        print('Không tìm thấy người dùng có tên đăng nhập', username)

    cursor.close()
    connection.close()

def send_email(email, new_password):
    smtp_host = 'your_smtp_host'  
    smtp_port = 587  
    smtp_username = 'your_email_username' 
    smtp_password = 'your_email_password' 

    sender = 'your_email_address' 
    receiver = email

    subject = 'Reset mật khẩu'
    body = f'Mật khẩu mới của bạn là: {new_password}'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

@app.route('/upload', methods=['POST'])
def upload_image_to_imgbb():
    image_path = request.form.get('image_path')

    url = 'https://imgbb.com/1/upload'
    api_key = '4cd53e2de49573f195e1b8b9c8d5d035' # thay doi api_key

    with open(image_path, 'rb') as file:
        payload = {
            'key': api_key,
            'image': file.read()
        }
        response = requests.post(url, payload)
        json_data = response.json()
        
        if json_data['status'] == 200:
            image_url = json_data['data']['url']
            return image_url
        else:
            return None

def save_image_comment(image_url, noidung_comment):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    insert_query = "INSERT INTO comment_image (url, noidung_comment) VALUES (%s, %s)"
    insert_values = (image_url, noidung_comment)
    cursor.execute(insert_query, insert_values)

    connection.commit()

    cursor.close()
    connection.close()

@app.route('/comments', methods=['POST'])
def get_comments():
    image_id = request.form.get('image_id')

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = "SELECT * FROM fakelocation_image WHERE id_image = %s"
    values = (image_id,)
    cursor.execute(sql, values)
    results = cursor.fetchall()

    for comment in results:
        comment_id = comment[0]
        comment_text = comment[1]
        comment_date = comment[2]
        print(f"Comment ID: {comment_id}")
        print(f"Comment Text: {comment_text}")
        print(f"Comment Date: {comment_date}")
        print()

@app.route('/1000comments', methods=['POST'])
def get_1000comments():
    image_id = 1  
    sql = "SELECT * FROM fakelocation_image WHERE image_id = %s ORDER BY comment_date DESC LIMIT 1000"
    connection= mysql.connector.connect(**config)
    cursor = connection.cursor()

    cursor.execute(sql, (image_id,))

    results = cursor.fetchall()
    for row in results:
        comment_id = row[0]
        comment_text = row[1]
        comment_date = row[2]
    
        print(f"Comment ID: {comment_id}")
        print(f"Comment Text: {comment_text}")
        print(f"Comment Date: {comment_date}")
        print()
@app.route('/postcomments', methods=['POST'])
def post_comments():
    connection= mysql.connector.connect(**config)
    cursor = connection.cursor()
    comment = "This is a sample comment."
    timestamp = datetime.now()
    insert_comment_query = "INSERT INTO comment_image (noidung_comment, timestamp) VALUES (%s, %s)"
    cursor.execute(insert_comment_query, (comment, timestamp))
    connection.commit()
    cursor.close()
    connection.close()
@app.route('/image_links', methods=['POST'])
def post_image():
    connection= mysql.connector.connect(**config)
    cursor = connection.cursor()
    image_link = "https://example.com/image.jpg"
    insert_image_query = "INSERT INTO fakelocation_image (image_link) VALUES (%s)"
    cursor.execute(insert_image_query, (image_link,))
    connection.commit()
    cursor.close()
    connection.close()
if __name__ == '__main__':
    app.run()
