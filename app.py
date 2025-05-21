from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Bắt buộc để dùng session và flash

def connect_to_database():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Thanh2004',
        database='qlyphongkham'
    )

# ------------------ LẤY DỮ LIỆU --------------------

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

# Lấy danh sách thuốc
def get_medicines():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM thuoc")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return medicines

# Lấy danh sách lịch khám (lịch hẹn)
def get_appointments():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT lh.id, bn.ho_ten AS ten_benh_nhan, bs.ho_ten AS ten_bac_si, lh.thoi_gian_hen, lh.tinh_trang, lh.trieu_chung
        FROM lichhen lh
        JOIN benhnhan bn ON lh.id_benh_nhan = bn.id
        JOIN bacsi bs ON lh.id_bac_si = bs.id
        ORDER BY lh.thoi_gian_hen DESC
    """)
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return appointments
# ------------------ ROUTES --------------------

@app.route('/')
def index():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/doctor')
def doctor():
    if 'admin' not in session:
        return redirect(url_for('login'))
    doctors = get_doctors()
    return render_template('doctor.html', doctors=doctors)
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
        return redirect(url_for('doctor'))
    return render_template('add_doctor.html')


@app.route('/edit-doctor/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        ho_ten = request.form['ho_ten']
        chuyen_khoa = request.form['chuyen_khoa']
        so_dien_thoai = request.form['so_dien_thoai']
        cursor.execute("UPDATE bacsi SET ho_ten=%s, chuyen_khoa=%s, so_dien_thoai=%s WHERE id=%s",
                       (ho_ten, chuyen_khoa, so_dien_thoai, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('doctor'))
    cursor.execute("SELECT * FROM bacsi WHERE id=%s", (id,))
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_doctor.html', doctor=doctor)

@app.route('/delete-doctor/<int:id>')
def delete_doctor(id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bacsi WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('doctor'))

@app.route('/patient')
def patient():
    if 'admin' not in session:
        return redirect(url_for('login'))
    patients = get_patients()
    return render_template('patient.html', patients=patients)

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
        return redirect(url_for('patient'))
    return render_template('add_patient.html')

@app.route('/edit-patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        ho_ten = request.form['ho_ten']
        ngay_sinh = request.form['ngay_sinh']
        gioi_tinh = request.form['gioi_tinh']
        so_dien_thoai = request.form['so_dien_thoai']
        dia_chi = request.form['dia_chi']
        cursor.execute("""
            UPDATE benhnhan 
            SET ho_ten=%s, ngay_sinh=%s, gioi_tinh=%s, so_dien_thoai=%s, dia_chi=%s 
            WHERE id=%s
        """, (ho_ten, ngay_sinh, gioi_tinh, so_dien_thoai, dia_chi, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('patient'))
    cursor.execute("SELECT * FROM benhnhan WHERE id=%s", (id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_patient.html', patient=patient)

@app.route('/delete-patient/<int:id>')
def delete_patient(id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM benhnhan WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('patient'))

@app.route('/medicine')
def medicine():
    if 'admin' not in session:
        return redirect(url_for('login'))
    medicines = get_medicines()
    return render_template('medicine.html', medicines=medicines)

@app.route('/appointment')
def appointment():
    if 'admin' not in session:
        return redirect(url_for('login'))
    appointments = get_appointments()
    return render_template('appointment.html', appointments=appointments)

# ------------------ ĐĂNG NHẬP --------------------

def check_admin(username, password):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()
    return admin

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = check_admin(username, password)
        if admin:
            session['admin'] = admin['username']
            return redirect(url_for('index'))
        else:
            flash('Đăng nhập thất bại. Kiểm tra lại thông tin.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
