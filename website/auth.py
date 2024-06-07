import mysql.connector
from flask import Blueprint, request, redirect, url_for, render_template,jsonify, session, flash
import re
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',  # MySQL sunucunuzun adresi
        user='root',  # MySQL kullanıcı adı
        password='',  # MySQL şifresi
        database='classcheck'  # Kullanmak istediğiniz veritabanı
    )
    return conn


@auth.route('/login', methods=['POST'])
def login():
   
    email = request.form['email']
    password = request.form['password']
    
    # Veritabanından e-posta ve şifre kontrolü
    conn=get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teachers WHERE email=%s AND password=%s", (email, password))
    teacher = cursor.fetchone()

    if teacher:
        # Giriş başarılıysa ana sayfaya yönlendir
        return redirect(url_for('views.teacher_login'))
    else:
        # Giriş başarısızsa hata mesajıyla birlikte login sayfasına yönlendir
        return render_template('login.html', invalid_login=True, invalid_email=True, invalid_password=True)
    

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        teacher_id=request.form['teacher_id']
        teacher_name = request.form['teacher_name']
        teacher_surname = request.form['teacher_surname']
        email = request.form['email']
        password = request.form['password']
        
        # Veritabanına ekleme
        conn = get_db_connection()
        cursor = conn.cursor()

        # Kullanıcının zaten var olup olmadığını kontrol et
        cursor.execute("SELECT * FROM teachers WHERE email=%s", (email,))
        existing_teacher = cursor.fetchone()
        
        if existing_teacher:
            flash('User already exists!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('views.signup'))
        
        cursor.execute("INSERT INTO teachers (teacher_id,teacher_name,teacher_surname,email, password) VALUES (%s,%s,%s,%s, %s)", (teacher_id,teacher_name,teacher_surname,email, password))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('User successfully registered!', 'success')
        return redirect(url_for('views.login'))
    
    return render_template('signup.html')

@auth.route('/add_teacher', methods=['POST'])
def add_teacher():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        teacher_name = request.form['teacher_name']
        teacher_surname = request.form['teacher_surname']
        email = request.form['email']
        password = request.form['password']
        
        # Veritabanına ekleme
        conn = get_db_connection()
        cursor = conn.cursor()

        # Öğretmenin zaten var olup olmadığını kontrol et
        cursor.execute("SELECT * FROM teachers WHERE teacher_id=%s OR email=%s", (teacher_id, email))
        existing_teacher = cursor.fetchone()
        
        if existing_teacher:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Teacher already exists!'})

        cursor.execute("INSERT INTO teachers (teacher_id, teacher_name, teacher_surname, email, password) VALUES (%s, %s, %s, %s, %s)", (teacher_id, teacher_name, teacher_surname, email, password))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Teacher successfully added!'})

@auth.route('/add_course', methods=['POST'])
def add_course():
    if request.method == 'POST':
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        course_day = request.form['course_day']
        lesson_start_time= request.form['lesson_start_time']
        lesson_end_time= request.form['lesson_end_time']
        class_name = request.form['class_name']
        
        # Veritabanına ekleme
        conn = get_db_connection()
        cursor = conn.cursor()

        # Kursun zaten var olup olmadığını kontrol et
        cursor.execute("SELECT * FROM courses WHERE course_id=%s", (course_id,))
        existing_course = cursor.fetchone()
        
        if existing_course:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Course already exists!'})
    
        cursor.execute("INSERT INTO courses (course_id, course_name, course_day, lesson_start_time, lesson_end_time, class_name) VALUES (%s, %s, %s, %s, %s, %s)", (course_id, course_name, course_day, lesson_start_time, lesson_end_time, class_name))
        conn.commit()
        cursor.close()
        conn.close()
    
    return jsonify({'success': True, 'message': 'Course successfully added!'})
    
@auth.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        student_surname = request.form['student_surname']
        
        # Veritabanına ekleme
        conn = get_db_connection()
        cursor = conn.cursor()

        # Öğrencinin zaten var olup olmadığını kontrol et
        cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
        existing_student = cursor.fetchone()
        
        if existing_student:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Student already exists!'})

        cursor.execute("INSERT INTO students (student_id, student_name, student_surname) VALUES (%s, %s, %s)", (student_id, student_name, student_surname))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Student successfully added!'})

@auth.route('/filter_attendances', methods=['POST'])
def filter_attendances():
    course_id = request.form.get('course_id')
    attandancedate = request.form.get('attandancedate')
    
    query = "SELECT * FROM attandance WHERE 1=1"
    params = []

    if course_id:
        query += " AND courseid = %s"
        params.append(course_id)
    if attandancedate:
        query += " AND DATE(attandancedate) = %s"
        params.append(attandancedate)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    attendances = cursor.fetchall()
    cursor.close()
    conn.close()

    if attendances:
        return jsonify({'success': True, 'attendances': attendances})
    else:
        return jsonify({'success': False, 'message': 'No attendances found for the selected filters.'})

@auth.route('/teacher_login')
def get_students_info():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_name FROM students")
    students = cursor.fetchall()
    for i in students:
        print(i.student_name)
    cursor.close()
    conn.close()
    return render_template('teacher_login.html', students=students) 

    """ @auth.route('/login', methods=['GET', 'POST'])
def login():
    invalid_email = False
    invalid_password = False
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teachers WHERE email=?", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('login.html') """
    """ if user:
            if check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                return redirect(url_for('views.teacher_login'))
            else:
                invalid_password = True
        else:
            invalid_email = True """

    """ return render_template('login.html', invalid_email=invalid_email, invalid_password=invalid_password)

    return render_template('login.html', invalid_email=invalid_email, invalid_password=invalid_password) """

    """ def validate_password(password):
    if not (8 <= len(password) <= 16):
        return "Your password must be 8-16 characters, include at least one lowercase letter, one uppercase letter, and a number."
    if not re.search(r"[A-Z]", password):
        return "Your password must be 8-16 characters, include at least one lowercase letter, one uppercase letter, and a number."
    if not re.search(r"[a-z]", password):
        return "Your password must be 8-16 characters, include at least one lowercase letter, one uppercase letter, and a number."
    if not re.search(r"[0-9]", password):
        return "Your password must be 8-16 characters, include at least one lowercase letter, one uppercase letter, and a number."
    return None """

    """ @auth.route('/signup', methods=['GET', 'POST'])
    def signup():
    if request.method == 'POST':
        # POST isteği ile gelen verileri işleme kodları
        pass
    else:
        # GET isteği ile signup sayfasını render etme kodları
        return render_template('signup.html')
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']

    # Şifre validasyonu
    if not email.endswith('@aydin.edu.tr'):
        flash('Invalid email domain. Only @aydin.edu.tr emails are allowed.')
        return redirect(url_for('auth.signup_page'))

    password_error = validate_password(password)
    if password_error:
        flash(password_error)
        return redirect(url_for('auth.signup_page'))
    
    if password != confirmPassword:
        flash('Passwords do not match.')
        return redirect(url_for('auth.signup_page'))

    conn = get_db_connection()
    try:
        # Kullanıcı var mı kontrol et
        select_cursor = conn.cursor()
        select_cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_record = select_cursor.fetchone()
        select_cursor.close()

        if existing_record:
            return 'User already exists!'
        
        # Yeni kullanıcı ekle
        insert_cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        insert_cursor.execute(
            "INSERT INTO users (name, surname, email, password) VALUES (%s, %s, %s, %s)",
            (name, surname, email, hashed_password)
        )
        conn.commit()
        insert_cursor.close()
        
    except sqlite3.Error as e:
        return f"An error occurred: {e}"
    finally:
        conn.close() """

    """     # INSERT işlemi için yeni bir cursor oluşturuyoruz
    insert_cursor = conn.cursor()
    
    # INSERT sorgusunu çalıştırıyoruz
    insert_cursor.execute("INSERT INTO teacher (name, surname, email, password, confirmPassword) VALUES (%s, %s, %s, %s, %s)", (name, surname, email, password, confirmPassword))
    
    # İşlemi tamamla ve bağlantıyı kapat
    conn.commit()
    conn.close()
    
    return 'Sign up successful!' """


