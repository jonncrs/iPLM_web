from email.policy import default
from django.forms import ModelForm
from django import forms
from .models import *
from django.forms import ValidationError

class InputGrades(ModelForm):
	class Meta:
		model = currchecklist
		fields = ('curriculumCode', 'subjectGrades')

class StudentsForm(forms.ModelForm):
	class Meta:
		model = StudentInfo
		fields = ('studentUser','studentSection')
		widgets = {
			'studentUser': forms.Select(
				attrs={"class": "form-control"}),

			'studentSection': forms.Select(
				attrs={
					"class": "form-control",
					"type": "text",
					"placeholder": "1",
					"id": "editprofile"
				}
			)
		}

	def clean(self):
		studentID = self.cleaned_data.get('studentID')
		if studentID == '':
			raise ValidationError('Please fill the fields.')
		if len(studentID) != 9:
			raise ValidationError('Please enter the correct format of Student ID: 2020xxxxx.')
		return studentID
	def clean(self):
		collegeID = self.cleaned_data.get('collegeID')
		if collegeID == default:
			raise ValidationError('Please enter a College')
		return collegeID

class FacultyForm(forms.ModelForm):
	class Meta:
		model = FacultyInfo
		fields = ('facultyID', 'collegeID',)

	def clean(self):
		facultyID = self.cleaned_data.get('facultyID')
		if len(facultyID) != 9:
			raise ValidationError('Please enter the correct format of faculty ID: 2020xxxxx.')
		return facultyID
	def clean(self):
		collegeID = self.cleaned_data.get('collegeID')
		if collegeID == default:
			raise ValidationError('Please enter a College')
		return collegeID

class studyPlanForm(forms.ModelForm):
	class Meta: 
		model = studyPlan
		fields = 'curricula',
		widgets = {
			'curricula': forms.Select(
				attrs={"class": "form-control","required":True}),
				}
