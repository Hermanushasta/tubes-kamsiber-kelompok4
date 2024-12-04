from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
import re
from markupsafe import escape

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    

    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()

    #kode sebelumnya (masih menggunakan interpolasi string)
    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)
    
    # kode perbaikan (parameterized quiries)
    # Menambahkan placeholder "?" sebagai parameterized quiries dalam SQLite
    # Memberikan tuple di method "execute" pada parameter (name, age, grade))
    query = "INSERT INTO student (name, age, grade) VALUES (?, ?, ?)"
    cursor.execute(query, (name, age, grade))
    
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>') 
def delete_student(id):
    # RAW Query
    # kode sebelumnya (masih menggunakan interpolasi string)
    # db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    
    # perbaikan kode (parameterized queries)
    db.session.execute(
        text("DELETE FROM student WHERE id=:id"),
        {'id': id})
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # Validasi input
        if not name or not isinstance(name, str) or len(name) > 100 or not re.match(r'^[A-Za-z\s]+$', name):    
            return "Invalid name", 400
        
        if not age.isdigit() or int(age) < 1 or int(age) > 120:
            return "Invalid age", 400
        
        if not re.match(r'^[A-F][+-]?$|^[A]$', grade): 
            return "Invalid grade", 400

        # Escape input untuk HTML
        name = escape(name)
        grade = escape(grade)

        # RAW Query
        # kode sebelumnya (masih menggunakan interpolasi string)
        # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        
        # perbaikan kode (paramaterized queries)
        db.session.execute(
            text("UPDATE student SET name=:name, age=:age, grade=:grade WHERE id=:id"),
            {'name': name, 'age': age, 'grade': grade, 'id': id})
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        # kode sebelumnya (masih menggunakan interpolasi string)
        # student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        
        #perbaikan kode (parameterized queries)
        student = db.session.execute(
            text("SELECT * FROM student WHERE id=:id"),
            {'id': id}
        ).fetchone()

        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

