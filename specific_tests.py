import unittest
import os
from backend import *

TEST_DB = 'test.db'
db = sqlalchemy.SQLAlchemy(app)

class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testDB.db'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

        # Disable sending emails during unit testing
        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        pass

    def verify_info(self, email, data:dict) -> list:
        # Verify that account is actually in DB
        ret = [False] * 6
        curr = User.query.filter_by(email=email).first()
        ret[0] = curr != None
        ret[1] = curr.email == data["email_input"]
        ret[2] = curr.name == data["firstname_input"]
        ret[3] = curr.lastName == data["lastname_input"]
        ret[4] = curr.phone == data["phone_input"]

        # Make sure password is encrypted
        ret[5] = bcrypt.check_password_hash(curr.pw, data["password_input"])
        return ret

    def test_login(self):
        '''
        Unit test where we try to login with the right credentials
        '''
        response = self.app.post("/login", data=dict(email="NewStudent@wsu.edu", password="gfgfhtr2123", remember=False))
        self.assertEqual(response.location, "http://localhost/viewprofile")

    def test_login2(self):
        '''
        Unit test where we try to login with the wrong credentials
        '''
        response = self.app.post("/login", data=dict(email="NewStudent@wsu.edu", password="gfg", remember=False))
        self.assertEqual(response.location, "http://localhost/login")

    def test_create_account_student(self):
        '''
        Unit Test that attempts to create existing student account
        '''

        data = {
                "email_input": "NewStudent@wsu.edu",
                "password_input": "gfgfhtr2123",
                "wsuID_input": "57384758743",
                "firstname_input": "Sam",
                "lastname_input": "Dam",
                "account": "Student",
                "phone_input": "243-521-5214"
                }
        response = self.app.post("/newaccount", data=data)
        self.assertEqual(response.location, "http://localhost/signup")

    def test_create_account_student2(self):
        '''
        Unit Test that attempts to create new student account
        '''

        data = {
                "email_input": "Test@wsu.edu",
                "password_input": "gfgfhtr2123",
                "wsuID_input": "2412343",
                "firstname_input": "Dam",
                "lastname_input": "Sam",
                "account": "Student",
                "phone_input": "243-521-5214"
                }
        response = self.app.post("/newaccount", data=data)
        self.assertEqual(response.location, "http://localhost/viewprofile")

        # Verify that account is actually in DB
        for i in self.verify_info("Test@wsu.edu", data):
            self.assertTrue(i)

    def test_create_account_instructor(self):
        '''
        Unit Test that attempts to create existing instructor account
        '''

        data = {
                "email_input": "NewProf@wsu.edu",
                "password_input": "gfgfhtr2123",
                "wsuID_input": "57384758743",
                "firstname_input": "Sam",
                "lastname_input": "Dam",
                "account": "Instructor",
                "phone_input": "243-521-5214"
                }
        response = self.app.post("/newaccount", data=data)
        self.assertEqual(response.location, "http://localhost/signup")
    
    def test_create_account_instructor2(self):
        '''
        Unit Test that attempts to create new instructor account
        '''

        data = {
                "email_input": "TestProf@wsu.edu",
                "password_input": "r2123",
                "wsuID_input": "4353532",
                "firstname_input": "Jam",
                "lastname_input": "Mam",
                "account": "Instructor",
                "phone_input": "243-521-5214"
                }
        response = self.app.post("/newaccount", data=data)
        self.assertEqual(response.location, "http://localhost/viewprofile")

        # Verify that account is actually in DB
        for i in self.verify_info("TestProf@wsu.edu", data):
            self.assertTrue(i)

    def test_edit_profile_student(self):
        '''
        Unit Test that attempts to edit profile of a student
        '''
        self.app.post("/login", data=dict(email="NewStudent@wsu.edu", password="gfgfhtr2123", remember=True))
        data = {
                "edit_name_input": "Sam Jam",
                "edit_major_input": "Computer Science",
                "edit_gpa_input": "4.0",
                "edit_experience_input": "Physics 202: 1 year, Math 216: 2 years",
                "edit_phone_input": "443-521-5214"
                }
        response = self.app.post("/edit-account", data=data)
        curr = User.query.filter_by(email="NewStudent@wsu.edu").first()
        self.assertEqual(response.location, "http://localhost/viewprofile")
        self.assertEqual(curr.name, data["edit_name_input"].split()[0])
        self.assertEqual(curr.lastName, data["edit_name_input"].split()[1])
        self.assertEqual(curr.major, data["edit_major_input"])
        self.assertEqual(curr.gpa, float(data["edit_gpa_input"]))
        self.assertEqual(curr.phone, data["edit_phone_input"])
        self.assertEqual(curr.experience, data["edit_experience_input"])
    
    def test_edit_profile_instructor(self):
        '''
        Unit Test that attempts to edit profile of an instructor
        '''
        self.app.post("/login", data=dict(email="TestProf@wsu.edu", password="r2123", remember=True))
        data = {
                "edit_name_input": "Sam Jam",
                "edit_phone_input": "443-521-5214"
                }
        response = self.app.post("/edit-account", data=data)
        curr = User.query.filter_by(email="TestProf@wsu.edu").first()
        self.assertEqual(response.location, "http://localhost/viewprofile")
        self.assertEqual(curr.name, data["edit_name_input"].split()[0])
        self.assertEqual(curr.lastName, data["edit_name_input"].split()[1])
        self.assertEqual(curr.phone, data["edit_phone_input"])
    
    def test_create_course(self):
        '''
        Unit Test that attempts to create new course
        '''
        self.app.post("/login", data=dict(email="TestProf@wsu.edu", password="r2123", remember=True))
        response = self.app.post("/create-course", data={"create_course_input": "Engl 101"})
        self.assertEqual(response.location, "http://localhost/display_courses")

        curr = Classes.query.filter_by(title="Engl 101").first()
        prof = User.query.filter_by(email="TestProf@wsu.edu").first()
        self.assertNotEqual(curr, None)
        self.assertEqual(curr.teacherID, prof.userID)

    def test_create_course2(self):
        '''
        Unit Test that attempts to create existing course. Depends on previous test case
        '''
        self.app.post("/login", data=dict(email="TestProf@wsu.edu", password="r2123", remember=True))
        response = self.app.post("/create-course", data={"create_course_input": "Engl 101"})
        self.assertEqual(response.location, "http://localhost/create_course")
        curr = Classes.query.filter_by(title="Engl 101").first()
        self.assertNotEqual(curr, None)

if __name__ == '__main__':
    unittest.main()