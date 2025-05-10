from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Kết nối đến MySQL
def connect_to_database():
    return mysql.connector.connect(
        host='localhost',        # Máy chủ MySQL
        user='root',             # Tên người dùng MySQL
        password='Thanh2004Thanh2004',# Mật khẩu MySQL
        database='qlyphongkham'  # Tên cơ sở dữ liệu
    )

# Lấy danh sách bác sĩ từ MySQL
def get_doctors():
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bacsi")
    doctors = cursor.fetchall()
    cursor.close()
    connection.close()
    return doctors

# Lấy danh sách bệnh nhân từ MySQL
def get_patients():
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM benhnhan")
    patients = cursor.fetchall()
    cursor.close()
    connection.close()
    return patients

# Trang chủ - Hiển thị bác sĩ và bệnh nhân
@app.route('/')
def index():
    doctors = get_doctors()
    patients = get_patients()
    return render_template('index.html', doctors=doctors, patients=patients)

if __name__ == '__main__':
    app.run(debug=True)
