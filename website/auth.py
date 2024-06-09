import mysql.connector
from flask import Blueprint, request, redirect, url_for, render_template, jsonify, session, flash
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
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers WHERE teacher_email=%s", (email,))
    teacher = cursor.fetchone()

    if teacher and check_password_hash(teacher['teacher_password'], password):
        session['teacher_id'] = teacher['teacher_id']
        return redirect(url_for('views.teacher_login'))
    else:
        return render_template('login.html', invalid_login=True)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        teacher_name = request.form['teacher_name']
        teacher_surname = request.form['teacher_surname']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM teachers WHERE teacher_email=%s", (email,))
        existing_teacher = cursor.fetchone()
        
        if existing_teacher:
            flash('User already exists!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('views.signup'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute("INSERT INTO teachers (teacher_id, teacher_name, teacher_surname, teacher_email, teacher_password) VALUES (%s, %s, %s, %s, %s)", 
                       (teacher_id, teacher_name, teacher_surname, email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('User successfully registered!', 'success')
        return redirect(url_for('views.login'))
    
    return render_template('signup.html')

@auth.route('/add_teacher', methods=['POST'])
def add_teacher():
    try:
        teacher_id = request.form['teacher_id']
        teacher_name = request.form['teacher_name']
        teacher_surname = request.form['teacher_surname']
        email = request.form['email']
        password = request.form['password']

        # Boş alan kontrolü
        if not teacher_id or not teacher_name or not teacher_surname or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required!'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM teachers WHERE teacher_id=%s OR teacher_email=%s", (teacher_id, email))
        existing_teacher = cursor.fetchone()

        if existing_teacher:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Teacher already exists!'})

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute("INSERT INTO teachers (teacher_id, teacher_name, teacher_surname, teacher_email, teacher_password) VALUES (%s, %s, %s, %s, %s)", 
                       (teacher_id, teacher_name, teacher_surname, email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Teacher successfully added!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@auth.route('/remove_teacher', methods=['POST'])
def remove_teacher():
    try:
        teacher_id = request.form['teacher_id']

        # Boş alan kontrolü
        if not teacher_id:
            return jsonify({'success': False, 'message': 'Teacher ID is required!'})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teachers WHERE teacher_id=%s", (teacher_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Teacher successfully removed!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@auth.route('/add_course', methods=['POST'])
def add_course():
    try:
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        course_day = request.form['course_day']
        lesson_start_time = request.form['lesson_start_time']
        lesson_end_time = request.form['lesson_end_time']
        class_name = request.form['class_name']

        # Boş alan kontrolü
        if not course_id or not course_name or not course_day or not lesson_start_time or not lesson_end_time or not class_name:
            return jsonify({'success': False, 'message': 'All fields are required!'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM courses WHERE course_id=%s", (course_id,))
        existing_course = cursor.fetchone()

        if existing_course:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Course already exists!'})

        cursor.execute("INSERT INTO courses (course_id, course_name, course_day, attendance_start_time, attendance_end_time, class_name) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (course_id, course_name, course_day, lesson_start_time, lesson_end_time, class_name))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Course successfully added!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@auth.route('/remove_course', methods=['POST'])
def remove_course():
    try:
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        course_day = request.form['course_day']

        # Boş alan kontrolü
        if not course_id or not course_name or not course_day:
            return jsonify({'success': False, 'message': 'All fields are required!'})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE course_id=%s AND course_name=%s AND course_day=%s", 
                       (course_id, course_name, course_day))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Course successfully removed!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@auth.route('/add_student', methods=['POST'])
def add_student():
    try:
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        student_surname = request.form['student_surname']

        # Boş alan kontrolü
        if not student_id or not student_name or not student_surname:
            return jsonify({'success': False, 'message': 'All fields are required!'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
        existing_student = cursor.fetchone()

        if (existing_student):
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Student already exists!'})

        cursor.execute("INSERT INTO students (student_id, student_name, student_surname) VALUES (%s, %s, %s)", 
                       (student_id, student_name, student_surname))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Student successfully added!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@auth.route('/remove_student', methods=['POST'])
def remove_student():
    try:
        student_id = request.form['student_id']

        # Boş alan kontrolü
        if not student_id:
            return jsonify({'success': False, 'message': 'Student ID is required!'})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Student successfully removed!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@auth.route('/filter_students', methods=['POST'])
def filter_students():
    course_id = request.form.get('course_id')
    course_day = request.form.get('course_day')
    lesson_start_time = request.form.get('lesson_start_time')
    class_name = request.form.get('class_name')
    
    query = """
        SELECT s.student_id, s.student_name, s.student_surname, a.attendance
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id
        WHERE a.course_id = %s AND a.course_day = %s AND a.lesson_start_time = %s AND a.class_name = %s
    """
    params = [course_id, course_day, lesson_start_time, class_name]
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('teacher_login.html', students=students)

@auth.route('/toggle_attendance/<int:student_id>', methods=['POST'])
def toggle_attendance(student_id):
    data = request.get_json()
    attendance = data.get('attendance')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE attendance SET attendance=%s WHERE student_id=%s", (attendance, student_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True})

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.login'))

@auth.route('/filter_attendances', methods=['POST'])
def filter_attendances():
    course_id = request.form['course_id']
    attendance_date = request.form['attendance_date']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT a.course_id, a.student_id, DATE_FORMAT(a.attendance_date, '%%d-%%m-%%Y') as formatted_date
        FROM attendance a
        WHERE a.course_id = %s AND DATE(a.attendance_date) = %s
    """
    cursor.execute(query, (course_id, attendance_date))
    attendances = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('authorize_attendances.html', attendances=attendances)
