from tkinter import Entry
from django import forms
import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models import JSONField, Model
from django.forms import ValidationError
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from pytz import utc
from django.forms import ValidationError
from django.utils import timezone
from django.contrib import messages
from datetime import date
from django.core.validators import validate_email
from dis import findlabels

from .validators import validate_file_extension

import datetime
import os

now = timezone.now()

SemesterDropdown = [
    ('1', 'First Semester'),
    ('2', 'Second Semester')
]

SchoolYearDropdown = []
for y in range((datetime.datetime.now().year) - 5, (datetime.datetime.now().year) + 1):
    SchoolYearDropdown.append((y, y))

CollegeDropdown = [
    ('1', 'CET'),
    ('2', 'CEE')
]

PurposeDropdown = [
    ('1', 'Health Problems'),
    ('2', 'Financial Problems'),
    ('3', 'Employment Obligations'),
    ('4', 'Depression'),
    ('5', 'Academic Endeavors')
]

class College(models.Model):
    collegeName = models.CharField(max_length=150, null=True, verbose_name='College Name')
    collegeDesc = models.CharField(max_length=200, null=True, blank=True, verbose_name='College Description')

    def __str__(self):
        return self.collegeName


# Base User Database
class UserManager(BaseUserManager):
    def create_user(self, email1, email, firstName, middleName, lastName, password=None):
        """
        Creates and saves a User with the given email, name, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not email1:
            raise ValueError('Users must have an email address')

        user = self.model(
            email1=self.normalize_email(email1),
            email=self.normalize_email(email),
            firstName=firstName,
            middleName=middleName,
            lastName=lastName,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email1, email, firstName, middleName, lastName, password=None):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(
            email1, email,
            password=password,
            firstName=firstName,
            middleName=middleName,
            lastName=lastName
        )
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):

    email_error_message = 'Email must be: @plm.edu.ph'
    email_regex = RegexValidator(
    regex=r'^[A-Za-z0-9._%+-]+@plm.edu.ph$',
    message=email_error_message
    )

    email = models.EmailField(
        verbose_name='PLM Email Address', validators=[email_regex],
        max_length=255,
        unique=True,
    )
    
    email1 = models.EmailField(
    verbose_name='Personal Email Address',
    max_length=255,
    unique=True,
    default='example@gmail.com',
    )

    firstName = models.CharField(max_length=100, verbose_name='First Name')
    middleName = models.CharField(max_length=100, blank=True, default="", verbose_name='Middle Name')
    lastName = models.CharField(max_length=100, verbose_name='Last Name')
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    is_chairperson = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_applicant = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email1','firstName', 'middleName', 'lastName']

    def full_name(self):
        return self.email1, self.email, self.lastName, self.firstName, self.middleName

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "User"


# Do not remove or modify the above users ^^

# ------------------ Academic Year Info----------------------------------------------------

class AcademicYearInfo(models.Model):
    year_error_message = 'Year must be entered in format: 20XX'
    year_regex = RegexValidator(
        regex=r'^20\d{2}$',
        message=year_error_message
    )
    yearstarted = models.CharField(validators=[year_regex], max_length=50, verbose_name='Year Started', null=True)
    yearended = models.CharField(validators=[year_regex], max_length=50, verbose_name='Year Ended', null=True)
    semester = models.CharField(max_length=150, null=True, verbose_name='Semester')

    class Meta:
            verbose_name_plural = "Academic Year Information"

    def __str__(self):
        return '%s - %s' % (self.yearstarted, self.yearended)


# ------------------ Chairperson Database----------------------------------------------------
class ChairpersonInfo (models.Model):
    cpersonUser = OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="Chairperson User")

    class Meta:
        verbose_name_plural = "Chairperson Information"
    
    def __str__(self):
        return self.cpersonUser.email


class Department(models.Model):
    collegeId = ForeignKey(College, null=True, verbose_name='College', on_delete=models.CASCADE)
    courseName = models.CharField(max_length=150, null=True, verbose_name='Course')
    courseDesc = models.CharField(max_length=200, null=True, blank=False, verbose_name='Course Description')
    chairperson = ForeignKey(ChairpersonInfo, on_delete=models.PROTECT, null=True, blank=False)

    def __str__(self):
        return self.courseName
    class Meta:
        constraints =[models.UniqueConstraint(fields=['collegeId', 'courseName'], name='Department')]




# ------------------ Faculty Database -----------------------------------------------------------
class FacultyInfo(models.Model):
    WorkStatus_CHOICES = (
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
    )

    Gender_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    CivilStatus_CHOICES = (
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Separated', 'Separated'),
        ('Widow', 'Widow'),
    )

    Citizenship_CHOICES = (
        ('Filipino', 'Filipino'),
        ('Others', 'Others'),
    )

    # ID number code. Can be copy pasted to suit ID code for certain user.
    facultyID_error_message = 'Faculty ID must be entered in format: 20XXXXXXX'
    facultyID_regex = RegexValidator(
        regex=r'^20\d{7}$',
        message=facultyID_error_message
    )

    # Contact Number format code
    phone_error_message = 'Contact number must be entered in format: 09XXXXXXXXX'
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message=phone_error_message
    )

    def fid_default():
        year = date.today().year
        check = FacultyInfo.objects.all()
        if check.exists():
            id = FacultyInfo.objects.latest('facultyUser_id')
        else:
            id = 1
        fetch = str(id)
        final = fetch.split()[0].strip()
        f_id = int(final)
        overOneThousand = 0
        lengthFacultyId = 0
        stringFacultyID = str(f_id)
        stringOverOneThousand = str(overOneThousand)
        finalFacultyID = ''
        lengthFacultyId = len(stringFacultyID)

        def lengthOfRawFacultyId(lengthOfID ,rawFacultyId):
            fiveDigitFacultyId = ''
            if lengthOfID == 1:
                fiveDigitFacultyId = '000' + rawFacultyId
            elif lengthOfID == 2:
                fiveDigitFacultyId = '00' + rawFacultyId
            elif lengthOfID == 3:
                fiveDigitFacultyId = '0' + rawFacultyId
            return fiveDigitFacultyId

        if f_id > 1000:
            while f_id >= 1000:
                f_id += 1
                f_id -= 1000
            stringOverOneThousand = str(overOneThousand)
            stringFacultyID = str(f_id)
            lengthFacultyId = len(stringFacultyID)
            finalFacultyID = str(year) + stringOverOneThousand + lengthOfRawFacultyId(lengthFacultyId, stringFacultyID)
        else:
            finalFacultyID = str(year) + stringOverOneThousand + lengthOfRawFacultyId(lengthFacultyId, stringFacultyID)
        
        return finalFacultyID

    facultyUser = OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name='Faculty User')
    facultyID = models.CharField(validators=[facultyID_regex], max_length=50,
                                 unique=True, verbose_name='Faculty ID', null=True, default=fid_default)
    collegeID = ForeignKey(College, null=True, verbose_name='College', on_delete=models.SET_NULL, blank=False, default=1)
    departmentID = ForeignKey(Department, null=True, verbose_name='Department', on_delete=models.SET_NULL, blank=False, default=1)
    facultyWorkstatus = models.CharField(max_length=100, choices=WorkStatus_CHOICES,
                                         null=True, verbose_name='Work Status')
    facultyGender = models.CharField(max_length=50, null=True, choices=Gender_CHOICES, verbose_name='Gender')
    facultyCivilstatus = models.CharField(max_length=150, null=True, choices=CivilStatus_CHOICES,
                                          verbose_name='Civil Status')
    facultyCitizenship = models.CharField(max_length=50, null=True, default='Filipino',verbose_name='Citizenship')
    facultyContact = models.CharField(validators=[phone_regex], max_length=50,
                                      null=True, verbose_name='Contact Number')
    facultyIn = models.CharField(max_length=100, null=True, blank=False, verbose_name='Time In', default = "7:00")
    facultyOut = models.CharField(max_length=100, null=True, blank=False, verbose_name='Time Out', default = "22:00")

    class Meta:
        verbose_name_plural = "Faculty Information"

    def __str__(self):
       return '%s - %s, %s - (%s) '%(self.facultyUser.id, self.facultyUser.lastName, self.facultyUser.firstName,self.facultyWorkstatus)

class BlockSection(models.Model):
    Year_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    )
    Block_CHOICES = (
    ('BS IT', 'BS IT'),
    ('BS EE', 'BS EE'),
    )
    blockYear = models.CharField(max_length=150, null=True, choices= Year_CHOICES, verbose_name='Block Year Level')
    blockSection = models.CharField(max_length=50,null=True, verbose_name='Block Section')
    college = models.ForeignKey(College, null=True, verbose_name='College', on_delete=models.PROTECT)
    blockCourse = models.CharField(max_length=50, null=True, choices= Block_CHOICES, verbose_name='Block Course')
    curryear = models.CharField(max_length=50, null=True, verbose_name='Curriculum Year')
    adviser = models.ForeignKey(FacultyInfo, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Block Section"
        constraints =[models.UniqueConstraint(fields=['blockYear', 'blockSection','blockCourse'], name='block section')]

    def __str__(self):
        return '%s %s - %s' %(self.blockCourse, self.blockYear, self.blockSection)


# ------------------ Curriculum and Subjects----------------------------------------------------
class RoomSchedule(models.Model):
    classTimeIn = models.TimeField(max_length=200)
    classTimeOut = models.TimeField(max_length=200, null=True)
    Day = (('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
           ('thursday', 'thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'))
    classDay = models.CharField(max_length=200, choices=Day, null=True)

    class Meta:
        verbose_name = "Room Schedule"

    def __str__(self):
        return self.classDay


class RoomInfo(models.Model):
    room = models.CharField(max_length=100, null=True, verbose_name='Room',unique=True)

    class Meta:
        verbose_name_plural = "Room Information"

    def __str__(self):
        return self.room


class subjectInfo(models.Model):
    subjectCode = models.CharField(max_length=50, unique=True, verbose_name='Subject Code', null=True)
    subjectName = models.CharField(max_length=100, verbose_name="Subject Name", null=True)
    subjectPrerequisite = models.CharField(max_length=100, verbose_name="Pre-requisite", null=True, blank=True)
    yearstanding = models.CharField(max_length=100, verbose_name="Year Standing", null=True, blank=True)
    college = ForeignKey(College, null=True, verbose_name='College', on_delete=models.SET_NULL, blank=True)

    class Meta:
        verbose_name_plural = "Subject Information"
        constraints =[models.UniqueConstraint(fields=['subjectCode', 'subjectName','college'], name='subject')]

    def __str__(self):
        return '| %s | %s |' % (self.subjectCode, self.subjectName)


class SubjectSchedule(models.Model):
    subjectCode = models.ForeignKey(subjectInfo, null=True, on_delete=DO_NOTHING)
    faculty = models.ForeignKey(FacultyInfo, null=True, on_delete=DO_NOTHING)
    roomSchedule = models.ForeignKey(RoomSchedule, null=True, on_delete=DO_NOTHING)
    room = models.ForeignKey(RoomInfo, null=True, on_delete=DO_NOTHING)
    Session = (('Synchronous', 'Synchronous'), ('Asynchronous', 'Asynchronous'))
    sessionType = models.CharField(max_length=200, choices=Session)
    Type = (('Block', 'Block'), ('Subject', 'Subject'))
    scheduleType = models.CharField(max_length=200, choices=Type)
    blockSection = models.ForeignKey(BlockSection, null=True, on_delete=DO_NOTHING)
    Status = (('ACTIVE', 'ACTIVE'), ('INACTIVE', 'INACTIVE'))
    status = models.CharField(max_length=200, choices=Status, null=True)
    YearStand = (('First Year', 'First Year'), ('Second Year', 'Second Year'), ('Third Year', 'Third Year'),
                 ('Fourth Year', 'Fourth Year'), ('Fifth Year', 'Fifth Year'), ('Sixth Year', 'Sixth Year'),
                 ('Servicing Colleges', 'Servicing Colleges'))
    yearStanding = models.CharField(max_length=200, choices=YearStand, null=True)

    class Meta:
        verbose_name = "Subject Schedule"

    def __str__(self):
        return self.status


class curriculumInfo(models.Model):

    SchoolYear = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]

    SchoolSem = [
        ('1', 'First Semester'),
        ('2', 'Second Semester'),
        ('Summer', 'Summer')
    ]
    
    curriculumyear = models.CharField(max_length=100, verbose_name="Curriculum Year", null=True)
    subjectUnits = models.CharField(max_length=100, verbose_name="Subject Units", null=True)
    schoolYear = models.CharField(max_length=100,choices=SchoolYear, verbose_name="School Year", null=True)
    schoolSem = models.CharField(max_length=100,choices=SchoolSem, verbose_name="School Sem", null=True)
    departmentID = models.ForeignKey(Department, null=True, verbose_name='Department', on_delete=models.SET_NULL,
                                     blank=False)
    subjectCode = models.ForeignKey(subjectInfo, null=True, verbose_name='Subject', on_delete=models.SET_NULL,
                                    blank=False)
    blockCourse = models.CharField(max_length=100, verbose_name="Course", null=True)
    counted_in_GWA = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Curriculum Information"
        constraints = [models.UniqueConstraint(fields=['curriculumyear', 'schoolYear','schoolSem','departmentID','subjectCode'], name='curriculum')]

    def __str__(self):
        return '| %s  %s | %s ' % (self.curriculumyear, self.subjectCode,self.blockCourse)


# --------------------------- Student Database-----------------------------------------
class StudentInfo(models.Model):
    Type_CHOICES = (('Old', 'Old'), ('New', 'New'),)
    Status_CHOICES = (('Regular', 'Regular'), ('Irregular', 'Irregular'),)

    Gender_CHOICES = (('Male', 'Male'), ('Female', 'Female'),)
    CivilStatus_CHOICES = (('Single', 'Single'), ('Married', 'Married'),)

    Citizenship_CHOICES = (('Filipino', 'Filipino'),)
    Year_CHOICES = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'),)

    # ID number code. Can be copy pasted to suit ID code for certain user.
    studentID_error_message = 'Student ID must be entered in format: 20XXXXXXX'
    studentID_regex = RegexValidator(
        regex=r'^20\d{7}$',
        message=studentID_error_message
    )
    # Contact Number format code
    phone_error_message = 'Contact number must be entered in format: 09XXXXXXXXX'
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message=phone_error_message
    )
    # Curriculum Year format code
    curr_error_message = 'Curriculum Year must be entered in format: 20XX'
    curr_regex = RegexValidator(
        regex=r'^20\d{2}$',
        message=curr_error_message
    )

    def sid_default():
        year = date.today().year
        check = StudentInfo.objects.all()
        if check.exists():
            id = StudentInfo.objects.latest('studentUser_id')
        else:
            id = 1
        fetch = str(id)
        final = fetch.split()[0].strip()
        s_id = int(final)
        overOneThousand = 0
        lengthStudentId = 0
        stringStudentID = str(s_id)
        stringOverOneThousand = str(overOneThousand)
        finalStudentID = ''
        lengthStudentId = len(stringStudentID)

        def lengthOfRawStudentId(lengthOfID ,rawStudentId):
            fiveDigitStudentId = ''
            if lengthOfID == 1:
                fiveDigitStudentId = '000' + rawStudentId
            elif lengthOfID == 2:
                fiveDigitStudentId = '00' + rawStudentId
            elif lengthOfID == 3:
                fiveDigitStudentId = '0' + rawStudentId
            return fiveDigitStudentId

        if s_id > 1000:
            while s_id >= 1000:
                s_id += 1
                s_id -= 1000
            stringOverOneThousand = str(overOneThousand)
            stringStudentID = str(s_id)
            lengthStudentId = len(stringStudentID)
            finalStudentID = str(year) + stringOverOneThousand + lengthOfRawStudentId(lengthStudentId, stringStudentID)
        else:
            finalStudentID = str(year) + stringOverOneThousand + lengthOfRawStudentId(lengthStudentId, stringStudentID)
            
        return finalStudentID

    studentUser = OneToOneField(User, on_delete=CASCADE, primary_key=True, verbose_name='Student Email')
    studentID = models.CharField(validators=[studentID_regex], max_length=50, unique=True, verbose_name='Student ID',
                                 null=True, default = sid_default)
    collegeID = ForeignKey(College, null=True, verbose_name='College', on_delete=models.SET_NULL, blank=False, default=1)
    departmentID = ForeignKey(Department, null=True, verbose_name='Department', on_delete=models.SET_NULL, blank=False, default=1)
    studentGender = models.CharField(max_length=50, null=True, choices=Gender_CHOICES, verbose_name='Gender')
    studentCitizenship = models.CharField(max_length=50, null=True,default='Filipino', verbose_name='Citizenship')
    studentCivilstatus = models.CharField(max_length=150, null=True, choices=CivilStatus_CHOICES,
                                          verbose_name='Civil Status', default=1)
    studentContact = models.CharField(validators=[phone_regex], max_length=50, null=True, verbose_name='Contact Number')
    studentRegStatus = models.CharField(max_length=100, choices=Status_CHOICES, null=True,
                                        verbose_name='Student Status')
    studentType = models.CharField(max_length=150, null=True, choices=Type_CHOICES, verbose_name='Student Type')
    studentCourse = models.CharField(max_length=50, null=True, verbose_name='Course', default='BSIT')
    studentYearlevel = models.CharField(max_length=150, null=True, choices=Year_CHOICES, verbose_name='Year Level')
    studentSection = models.ForeignKey(BlockSection, null=True, verbose_name='Section', on_delete=models.SET_NULL,
                                       blank=False)
    studentCurriculum = models.CharField(validators=[curr_regex], max_length=50, verbose_name='Curriculum Year',
                                         null=True, default= date.today().year)

    # advisoryClasscode = ForeignKey(advisoryClass, null=True, verbose_name='Class Advisory', on_delete=DO_NOTHING)

    class Meta:
        verbose_name_plural = "Student Information"
    
    def __str__(self):
        return '%s' %(self.studentID)


# HD Application
class hdApplicant(models.Model):
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE, blank=False)
    studentDropform = models.FileField(upload_to='hdSubmission/', blank=False, null=True, validators=[validate_file_extension], verbose_name="Student Drop Form")
    studentClearanceform = models.FileField(upload_to='hdSubmission/', blank=False, null=True, validators=[validate_file_extension], verbose_name="Student Clearance Form")
    studentTransfercert = models.FileField(upload_to='hdSubmission/', blank=False, null=True, validators=[validate_file_extension], verbose_name="Student Transfer Certificate")
    studentHdletter = models.FileField(upload_to='hdSubmission/', blank=False, null=True, validators=[validate_file_extension], verbose_name="Student HD Letter")
    studentGrades = models.FileField(upload_to='hdSubmission/', blank=False, null=True, validators=[validate_file_extension], verbose_name="Student Grades")
    stdParentsig = models.FileField(upload_to='hdSubmission/', blank=False, null=True, validators=[validate_file_extension], verbose_name="Student\'s Parent Signature")
    remarks = models.CharField(default="Submitted", max_length=25)
    comment = models.TextField(max_length=150, null=True, blank=False, verbose_name="Feedback")
    hd_dateSubmitted = models.DateField(default=now, verbose_name="HD Date Submitted")

    # dateApproved = models.DateTimeField()
    class Meta:
        verbose_name = "HD Applicant"

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)


# OJT Application
class OjtApplicant(models.Model):
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE, blank=True)
    ojtResume = models.FileField(upload_to='ojtSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='OJT Resume')
    ojtRecLetter = models.FileField(upload_to='ojtSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='OJT Recommended Letter')
    ojtWaiver = models.FileField(upload_to='ojtSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name=' OJT Waiver')
    ojtAcceptForm = models.FileField(upload_to='ojtSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='OJT Accept Form')
    ojtCompanyProfile = models.FileField(upload_to='ojtSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='OJT Company Profile')
    ojtCompanyId = models.FileField(upload_to='ojtSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='OJT Company ID')
    ojtMedcert = models.FileField(upload_to='ojtSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='OJT Medical Certificate')
    remarks = models.CharField(max_length=150, default='Submitted', verbose_name='Status')
    comment = models.TextField(max_length=150, null=True, blank=True, verbose_name='Feedback')
    ojt_dateSubmitted = models.DateField(default=now, verbose_name='OJT Date Submitted')

    class Meta:
        verbose_name = "OJT Applicant"

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)


class spApplicant(models.Model):
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE, blank=True)
    remarks = models.CharField(default="Submitted", max_length=25)
    date = models.DateField(default=now)
    sdplan = models.FileField(upload_to='spSubmission/', null=True, blank=True, verbose_name='Study Plan')
    comment = models.TextField(max_length=150, null=True, blank=True, verbose_name='Feedback')

    class Meta:
        verbose_name = "Study Plan Applicant"

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)


class LOAApplicant(models.Model):
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE, blank=True)
    studentLOAClearanceform = models.FileField(upload_to='LOASubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student LOA Clearance Form')
    studentStudyplan = models.FileField(upload_to='LOASubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Study Plan')
    studentLOAletter = models.FileField(upload_to='LOASubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student LOA Letter')
    studentLOAFORM = models.FileField(upload_to='LOASubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student LOA Form')
    studentChecklist = models.FileField(upload_to='LOASubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Checklist')
    studentDroppingForm = models.FileField(upload_to='LOASubmission/', blank=True, null=True)
    remarks = models.CharField(max_length=150, default='Submitted')
    status = models.CharField(max_length=150, default='Pending')
    comment = models.TextField(null=True, blank=True, verbose_name='Feedback')
    LOA_dateSubmitted = models.DateField(default=now, verbose_name='LOA Date Submitted')
    signature1 = models.ImageField(upload_to='LOASign/', null=True, blank=True, verbose_name='First Signature')
    signature2 = models.ImageField(upload_to='LOASign/', null=True, blank=True, verbose_name='Second Signature')

    # dateApproved = models.DateTimeField()
    class Meta:
        verbose_name= "LOA Applicant"

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)


class currchecklist(models.Model):
    GRADES = (
    (1.00,'1'),
    (1.25,'1.25'),
    (1.50,'1.50'),
    (1.75,'1.75'),
    (2,'2'),
    (2.25,'2.25'),
    (2.5,'2.5'),
    (2.75,'2.75'),
    (3.00,'3'),
    (5.00,'5'),
    )

    SEMESTER  = (
    ('1', '1'),
    ('2', '2'),
    ('Summer', 'Summer'),
    )

    YEARLEVEL = (
    ('1', '1st Year'),
    ('2', '2nd Year'),
    ('3', '3rd Year'),
    ('4', '4th Year'),
    ('5', '5th Year'),
    ('6', '6th Year'),
    )
    
    owner = models.ForeignKey(StudentInfo, null=True, verbose_name='Student Number', on_delete=models.CASCADE,blank=True)
    curriculumCode = models.ForeignKey(curriculumInfo, null=True, verbose_name='Subjects', on_delete=models.CASCADE)
    subjectGrades = models.DecimalField(decimal_places=2, max_digits=3,choices=GRADES, verbose_name="Subject Grades", null=True)
    yearTaken = models.CharField(max_length=50, choices=YEARLEVEL, verbose_name='Year Taken', null=True)
    semTaken = models.CharField(max_length=50, choices=SEMESTER, verbose_name="School Sem", null=True)

    class Meta:
            verbose_name = "Checklist"

    def __str__(self):
        return self.owner.studentUser.lastName


class crsGrade(models.Model):
    studentID =  models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE,blank=True)
    crsFile = models.FileField(upload_to='crsSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='CRS File')
    comment = models.TextField(null=True, blank=True, verbose_name='Feedback')
    remarks = models.CharField(max_length=150, default='Submitted', verbose_name='Status')

    class Meta:
            verbose_name = "CRS Grade"

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)

class crsChecklist(models.Model):
    studentID =  models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE,blank=True)
    checkList = models.FileField(upload_to='checklist/', blank=True, null=True)
    crsChecklist = models.FileField(upload_to='crsChecklist/', blank=True, null=True)
    crsApprovedChecklist = models.FileField(upload_to='approvedChecklist/', blank=True, null=True)
    comment = models.TextField(null=True, blank=True, verbose_name='Feedback')
    remarks = models.CharField(max_length=150, default='Submitted', verbose_name='Status')

    class Meta:
            verbose_name_plural = "CRS Checklist"

    def __str__(self):
        return self.studentID.studentUser.lastName

# FORMS TO FILL-UP
class hdClearanceForm(models.Model):
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE, blank=True)
    firstEnrollment = models.CharField(max_length=100, verbose_name="Semester (First Enrollment in PLM)", null=True)
    studentFirstSY = models.CharField(max_length=100, verbose_name="School Year (First Enrollment in PLM)", null=True)
    studentFirstCollege = models.CharField(max_length=100, verbose_name="College (First Enrollment in PLM)", null=True)
    lastEnrollment = models.CharField(max_length=100, verbose_name="Semester (Last/Present Enrollment in PLM)",
                                      null=True)
    studentLastPCollege = models.CharField(max_length=100, verbose_name="College (Last/Present Enrollment in PLM)",
                                           null=True)
    studentLastPSY = models.CharField(max_length=100, verbose_name="School Year (Last/Present Enrollment in PLM)",
                                      null=True)
    studentPurpose = models.CharField(max_length=100, verbose_name="Purpose of Clearance", null=True)
    studentOthers = models.CharField(max_length=100, verbose_name="If you picked others please specify:", blank=True,
                                     null=True)
    studentCurrentdate = models.DateField(max_length=100, verbose_name="Current Date", null=True)

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)
    
    class Meta:
        verbose_name = "HD Clearance Form"


class hdTransferCert(models.Model):
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE)
    studentSchool = models.CharField(max_length=100, verbose_name="School (Where you'll transfer)", null=True)
    studentSchooladdress = models.CharField(max_length=100, verbose_name="School Address (Where you'll transfer)",
                                            null=True)
    studentHomeaddress = models.CharField(max_length=100, verbose_name="Home Address", null=True)
    studentCollege = models.CharField(max_length=100, verbose_name="College", null=True)
    studentCredentials = models.CharField(max_length=100, verbose_name="Credentials", null=True)
    studentFirstSY = models.CharField(max_length=100, verbose_name="School Year (First Enrollment in College)",
                                      null=True)
    studentLastPSY = models.CharField(max_length=100, verbose_name="School Year (Last Enrollment in College)",
                                      null=True)
    studentNoOfSem = models.CharField(max_length=100, verbose_name="No. of Semesters/Summers Attended", null=True)
    studentDegree = models.CharField(max_length=100, verbose_name="Degree", null=True)
    studentMonth = models.CharField(max_length=100, verbose_name="Month", null=True)
    studentDay = models.CharField(max_length=100, verbose_name="Day", null=True)
    studentYear = models.CharField(max_length=100, verbose_name="Year", null=True)
    studentCurrentdate = models.DateField(max_length=100, verbose_name="Current Date", null=True)

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)

    class Meta:
        verbose_name = "HD Transfer Certificate"


class loaClearanceForm(models.Model):
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE)
    firstEnrollment2 = models.CharField(max_length=100, choices=SemesterDropdown, verbose_name="Semester (First Enrollment in PLM)", null=True)
    studentFirstSY2 = models.IntegerField(max_length=4, choices=SchoolYearDropdown, default=datetime.datetime.now().year, verbose_name="School Year (First Enrollment in PLM)", null=True)
    studentFirstCollege2 = models.CharField(max_length=100, choices=CollegeDropdown, verbose_name="College (First Enrollment in PLM)", null=True)
    lastEnrollment2 = models.CharField(max_length=100, choices=SemesterDropdown, verbose_name="Semester (Last/Present Enrollment in PLM)",
                                       null=True)
    studentLastPCollege2 = models.CharField(max_length=100, choices=CollegeDropdown, verbose_name="College (Last/Present Enrollment in PLM)",
                                            null=True)
    studentLastPSY2 = models.IntegerField(max_length=4, choices=SchoolYearDropdown, default=datetime.datetime.now().year, verbose_name="School Year (Last/Present Enrollment in PLM)",
                                       null=True)
    studentPurpose2 = models.CharField(max_length=100, choices=PurposeDropdown, verbose_name="Purpose of Clearance", null=True)
    studentOthers2 = models.CharField(max_length=100, verbose_name="Student Others 2", blank=True, null=True)
    studentCurrentdate2 = models.DateField(max_length=100, verbose_name="Current Date", null=True)

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)

    class Meta:
        verbose_name = "LOA Clearance Form"

# LOA FORM
class loaForm(models.Model):
    SchoolYearDropdown = []
    for y in range((datetime.datetime.now().year) - 2, (datetime.datetime.now().year) + 7):
        SchoolYearDropdown.append((y, y))
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE)
    genave = models.DecimalField(decimal_places=2, max_digits=3, verbose_name="GWA", null=True)
    sem = models.CharField(max_length=100, choices=SemesterDropdown, verbose_name="Effective From Sem", null=True)
    sy = models.IntegerField(max_length=4, choices=SchoolYearDropdown, default=datetime.datetime.now().year, verbose_name="Effective From S.Y.:", null=True)
    sem2 = models.CharField(max_length=100, choices=SemesterDropdown, verbose_name="Effective Until Sem", null=True)
    sy2 = models.IntegerField(max_length=4, choices=SchoolYearDropdown, default=datetime.datetime.now().year, verbose_name="Effective Until S.Y.:", null=True)
    reason = models.CharField(max_length=100, choices=PurposeDropdown, verbose_name="Reason", blank=True, null=True)
    dof = models.DateField(max_length=100, verbose_name="Date of Filing", null=True)

    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.studentID.studentUser.lastName, self.studentID.studentUser.firstName)

    class Meta:
        verbose_name = "LOA Form"

# HD Dropping Form
class HD_DroppingForm(models.Model):
    Admin_Upload = models.FileField(upload_to='Student/Dropping Form', validators=[validate_file_extension])

    @property
    def filename(self):
        return os.path.basename(self.Admin_Upload.name)

    def __str__(self):
        return '%s - %s '%(self.id, os.path.basename(self.Admin_Upload.name))

    class Meta:
            verbose_name = "HD Dropping Form"

# Shifting Form
class ShiftingForm(models.Model):
    Admin_Upload = models.FileField(upload_to='Student/Shifting Form')

    class Meta:
            verbose_name_plural = "Shifting Form"

# OUTSHIFTER APPLICANT
class OutShifterApplicant(models.Model):
    studentID = models.ForeignKey(StudentInfo, null=True, verbose_name='Student', on_delete=models.CASCADE, blank=True)
    studentStudyplan = models.FileField(upload_to='OutShifterSubmission/', blank=True, null=True)
    studentshifterletter = models.FileField(upload_to='OutShifterSubmission/', blank=True, null=True)
    checklist = models.FileField(upload_to='OutShifterSubmission/', blank=True, null=True)
    shiftingForm = models.FileField(upload_to='OutShifterSubmission/', blank=True, null=True) 
    shifter_dateSubmitted = models.DateField(default=now)
    signature1 = models.ImageField(upload_to='ShifterSign/', null=True, blank=True)
    signature2 = models.ImageField(upload_to='ShifterSign/', null=True, blank=True)   
    remarks = models.CharField(max_length=150, default='Submitted', verbose_name='Status')
    comment = models.TextField(null=True, blank=True, verbose_name='Feedback')
    

    # dateApproved = models.DateTimeField()

    class Meta:
        verbose_name_plural = "Outbound Shifter Applicants"

    def __str__(self):
        return self.studentID.studentUser.lastName

# SHIFTER APPLICANT
class ShifterApplicant(models.Model):
    studentID = models.CharField(max_length=100, verbose_name="Student Number", null=True)
    department = models.CharField(max_length=100, verbose_name="Department", null=True)
    lname = models.CharField(max_length=100, verbose_name="Last Name", null=True)
    fname = models.CharField(max_length=100, verbose_name="First Name", null=True)
    mname = models.CharField(max_length=100, verbose_name="Middle Name", null=True)
    eadd = models.CharField(max_length=100, verbose_name="Email Address", null=True)
    cnum = models.CharField(max_length=100, verbose_name="Contact Number", null=True)
    studentStudyplan = models.FileField(upload_to='ShifterSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Study Plan')
    studentshifterletter = models.FileField(upload_to='ShifterSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Shifter Letter')
    studentGrade = models.FileField(upload_to='ShifterSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Grades')
    remarks = models.CharField(max_length=150, default='Submitted', verbose_name='Status')
    shifter_dateSubmitted = models.DateField(default=now, verbose_name='Shifter Date Submitted')
    signature1 = models.ImageField(upload_to='ShifterSign/', null=True, blank=True, verbose_name='First Signature')
    signature2 = models.ImageField(upload_to='ShifterSign/', null=True, blank=True, verbose_name='Second Signature')
    applicant_num = models.CharField(max_length=10, verbose_name="applicant_num", null=True)
    sex = models.CharField(max_length=100, verbose_name="sex", null=True)
    Checklist  = models.FileField(upload_to='ShifterSubmission/', blank=True, null=True)
    shiftingForm = models.FileField(upload_to='ShifterSubmission/', blank=True, null=True)
    comment = models.TextField(null=True, blank=True, verbose_name='Feedback')

    # dateApproved = models.DateTimeField()

    class Meta:
        verbose_name = "Shifter Applicant"
        
    def __str__(self):
        return '%s - %s, %s '%(self.studentID, self.lname, self.fname)

# TRANSFEREE APPLICANT
class TransfereeApplicant(models.Model):
    studentID = models.CharField(max_length=100, verbose_name="Student Number", null=True)
    department = models.CharField(max_length=100, verbose_name="Department", null=True)
    lname = models.CharField(max_length=100, verbose_name="Last Name", null=True)
    fname = models.CharField(max_length=100, verbose_name="First Name", null=True)
    mname = models.CharField(max_length=100, verbose_name="Middle Name", null=True)
    eadd = models.CharField(max_length=100, verbose_name="Email Address", null=True)
    cnum = models.CharField(max_length=100, verbose_name="Contact Number", null=True)
    studentStudyplan = models.FileField(upload_to='TransfereeSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Study Plan')
    studentNote = models.FileField(upload_to='TransfereeSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Note')
    studentHD = models.FileField(upload_to='TransfereeSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student HD')
    studentGoodmoral = models.FileField(upload_to='TransfereeSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Good Moral')
    studentGrade = models.FileField(upload_to='TransfereeSubmission/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Student Grade')
    comment = models.TextField(null=True, blank=True, verbose_name='Feedback')
    remarks = models.CharField(max_length=150, default='Submitted', verbose_name='Status')
    transfer_dateSubmitted = models.DateField(default=now, verbose_name='Tranfer Date Submitted')
    signature1 = models.ImageField(upload_to='TransfereeSign/', null=True, blank=True, verbose_name='First Signature')
    signature2 = models.ImageField(upload_to='TransfereeSign/', null=True, blank=True, verbose_name='Second Signature')
    applicant_num = models.CharField(max_length=10, verbose_name="applicant_num", null=True)
    sex = models.CharField(max_length=100, verbose_name="sex", null=True)
    # dateApproved = models.DateTimeField()

    class Meta:
        verbose_name = "Transferee Applicant"

    def str(self):
        return '| %s  %s ' % (self.studentID, self.lname)

    # dateApproved = models.DateTimeField()



# --------------------------- Faculty Applicant Database ---------------------------------------
class FacultyApplicant(models.Model):
    phone_error_message = 'Contact number must be entered in format: 09XXXXXXXXX'
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message=phone_error_message
    )
    
    lastName = models.CharField(max_length=100, verbose_name="Last Name", null=True)
    firstName = models.CharField(max_length=100, verbose_name="First Name", null=True)
    middleName = models.CharField(max_length=100, verbose_name="Middle Name", null=True)
    email = models.CharField(max_length=100, verbose_name="Email", null=True)
    phoneNumber = models.CharField(validators=[phone_regex], max_length=100, verbose_name='Phone Number', null=True)
    sex = models.CharField(max_length=100, verbose_name="sex", null=True)
    department = models.CharField(max_length=100, verbose_name="Department", null=True)
    time = models.CharField(max_length=100, verbose_name="Available Time", null=True)
    CV = models.FileField(upload_to='facultyApplicant/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Curriculum Vitae')
    certificates = models.FileField(upload_to='facultyApplicant/', blank=True, null=True, validators=[validate_file_extension])
    credentials = models.FileField(upload_to='facultyApplicant/', blank=True, null=True, validators=[validate_file_extension])
    TOR = models.FileField(upload_to='facultyApplicant/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Transcripts of Records')
    PDS = models.FileField(upload_to='facultyApplicant/', blank=True, null=True, validators=[validate_file_extension], verbose_name='Personal Data Sheet')
    remarks = models.CharField(max_length=150, default='Submitted', verbose_name='Status')
    applicant_num = models.CharField(max_length=10, verbose_name="applicant_num", null=True)
    comment = models.TextField(null=True, blank=True, verbose_name='Feedback')
    
    class Meta:
        verbose_name = "Faculty Applicant"

    def __str__(self):
        return self.email





class studentScheduling(models.Model):
    MONTH = (
    ('Monday','Monday'),
    ('Tuesday','Tuesday'),
    ('Wednesday','Wednesday'),
    ('Thursday','Thursday'),
    ('Friday','Friday'),
    ('Saturday','Saturday')
)
    TYPE = (
    ('Asynchronous','Asynchronous'),
    ('Synchronous','Synchronous'),
)
    
    def svalidate(value):
        if value <= 0:
            raise ValidationError(
                ('Section cannot be <= 0')
            )

    instructor = ForeignKey(FacultyInfo,  null=True, verbose_name='Instructor', on_delete=models.SET_NULL,blank=True)
    subjectCode = models.ForeignKey(curriculumInfo, null=True, verbose_name='Subjects', on_delete=models.CASCADE)
    section = models.IntegerField(null=True, blank=False, verbose_name='Subject Section', validators=[svalidate])
    day = models.CharField(max_length=100, null=True, choices=MONTH, verbose_name='Day')
    timeStart = models.TimeField(verbose_name='Time Start')
    timeEnd = models.TimeField(verbose_name='Time End')
    room = models.ForeignKey(RoomInfo, null=True, verbose_name='Room', on_delete=models.CASCADE)
    type= models.CharField(max_length=100, verbose_name="type",choices=TYPE, null=True)
    realsection= models.ForeignKey(BlockSection, null=True, verbose_name='Block Section', on_delete=models.SET_NULL,blank=True)

    class Meta:
        verbose_name_plural = "Student Scheduling"





# ---------------------------Saving and Creating Users----------------- ---------------------------
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_chairperson == True:
            ChairpersonInfo.objects.create(cpersonUser=instance)
        elif instance.is_faculty == True:
            FacultyInfo.objects.create(facultyUser=instance)
        elif instance.is_faculty == True:
            StudentInfo.objects.create(studentUser=instance)


#Database structures for study plan generation
class Curricula(models.Model):
    cYear = [
        ('First Year', 'First Year'),
        ('Second Year', 'Second Year'),
        ('Third Year', 'Third Year'),
        ('Fourth Year', 'Fourth Year'),
        ('Fifth Year', 'Fifth Year'),
        ('Sixth Year', 'Sixth Year')
    ]

    cSem = [
        ('First Semester', 'First Semester'),
        ('Second Semester', 'Second Semester'),
        ('Summer', 'Summer')
    ]

    departmentID = models.ForeignKey(Department, verbose_name='Department', null=True, on_delete=models.PROTECT)
    cYear = models.CharField(max_length=100, choices=cYear, verbose_name="Curriculum Year", null=True)
    cSem = models.CharField(max_length=100, choices=cSem, verbose_name="Curriculum Semester", null=True)
    totalUnits = models.IntegerField(verbose_name="Total Units", null=True)
    schoolYr = models.CharField(max_length=50, verbose_name="School Year", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Curricula"
        constraints = [
            models.UniqueConstraint(fields=['departmentID', 'cYear', 'cSem', 'schoolYr'], name='unique_curriculum')
        ]

    def __str__(self):
        return '%s %s - %s, %s' %(self.departmentID, self.schoolYr, self.cYear, self.cSem)

class courseList(models.Model):
    curricula = models.ForeignKey(Curricula, verbose_name='Curriculum', null=True, on_delete=models.PROTECT)
    courseCode = models.CharField(max_length=50, verbose_name="Course Code", null=True)
    courseName = models.CharField(max_length=100, verbose_name="Course Name", null=True)
    courseUnit = models.IntegerField(verbose_name="Units", null=True)
    prerequisite = models.CharField(max_length=100, verbose_name="Pre(Co)-Requisite", null=True, blank=True)
    counted_in_GWA = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Course List"
        constraints = [
            models.UniqueConstraint(fields=['curricula', 'courseCode'], name='course_outline')
        ]

    def __str__(self):
       return '%s: %s - %s' %(self.curricula.departmentID, self.courseCode, self.courseName)

class studyPlan(models.Model):
    studentinfo = models.ForeignKey(StudentInfo, unique=True, verbose_name='Student', null=True, on_delete=models.CASCADE)
    admissionYr = models.CharField(max_length=50, verbose_name="Admission Year", null=True, blank=True)
    curricula = models.ForeignKey(Curricula, verbose_name='Curricula', null=True, blank=True, on_delete=models.SET_NULL)
    failedsubs = models.JSONField(default='', verbose_name='Failed Subjects')

    def __str__(self):
        return self.studentinfo.studentID

    class Meta:
        verbose_name = "Study Plan"

class Notification(models.Model): 
    STATUS_CHOICES = (
        ('Read', 'Read'),
        ('Unread', 'Unread')
    )

    user_id = models.ForeignKey(User, verbose_name='User Email', on_delete=models.CASCADE)
    title = models.CharField(verbose_name="title", max_length=255)
    description = models.CharField(verbose_name="description", max_length=255)
    status = models.CharField(verbose_name="status", choices=STATUS_CHOICES, max_length=255, default="Unread")
    created_at = models.TimeField(verbose_name="created_at", auto_now_add=True)

    def __str__(self):
        return self.title

class Event(models.Model):
    CATEGORY_CHOICES = (
        ('Academics', 'Academics'), 
        ('Sports', 'Sports'),
        ('Social', 'Social'),
        ('Arts & Culture', 'Arts & Culture'),
        ('Featured', 'Featured')
        )
    eventCategory = models.CharField(verbose_name='Category', max_length=255, choices=CATEGORY_CHOICES)
    eventTitle = models.CharField(verbose_name='title', max_length=255)
    eventDescription = models.TextField(verbose_name='description')
    eventStartDate = models.DateTimeField(verbose_name='start date', default=now + timedelta(hours=1))
    eventEndDate = models.DateTimeField(verbose_name='end date', default=now + timedelta(hours=2))

    # Validator For Admin Page
    def clean(self):
        if self.eventStartDate < now:
            raise ValidationError('Cannot Add Events in the Past')
        if self.eventStartDate > self.eventEndDate:
            raise ValidationError('Cannot Add End Date if in the Past of Start Date')

    def validate_frontend(self, *args, **kwargs):
        if utc.localize(parse_datetime(self.eventStartDate)) < now:
            raise ValidationError('Cannot Add Events in the Past')
        if utc.localize(parse_datetime(self.eventStartDate)) > utc.localize(parse_datetime(self.eventEndDate)):
            raise ValidationError('Cannot Add End Date if in the Past of Start Date')
    
    def format_startDate(self):
        return datetime.date.strftime(self.eventStartDate, '%Y-%m-%dT%H:%M')
    def format_endDate(self):
        return datetime.date.strftime(self.eventEndDate, '%Y-%m-%dT%H:%M')

    def __str__(self):
        return '%s - %s' %(self.eventTitle, self.eventCategory) 