
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.secret_key = 'studentmanagementsecret'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ka@960491'
app.config['MYSQL_DB'] = 'student_management'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        cursor = mysql.connection.cursor()

        cursor.execute(
            "INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,%s)",
            (name, email, password, role)
        )

        mysql.connection.commit()
        cursor.close()

        flash("Registration Successful")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))

        else:
            flash("Invalid Email or Password")

    return render_template('login.html')


@app.route('/admin_dashboard')
def admin_dashboard():

    if 'loggedin' in session and session['role'] == 'admin':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

        total_students = len(students)

        return render_template(
            'admin_dashboard.html',
            students=students,
            total_students=total_students
        )

    return redirect(url_for('login'))

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        marks = request.form['marks']
        attendance = request.form['attendance']

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO students(name,email,course,marks,attendance)
            VALUES(%s,%s,%s,%s,%s)
        """, (name, email, course, marks, attendance))

        mysql.connection.commit()
        cursor.close()

        flash("Student Added Successfully")
        return redirect(url_for('admin_dashboard'))

    return render_template('add_student.html')


@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        marks = request.form['marks']
        attendance = request.form['attendance']

        cursor.execute("""
            UPDATE students
            SET name=%s,email=%s,course=%s,marks=%s,attendance=%s
            WHERE id=%s
        """, (name, email, course, marks, attendance, id))

        mysql.connection.commit()

        flash("Student Updated Successfully")
        return redirect(url_for('admin_dashboard'))

    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()

    return render_template('edit_student.html', student=student)


@app.route('/delete_student/<int:id>')
def delete_student(id):

    cursor = mysql.connection.cursor()

    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    mysql.connection.commit()

    flash("Student Deleted Successfully")

    return redirect(url_for('admin_dashboard'))

@app.route('/student_dashboard')
def student_dashboard():

    if 'loggedin' in session and session['role'] == 'student':

        student_id = session['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT * FROM students WHERE id=%s", (student_id,))
        student = cursor.fetchone()

        return render_template('student_dashboard.html', student=student)

    return redirect(url_for('login'))


@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)