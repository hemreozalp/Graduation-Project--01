from flask import Blueprint, render_template, request, jsonify
from .auth import get_db_connection

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template('base.html')

@views.route('/login')
def login():
    return render_template('login.html')

@views.route('/signup')
def signup():
    return render_template('signup.html')

@views.route('/authorized_login')
def authorized_login():
    return render_template('authorized_login.html')

@views.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        course_day = request.form.get('course_day')
        lesson_start_time = request.form.get('lesson_start_time')
        class_name = request.form.get('class_name')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT s.student_id, s.student_name, s.student_surname, a.attendance
            FROM students s
            LEFT JOIN attendance a ON s.student_id = a.student_id
            WHERE a.course_id = %s AND a.course_day = %s AND a.lesson_start_time = %s AND a.class_name = %s
        """
        cursor.execute(query, (course_id, course_day, lesson_start_time, class_name))
        students = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('teacher_login.html', students=students)
    return render_template('teacher_login.html')

@views.route('/add_teacher')
def add_teacher():
    return render_template('add_teacher.html')

@views.route('/add_course')
def add_course():
    return render_template('add_course.html')

@views.route('/add_student')
def add_student():
    return render_template('add_student.html')

@views.route('/attendances')
def attendances():
    return render_template('authorize_attendances.html')

@views.route('/filter_attendances', methods=['POST'])
def filter_attendances():
    course_id = request.form.get('course_id')
    attendance_date = request.form.get('attendance_date')

    conditions = []
    params = []

    if course_id:
        conditions.append("a.course_id = %s")
        params.append(course_id)
    if attendance_date:
        conditions.append("DATE(a.attendance_date) = %s")
        params.append(attendance_date)

    if not conditions:
        return jsonify([])  # Hiçbir koşul verilmezse boş sonuç döndür

    query = f"""
        SELECT a.course_id, a.student_id, a.attendance_date
        FROM attendance a
        WHERE {' AND '.join(conditions)}
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    attendances = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(attendances)