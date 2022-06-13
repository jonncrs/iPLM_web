#notif new import
import mysql.connector

_db = mysql.connector.connect(host = "localhost", user = "root", password = "")

class Query():
    def lastName(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute(f"SELECT lastName from crs_user WHERE id = {id}")
        lastName = Q.fetchone()
        return lastName[0]

    def honorific(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute(f"SELECT studentGender from crs_studentinfo WHERE studentUser_id = {id}")
        gender = Q.fetchone()
        if gender[0] == "Male":
            honorific = "Mr."
            return honorific
        else:
            honorific = "Ms."
            return honorific

    def deptID_from_students(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute(f"SELECT departmentID_id from crs_studentinfo WHERE studentUser_id = {id}")
        dept_id = Q.fetchone() 
        return dept_id[0]
    
    def cpersonID_from_department(dept_id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute(f"SELECT chairperson_id from crs_department WHERE id = {dept_id}")
        cperson_id = Q.fetchone() 
        return cperson_id[0]

class shifterApplicants():
    def id():
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT id from crs_shifterapplicant where id = (SELECT max(id) from crs_shifterapplicant)" )
        last_insertID = Q.fetchone()
        return last_insertID[0]

    def dept(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT department from crs_shifterapplicant where id = " +  str(id))
        dept = Q.fetchone()
        return dept[0]
    
    def dept_id(dept):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT id from crs_department WHERE courseName like '%" +  str(dept) +"'")
        dept_id = Q.fetchone()
        return dept_id[0]
    
    def lastName(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT lname from crs_shifterapplicant WHERE id = " + str(id))
        lastName = Q.fetchone()
        return lastName[0]

    def honorific(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT sex from crs_shifterapplicant WHERE id = " + str(id))
        gender = Q.fetchone()
        if gender[0] == "Male":
            honorific = "Mr."
            return honorific
        else:
            honorific = "Ms."
            return honorific

class transfereeApplicants():
    def id():
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT id from crs_transfereeapplicant where id = (SELECT max(id) from crs_transfereeapplicant)" )
        last_insertID = Q.fetchone()
        return last_insertID[0]

    def dept(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT department from crs_transfereeapplicant where id = " +  str(id))
        dept = Q.fetchone()
        return dept[0]
    
    def dept_id(dept):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT id from crs_department WHERE courseName like '%" +  str(dept) +"'")
        dept_id = Q.fetchone()
        return dept_id[0]
    
    def lastName(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT lname from crs_transfereeapplicant WHERE id = " + str(id))
        lastName = Q.fetchone()
        return lastName[0]

    def honorific(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT sex from crs_transfereeapplicant WHERE id = " + str(id))
        gender = Q.fetchone()
        if gender[0] == "Male":
            honorific = "Mr."
            return honorific
        else:
            honorific = "Ms."
            return honorific

class facultyApplicants():
    def id():
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT id from crs_facultyapplicant where id = (SELECT max(id) from crs_facultyapplicant)" )
        last_insertID = Q.fetchone()
        return last_insertID[0]

    def dept(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT department from crs_facultyapplicant where id = " +  str(id))
        dept = Q.fetchone()
        return dept[0]
    
    def dept_id(dept):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT id from crs_department WHERE courseName like '%" +  str(dept) +"'")
        dept_id = Q.fetchone()
        return dept_id[0]
    
    def lastName(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT lastName from crs_facultyapplicant WHERE id = " + str(id))
        lastName = Q.fetchone()
        return lastName[0]

    def honorific(id):
        global _db
        Q = _db.cursor()
        Q.execute("USE iplmdatabase")
        Q.execute("SELECT sex from crs_facultyapplicant WHERE id = " + str(id))
        gender = Q.fetchone()
        if gender[0] == "Male":
            honorific = "Mr."
            return honorific
        else:
            honorific = "Ms."
            return honorific