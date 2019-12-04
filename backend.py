from __future__ import print_function
import sys
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import flask_login as flask_login
from flask_login import login_required, current_user, LoginManager, login_user, logout_user, UserMixin
import flask_sqlalchemy as sqlalchemy
from sqlalchemy import func

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taDB.db'
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =  False

db = sqlalchemy.SQLAlchemy(app)
bcrypt = Bcrypt(app)
reason = ""

login_manager = LoginManager()
login_manager.login_view = 'render_login'
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True, nullable=False)
    isTeacher = db.Column(db.Boolean)
    userID = db.Column(db.Integer)
    pw = db.Column(db.String(30))
    name = db.Column(db.String(15))
    lastName = db.Column(db.String(20))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    major = db.Column(db.String(30), default='')
    gpa = db.Column(db.Float, default=-1)
    experience = db.Column(db.String)
    grad_date = db.Column(db.String)
       
class Classes(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    teacherID = db.Column(db.Integer)
    title = db.Column(db.String(50))

class Applications(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    classID = db.Column(db.String(20))
    studentID = db.Column(db.Integer)
    name = db.Column(db.String(15))
    lastName = db.Column(db.String(20))
    status = db.Column(db.Integer, default = 0)

baseURL = '/api/'

@app.route('/newaccount', methods=['POST'])
def newInstructor():
    global reason
    newAccData = get_info(request)
    ver = verify_new_student(newAccData)
    if ver[0] or ver[1]:
        res = ""
        if ver[0] and ver[1]:
            res = "email and ID"
        elif ver[1]:
            res = "email"
        else:
            res = "ID"
        reason = res
        return redirect(url_for('render_signup'))

    newAcc = User(isTeacher=newAccData["is_teacher"],
                   userID=newAccData["ID"],
                   pw=bcrypt.generate_password_hash(newAccData["password"]),
                   name=newAccData["name"],
                   lastName=newAccData["lastname"],
                   email=newAccData["email"],
                   phone=newAccData["phone"])
    db.session.add(newAcc)
    db.session.commit()
    logout_user()
    login_user(newAcc)
    return redirect(url_for('render_profile'))

@app.route('/create-course', methods=['POST'])
def create_course():
    course = request.form.get("create_course_input")
    exist = Classes.query.filter_by(title=course).first()
    if course == "":
        flash("Please give a name to the class!")
        return redirect(url_for('render_create_course'))
    elif exist is not None:
        flash("Course with this name already exists!")
        return redirect(url_for('render_create_course'))
    Class = Classes(teacherID = flask_login.current_user.userID, title=course)
    db.session.add(Class)
    db.session.commit()
    return redirect(url_for('render_display_courses'))

@app.route('/edit-account', methods=['POST'])
def edit_account_student():
    curr = User.query.filter_by(id=flask_login.current_user.id).first()
    curr = change_info(curr, request)
    db.session.commit()
    return redirect(url_for('render_profile'))

@app.route('/login', methods=['POST'])
def log_in_user(email=None, password=None):
    email = request.form.get('email') if email is None else email
    password = request.form.get('password') if password is None else password
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    if user is not None and bcrypt.check_password_hash(user.pw, password):
        login_user(user, remember=remember)
        return redirect(url_for('render_profile'))
    flash("Please check your email and password and try again!")
    return redirect(url_for('render_login'))

def row_to_obj_user(row):
    obj = {
          "id": row.id,
          "isTeacher": row.isTeacher,
          "userID": row.userID,
          "name": row.name,
          "lastName": row.lastName,
          "email": row.email,
          "phone": row.phone,
          "gpa": row.gpa,
          "experience": row.experience,
          "major" : row.major,
          "grad_date" : row.grad_date
          }
    return obj

def row_to_obj_class(row):
    obj = {
          "id": row.id,
          "teacherID": row.teacherID,
          "title": row.title
          }
    return obj
    
def row_to_obj_applications(rows):
    obj = {
          "classID": rows[0].classID,
          "applications": {}
          }
    for row in rows:
        obj["applications"].row.id = row.studentID
    return obj

def get_info(req) -> dict:
    ret = {}
    ret["email"] = req.form.get('email_input')
    ret["password"] = req.form.get('password_input')
    ret["ID"] = req.form.get('wsuID_input')
    ret["name"] = req.form.get('firstname_input')
    ret["lastname"] = req.form.get('lastname_input')
    ret["phone"] = req.form.get('phone_input')
    ret["is_teacher"] = True if req.form.get('account') == "Instructor" else False
    return ret

def change_info(user, req):
    name = req.form.get("edit_name_input").split()
    if len(name) == 1:
        name.append("")
    elif len(name) == 0:
        name = ["", ""]
    user.name = name[0] if name[0] != "" else user.name
    user.lastName = name[1] if name[1] != "" else user.lastName
    user.phone = req.form.get('edit_phone_input') if req.form.get('edit_phone_input') != "" else user.lastName
    if not user.isTeacher:
        user.major = req.form.get('edit_major_input') if req.form.get('edit_major_input') != "" else user.lastName
        user.gpa = req.form.get('edit_gpa_input') if req.form.get('edit_gpa_input') != "" else user.lastName
        user.grad_date = req.form.get('edit_graduation_date_input') if req.form.get('edit_graduation_date_input') != "" else user.grad_date
        user.experience = req.form.get('edit_experience_input') if req.form.get('edit_experience_input') != "" else user.lastName
        if req.form.get("edit_add_TA_app") != None:
            
            newApp = Applications(
                   studentID=user.userID,
                   name=user.name,
                   lastName=user.lastName,
                   classID=req.form.get("edit_add_TA_app"))
            db.session.add(newApp)
            db.session.commit()
    
            
        li = req.form.getlist("checked_box")

        for i in li:
            removeApp = Applications.query.filter_by(id=i).first()
            db.session.delete(removeApp)
            #print(i)

        db.session.commit()

    return user

def verify_new_student(student:dict) -> tuple:
    '''
    Function to verify if user already exists in DB.\n
    paramenters: student as dict\n
    returns: if account exists as tuple
    '''
    resp = [False, False]
    resp[0] = db.session.query(User).filter(User.userID==student["ID"]).scalar()
    resp[1] = db.session.query(User).filter(User.email==student["email"]).scalar()
    return resp

@app.route('/viewprofile')
@login_required
def render_profile():
    data = {}
    if flask_login.current_user is None:
        data = {"id": "", "isTeacher": "", "userID": "", "name": "name", "lastName": "", "email": "", "phone": "", "gpa": "", "experience": ""}
    else:
        data = row_to_obj_user(flask_login.current_user)
    courses = db.session.query(Applications).filter_by(studentID=current_user.userID)

    return render_template('viewprofile.html', **data, data2 = courses.all())
    
@app.route('/view_profile_select/<studentID>')
@login_required
def render_profile_select(studentID):
    print(studentID)
    student = User.query.filter_by(userID = studentID).first()
    data = row_to_obj_user(student)
    return render_template('viewprofile.html', **data)

@app.route('/create_course')
@login_required
def render_create_course():
    if not check_access():
        return redirect(url_for('render_profile'))
    return render_template('create_course.html')


@app.route('/edit_profile')
@login_required
def render_edit_profile():
    global reason
    names = db.session.query(Classes)
    res = []
    for i in names:
        applied = Applications.query.filter_by(classID=i.title, studentID=current_user.userID).first()
        if applied == None:
            res.append(i)

    courses = db.session.query(Applications).filter_by(studentID=current_user.userID, status=0)

    return render_template('editprofile.html', data = res, data2 = courses.all())



@app.route('/login', methods=['GET'])
def render_login():
    if current_user.is_authenticated:
        return render_profile()
    return render_template('login.html')

@app.route('/signup')
def render_signup():
    global reason
    data = {}
    if current_user.is_authenticated:
        return redirect(url_for('render_profile'))
    if reason == "":
        data = {"reason": ""}
    else:
        data["reason"] = "Account with this "  + reason + " already exists!"
        reason = ""
    return render_template('create_account.html', **data)

@app.route('/display_courses',  methods=['GET'])
def render_display_courses():
    names = db.session.query(Classes)
    return render_template('display_courses.html', data = names.all())

@app.route('/')
def render_index():
    return render_template('login.html')

@login_manager.user_loader
def get_user(ident):
  return User.query.get(int(ident))

@app.route('/TA_application')
@login_required
def render_TA_application(students = []):
    if not check_access():
        return redirect(url_for('render_profile'))
    courses = db.session.query(Classes)
    return render_template('TA_application.html', data = courses.all(), students = students)


@app.route('/TA_application', methods=['GET','POST'])
@login_required
def list_students():
    if not check_access():
        return redirect(url_for('render_profile'))
    course = request.form.get('class_title')
    students = Applications.query.filter_by(classID = course, status=0)

    return render_TA_application(students.all())


@app.route('/TA_application_status', methods=['GET','POST'])
@login_required
def student_accept_reject():
    if not check_access():
        return redirect(url_for('render_profile'))
    SID = request.form.get('SID')
    CID = request.form.get('CID')
 

    if request.form.get('Accept') == 'Accept':
        Application = Applications.query.filter_by(classID=CID, studentID=SID).first()
        Application.status = 1

    elif request.form.get('Reject') == 'Reject':
        Application = Applications.query.filter_by(classID=CID, studentID=SID).first()
        Application.status = -1
    
    db.session.commit()

    return render_TA_application()


@app.route('/logout')
@login_required
def render_logout():
    logout_user()
    return redirect(url_for('render_login'))

def check_access():
    return current_user.isTeacher

'''
@app.route('/<string:page_name>/')
def render_static(page_name):
    if page_name == "viewprofile":
        return render_profile()
    return render_template('%s.html' % page_name)
'''


def main():
    if sys.version_info < (3,7,2):
        print("Sorry, this requires python >= 3.7.2!")
        exit()

    db.create_all()
    app.run()
    
if __name__ == '__main__':
    app.debug = True
    main()