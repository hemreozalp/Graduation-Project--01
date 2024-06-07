from flask import Blueprint,render_template

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

@views.route('/teacher_login')
def teacher_login():
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
    return render_template('attendances.html')

# Diğer görünüm fonksiyonları buraya eklenebilir