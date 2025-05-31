from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps
from flask import abort

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Bắt buộc để dùng session và flash

def connect_to_database():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Thanh2004',
        database='qlyphongkham'
    )

# Decorator kiểm tra quyền admin

def yeu_cau_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'vai_tro' not in session or session['vai_tro'] != 'admin':
            flash("Bạn không có quyền truy cập!", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
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

def get_medicines():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM thuoc")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return medicines

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
def home():
    # Trang giới thiệu công khai
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/dashboard/benh-nhan')
def dashboard_benh_nhan():
    if 'user_id' not in session or session.get('vai_tro') != 'benh_nhan':
        return redirect(url_for('loginuser'))

    benh_nhan_id = session['user_id']
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    # Lấy lịch hẹn
    cursor.execute("""
        SELECT lh.thoi_gian_hen, lh.tinh_trang, lh.trieu_chung, bs.ho_ten AS ten_bac_si
        FROM LichHen lh
        JOIN BacSi bs ON lh.id_bac_si = bs.id
        WHERE lh.id_benh_nhan = %s
        ORDER BY lh.thoi_gian_hen DESC
    """, (benh_nhan_id,))
    lich_hen = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('dashboard_benh_nhan.html', lich_hen=lich_hen)

@app.route('/dashboard/benh-nhan/dat-lich', methods=['GET', 'POST'])
def dat_lich_kham():
    if 'user_id' not in session or session.get('vai_tro') != 'benh_nhan':
        return redirect(url_for('loginuser'))

    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        id_benh_nhan = session['user_id']
        id_bac_si = request.form['id_bac_si']
        thoi_gian_hen = request.form['thoi_gian_hen']
        trieu_chung = request.form['trieu_chung']

        cursor.execute("""
            INSERT INTO LichHen (id_benh_nhan, id_bac_si, thoi_gian_hen, tinh_trang, trieu_chung)
            VALUES (%s, %s, %s, 'cho_duyet', %s)
        """, (id_benh_nhan, id_bac_si, thoi_gian_hen, trieu_chung))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard_benh_nhan'))  # chuyển về xem lịch hẹn

    # GET method: lấy danh sách bác sĩ
    cursor.execute("SELECT id, ho_ten FROM BacSi")
    bac_si_list = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('lichkham_benhnhan.html', bac_si_list=bac_si_list)



@app.route('/doctor')
def doctor():
    if 'admin' not in session:
        return redirect(url_for('login'))
    doctors = get_doctors()
    return render_template('doctor.html', doctors=doctors)

@app.route('/add-doctor', methods=['GET', 'POST'])

def add_doctor():
    if 'admin' not in session:
        return redirect(url_for('login'))
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
    if 'admin' not in session:
        return redirect(url_for('login'))
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
    if 'admin' not in session:
        return redirect(url_for('login'))
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
    if 'admin' not in session:
        return redirect(url_for('login'))
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
    if 'admin' not in session:
        return redirect(url_for('login'))
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
    if 'admin' not in session:
        return redirect(url_for('login'))
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

@app.route('/add-medicine', methods=['GET', 'POST'])

def add_medicine():
    if request.method == 'POST':
        ten_thuoc = request.form['ten_thuoc']
        don_vi = request.form['don_vi']
        gia_ban = request.form['gia']
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO thuoc (ten_thuoc, don_vi, gia) VALUES (%s, %s, %s)",
            (ten_thuoc, don_vi, gia_ban)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('medicine'))
    return render_template('add_medicine.html')


@app.route('/edit-medicine/<int:id>', methods=['GET', 'POST'])

def edit_medicine(id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        ten_thuoc = request.form['ten_thuoc']
        don_vi = request.form['don_vi']
        gia = request.form['gia']
        cursor.execute("UPDATE thuoc SET ten_thuoc=%s, don_vi=%s, gia=%s WHERE id=%s",
                       (ten_thuoc, don_vi, gia, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('medicine'))
    cursor.execute("SELECT * FROM thuoc WHERE id=%s", (id,))
    medicine = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_medicine.html', medicine=medicine)


@app.route('/appointment')
def appointment():
    if 'admin' not in session:
        return redirect(url_for('login'))
    appointments = get_appointments()
    return render_template('appointment.html', appointments=appointments)

@app.route('/add-appointment', methods=['GET', 'POST'])

def add_appointment():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id_benh_nhan = request.form['id_benh_nhan']
        id_bac_si = request.form['id_bac_si']
        thoi_gian_hen = request.form['thoi_gian_hen']
        tinh_trang = request.form['tinh_trang']
        trieu_chung = request.form['trieu_chung']
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lichhen (id_benh_nhan, id_bac_si, thoi_gian_hen, tinh_trang, trieu_chung) VALUES (%s, %s, %s, %s, %s)",
            (id_benh_nhan, id_bac_si, thoi_gian_hen, tinh_trang, trieu_chung)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('appointment'))

    patients = get_patients()
    doctors = get_doctors()
    return render_template('add_appointment.html', patients=patients, doctors=doctors)

@app.route('/edit-appointment/<int:id>', methods=['GET', 'POST'])

def edit_appointment(id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        trieu_chung = request.form['trieu_chung']
        thoi_gian_hen = request.form['thoi_gian_hen']
        tinh_trang = request.form['tinh_trang']
        cursor.execute("""
            UPDATE lichhen
            SET trieu_chung=%s, thoi_gian_hen=%s, tinh_trang=%s
            WHERE id=%s
        """, (trieu_chung, thoi_gian_hen, tinh_trang, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('appointment'))
    cursor.execute("SELECT * FROM lichhen WHERE id=%s", (id,))
    appointment = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_appointment.html', appointment=appointment)


# ---------- LẤY DANH SÁCH NGƯỜI DÙNG ----------
def get_users():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM NguoiDung")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

# ---------- ROUTE DANH SÁCH NGƯỜI DÙNG ----------
@app.route('/users')
def users():
    if 'admin' not in session:
        return redirect(url_for('login'))
    users = get_users()
    return render_template('users.html', users=users)

@app.route('/loginuser', methods=['GET', 'POST'])
def loginuser():
    if request.method == 'POST':
        ten_dang_nhap = request.form['ten_dang_nhap']
        mat_khau = request.form['mat_khau']

        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM NguoiDung WHERE ten_dang_nhap = %s", (ten_dang_nhap,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and mat_khau == user['mat_khau']:  # (Nên dùng hash trong thực tế)
            session['user_id'] = user['id']
            session['vai_tro'] = user['vai_tro']
            session['ten_dang_nhap'] = user['ten_dang_nhap']
            
            if user['vai_tro'] == 'admin':
                return redirect(url_for('dashboard'))
            elif user['vai_tro'] == 'bac_si':
                return redirect(url_for('dashboard_bac_si'))  # hoặc route tương ứng
            else:
                return redirect(url_for('dashboard_benh_nhan'))  # hoặc route tương ứng
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!", "error")

    return render_template('loginuser.html')

@app.route('/logoutuser')
def logoutuser():
    session.clear()  # Xóa toàn bộ thông tin đăng nhập trong session
    return redirect(url_for('loginuser'))  # Chuyển về trang đăng nhập


# ---------- THÊM NGƯỜI DÙNG ----------


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        ten_dang_nhap = request.form['ten_dang_nhap']
        mat_khau = request.form['mat_khau']
        vai_tro = request.form['vai_tro']
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NguoiDung (ten_dang_nhap, mat_khau, vai_tro)
            VALUES (%s, %s, %s)
        """, (ten_dang_nhap, mat_khau, vai_tro))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('users'))
    return render_template('add_user.html')

# ---------- SỬA NGƯỜI DÙNG ----------
@app.route('/edit-user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        ten_dang_nhap = request.form['ten_dang_nhap']
        mat_khau = request.form['mat_khau']
        vai_tro = request.form['vai_tro']
        cursor.execute("""
            UPDATE NguoiDung SET ten_dang_nhap=%s, mat_khau=%s, vai_tro=%s WHERE id=%s
        """, (ten_dang_nhap, mat_khau, vai_tro, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('users'))

    cursor.execute("SELECT * FROM NguoiDung WHERE id=%s", (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_user.html', user=user)

# ---------- XÓA NGƯỜI DÙNG ----------
@app.route('/delete-user/<int:id>')
def delete_user(id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM NguoiDung WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('users'))


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
            return redirect(url_for('dashboard'))
        else:
            flash('Đăng nhập thất bại. Kiểm tra lại thông tin.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)