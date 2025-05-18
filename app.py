from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def connect_to_database():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Thanh2004',
        database='qlyphongkham'
    )

def get_doctors():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bacsi")
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return doctors

def get_patients():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM benhnhan")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return patients

@app.route('/')
def index():
    doctors = get_doctors()
    patients = get_patients()
    return render_template('index.html', doctors=doctors, patients=patients)

@app.route('/add-doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        ho_ten = request.form['ho_ten']
        chuyen_khoa = request.form['chuyen_khoa']
        so_dien_thoai = request.form['so_dien_thoai']
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bacsi (ho_ten, chuyen_khoa, so_dien_thoai) VALUES (%s, %s, %s)", (ho_ten, chuyen_khoa, so_dien_thoai))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_doctor.html')

@app.route('/add-patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        ho_ten = request.form['ho_ten']
        ngay_sinh = request.form['ngay_sinh']
        gioi_tinh = request.form['gioi_tinh']
        so_dien_thoai = request.form['so_dien_thoai']
        dia_chi = request.form['dia_chi']
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO benhnhan (ho_ten, ngay_sinh, gioi_tinh, so_dien_thoai, dia_chi) VALUES (%s, %s, %s, %s, %s)",
            (ho_ten, ngay_sinh, gioi_tinh, so_dien_thoai, dia_chi)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_patient.html')


if __name__ == '__main__':
    app.run(debug=True)
