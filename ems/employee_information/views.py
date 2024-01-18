from django.shortcuts import redirect, render
from django.http import HttpResponse
from employee_information.models import Department, Position, Employees
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import json



#for resume parser
import fitz
import io
from PIL import Image
import os
import re
from pikepdf import Pdf, PdfImage
from pdfminer.high_level import extract_text
import cv2
import csv
import pickle
from docx2pdf import convert
import matplotlib.image as img
from os.path import exists
import pandas as pd
from pyresparser import ResumeParser
import matplotlib.pyplot as plt
import docx2txt
import csv
from pptx import Presentation
from pptx.util import Inches
from pathlib import Path
from PIL import Image
import numpy as np
import matplotlib.image as plt
from pyresparser import ResumeParser


#for job recomendation
from docx import Document
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from ftfy import fix_text
from sklearn.feature_extraction.text import TfidfVectorizer

employees = [

    {
        'code':1,
        'name':"John D Smith",
        'contact':'09123456789',
        'address':'Sample Address only'
    },{
        'code':2,
        'name':"Claire C Blake",
        'contact':'09456123789',
        'address':'Sample Address2 only'
    }

]
# Login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.
@login_required
def home(request):
    context = {
        'page_title':'Home',
        'employees':employees,
        'total_department':len(Department.objects.all()),
        'total_position':len(Position.objects.all()),
        'total_employee':len(Employees.objects.all()),
    }
    return render(request, 'employee_information/home.html',context)


#upload pdf here
def pdfupload(request):
    if request.method == 'POST':
        pdf_file = request.FILES['pdf_file']
        # Save the uploaded file to disk
        with open('uploaded_files/' + pdf_file.name, 'wb') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        return HttpResponse('File uploaded successfully.')
    else:
        return render(request, 'employee_information/resume_upload.html')


# def pdfupload(request):
#     if request.method == 'POST':
#         resumes_in_directory = []
#         resumes_in_directory = request.FILES['pdf_file']
#         result = final(resumes_in_directory)
#         print(result)
#         # Do something with the result
#         return HttpResponse('File uploaded successfully.')
#     else:
#         return render(request, 'employee_information/resume_upload.html')


def parser(request):
    # if request.method == 'POST':
        path = 'uploaded_files'
        os.chdir(path)

        resumes_in_directory = []

        for file in os.listdir():
            if file.endswith(".pdf"):
                resume_path = f"{path}\{file}"
                resumes_in_directory.append(resume_path)
                filename = file
                example = Pdf.open(filename)

        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)
        email = []
        regular_expression_for_email = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
        for i in resumes_in_directory:
            if i.endswith(".pdf"):
                text = extract_text(i)
            if i.endswith(".docx"):
                text = extract_text_from_docx(i)
            emails = re.findall(regular_expression_for_email, text)

            if emails:
                email.append(emails[0])
            else:
                email.append('NA')


        phone_numbers = []
        for i in resumes_in_directory:

            if i.endswith(".pdf"):
                text = extract_text(i)
            if i.endswith(".docx"):
                text = extract_text_from_docx(i)

            numbers = re.findall('[(+]*\d{0,3}[)]*[\d ]+[ \-\d]{9,}', text)
            temp = [number for number in numbers if len(number.strip().replace(" ", "")) > 9]  # List comprehension
            if temp:
                no = temp[0]
                if no.__contains__('-'):
                    no = no.replace('-', ' ')
                phone_numbers.append(no.strip())
            else:
                phone_numbers.append('NA')

        github_links = []

        for i in resumes_in_directory:
            if i.endswith(".pdf"):
                resume_text = extract_text(i)
            if i.endswith(".docx"):
                resume_text = extract_text_from_docx(i)

            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            url = re.findall(regex, resume_text.strip().replace(" ", ""))
            flag1 = 0
            flag2 = 0
            if url:
                temp = []
                for count in range(len(url)):
                    if re.search('github', url[count][0]):
                        temp.append(url[count][0])
                for z in temp:
                    if 'https:' in z and z.count('/') == 3:
                        flag1 = 1
                        while z.__contains__('|'):
                            z = z.replace('|', '')
                        github_links.append(z)
                    else:
                        if z.count('/') == 2:
                            flag1 = 1
                            while z.__contains__('|'):
                                z = z.replace('|', '')
                            github_links.append(z)
                if (flag1 == 0):
                    github_links.append('NA')

            else:
                github_links.append('NA')

        linkedin_links = []
        for i in resumes_in_directory:

            if i.endswith(".pdf"):
                resume_text = extract_text(i)

            if i.endswith(".docx"):
                resume_text = extract_text_from_docx(i)

            regex = r"https://[a-z]{2,3}[.]linkedin[.]com/.*[\n]{0,1}[a-z]*"
            r2 = r"www[.]linkedin[.]com/.*[\n]{0,1}[\s]*[A-Za-z0-9]*[\-]*[A-Za-z0-9]*[\-]*[0-9]*"
            url = re.findall(regex, resume_text)

            if url:
                if url[0].__contains__('|'):
                    t = url[0].split('|')
                    url[0] = t[0]
                if url[0].__contains__('\n'):
                    url[0] = url[0].replace('\n', '')

                linkedin_links.append(url[0].split(' ')[0])
            else:
                url = re.findall(r2, resume_text)
                if url:
                    if url[0].__contains__('|'):
                        t = url[0].split('|')
                        url[0] = t[0]
                    if url[0].__contains__('\n'):
                        url[0] = url[0].replace('\n', '')

                    linkedin_links.append(url[0].split(' ')[0])
                else:
                    linkedin_links.append('NA')

        education_info = []
        for i in resumes_in_directory:
            f = 0

            if i.endswith(".pdf") or i.endswith(".docx"):
                extracted_data = ResumeParser(i).get_extracted_data()
                edu_list = extracted_data['degree']
                if edu_list == None:
                    education_info.append('NA')
                elif len(edu_list) == 1:
                    edu_list[0] = re.sub('\n', '', edu_list[0])
                    education_info.append(edu_list[0])
                else:
                    ed = ''
                    for deg in range(len(edu_list)):
                        if edu_list[deg].__contains__('\n'):
                            edu_list[deg] = edu_list[deg].replace('\n', '')

                        #                 deg = re.sub('\n','',deg)

                        if edu_list[deg].__contains__('@') or edu_list[deg].__contains__('.com') or edu_list[
                            deg].__contains__('B I R T H'):
                            edu_list[deg] = ''

                        ed = ed + edu_list[deg] + ', '

                    ed = re.sub(r".$", "", ed)
                    ed = re.sub(r".$", "", ed)

                    if not ed.__contains__('('):
                        ed = ed.replace(')', '')
                    if not ed.__contains__(')'):
                        ed = ed.replace('(', '')
                    ed = ed.strip(' ,;')
                    education_info.append(ed)
        name=[]
        skills=[]
        experience=[]
        for i in resumes_in_directory:
            data = ResumeParser(i).get_extracted_data()
            for k,v in data.items():
                if k=='name':
                    name.append(v)
                if k=='skills':
                    skills.append(v)
                if k=='experience':
                    experience.append(v)

        context = {
            'email':email,
            'phone_numbers':phone_numbers,
            'github_links':github_links,
            'linkedin_links':linkedin_links,
            'education_info':education_info,
            'skills':skills,
            'name':name,
            'experience':experience,
        }
        return render(request,'employee_information/parser.html', context)
    # return render(request, "employee_information/parser.html")



def recommend(request):
    stopw = set(stopwords.words('english'))
    df = pd.read_csv('job_final.csv')
    df['test'] = df['Job_Description'].apply(
        lambda x: ' '.join([word for word in str(x).split() if len(word) > 2 and word not in (stopw)]))

    #
    path = 'uploaded_files'
    os.chdir(path)

    resumes_in_directory = []

    for file in os.listdir():
        if file.endswith(".pdf"):
            resume_path = f"{path}\{file}"
            resumes_in_directory.append(resume_path)
            filename = file
            example = Pdf.open(filename)

    path_parent = os.path.dirname(os.getcwd())
    os.chdir(path_parent)
    for i in resumes_in_directory:
        try:
            doc = Document()
            with open(i, 'r') as file:
                doc.add_paragraph(file.read())
            doc.save("text.docx")
            data1 = ResumeParser('text.docx').get_extracted_data()

        except:
            data1 = ResumeParser(i).get_extracted_data()

        resume = data1['skills']
        skills = []
        skills.append(' '.join(word for word in resume))

        def ngrams(string, n=3):
            string = fix_text(string)  # fix text
            string = string.encode("ascii", errors="ignore").decode()  # remove non ascii chars
            string = string.lower()
            chars_to_remove = [")", "(", ".", "|", "[", "]", "{", "}", "'"]
            rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
            string = re.sub(rx, '', string)
            string = string.replace('&', 'and')
            string = string.replace(',', ' ')
            string = string.replace('-', ' ')
            string = string.title()  # normalise case - capital at start of each word
            string = re.sub(' +', ' ', string).strip()  # get rid of multiple spaces and replace with a single
            string = ' ' + string + ' '  # pad names for ngrams...
            string = re.sub(r'[,-./]|\sBD', r'', string)
            ngrams = zip(*[string[i:] for i in range(n)])
            return [''.join(ngram) for ngram in ngrams]



        vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams, lowercase=False)
        tfidf = vectorizer.fit_transform(skills)
        from sklearn.neighbors import NearestNeighbors
        nbrs = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(tfidf)
        test = (df['test'].values.astype('U'))

        def getNearestN(query):
            queryTFIDF_ = vectorizer.transform(query)
            distances, indices = nbrs.kneighbors(queryTFIDF_)
            return distances, indices

        distances, indices = getNearestN(test)
        test = list(test)
        matches = []
        for i, j in enumerate(indices):
            dist = round(distances[i][0], 2)

            temp = [dist]
            matches.append(temp)

        matches = pd.DataFrame(matches, columns=['Match confidence'])
        df['match'] = matches['Match confidence']
        df1 = df.sort_values('match')
        last_df = df1[['Position', 'Company', 'Location']].head(10).reset_index()
        last_df.drop('index',axis=1,inplace=True)
        # final_df = last_df.to_html(classes="table table-striped")
        context = {"final_df":last_df}
    return render(request,"employee_information/recommendation.html", context)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'employee_information/about.html',context)

# Departments
@login_required
def departments(request):
    department_list = Department.objects.all()
    context = {
        'page_title':'Departments',
        'departments':department_list,
    }
    return render(request, 'employee_information/departments.html',context)
@login_required
def manage_departments(request):
    department = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            department = Department.objects.filter(id=id).first()
    
    context = {
        'department' : department
    }
    return render(request, 'employee_information/manage_department.html',context)

@login_required
def save_department(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_department = Department.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_department = Department(name=data['name'], description = data['description'],status = data['status'])
            save_department.save()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_department(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Department.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Positions
@login_required
def positions(request):
    position_list = Position.objects.all()
    context = {
        'page_title':'Positions',
        'positions':position_list,
    }
    return render(request, 'employee_information/positions.html',context)
@login_required
def manage_positions(request):
    position = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            position = Position.objects.filter(id=id).first()
    
    context = {
        'position' : position
    }
    return render(request, 'employee_information/manage_position.html',context)

@login_required
def save_position(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_position = Position.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_position = Position(name=data['name'], description = data['description'],status = data['status'])
            save_position.save()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_position(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Position.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
# Employees
def employees(request):
    employee_list = Employees.objects.all()
    context = {
        'page_title':'Employees',
        'employees':employee_list,
    }
    return render(request, 'employee_information/employees.html',context)
@login_required
def manage_employees(request):
    employee = {}
    departments = Department.objects.filter(status = 1).all() 
    positions = Position.objects.filter(status = 1).all() 
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            employee = Employees.objects.filter(id=id).first()
    context = {
        'employee' : employee,
        'departments' : departments,
        'positions' : positions
    }
    return render(request, 'employee_information/manage_employee.html',context)

@login_required
def save_employee(request):
    data =  request.POST
    resp = {'status':'failed'}
    if (data['id']).isnumeric() and int(data['id']) > 0:
        check  = Employees.objects.exclude(id = data['id']).filter(code = data['code'])
    else:
        check  = Employees.objects.filter(code = data['code'])

    if len(check) > 0:
        resp['status'] = 'failed'
        resp['msg'] = 'Code Already Exists'
    else:
        try:
            dept = Department.objects.filter(id=data['department_id']).first()
            pos = Position.objects.filter(id=data['position_id']).first()
            if (data['id']).isnumeric() and int(data['id']) > 0 :
                save_employee = Employees.objects.filter(id = data['id']).update(code=data['code'], firstname = data['firstname'],middlename = data['middlename'],lastname = data['lastname'],dob = data['dob'],gender = data['gender'],contact = data['contact'],email = data['email'],address = data['address'],department_id = dept,position_id = pos,date_hired = data['date_hired'],salary = data['salary'],status = data['status'])
            else:
                save_employee = Employees(code=data['code'], firstname = data['firstname'],middlename = data['middlename'],lastname = data['lastname'],dob = data['dob'],gender = data['gender'],contact = data['contact'],email = data['email'],address = data['address'],department_id = dept,position_id = pos,date_hired = data['date_hired'],salary = data['salary'],status = data['status'])
                save_employee.save()
            resp['status'] = 'success'
        except Exception:
            resp['status'] = 'failed'
            print(Exception)
            print(json.dumps({"code":data['code'], "firstname" : data['firstname'],"middlename" : data['middlename'],"lastname" : data['lastname'],"dob" : data['dob'],"gender" : data['gender'],"contact" : data['contact'],"email" : data['email'],"address" : data['address'],"department_id" : data['department_id'],"position_id" : data['position_id'],"date_hired" : data['date_hired'],"salary" : data['salary'],"status" : data['status']}))
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_employee(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Employees.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_employee(request):
    employee = {}
    departments = Department.objects.filter(status = 1).all() 
    positions = Position.objects.filter(status = 1).all() 
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            employee = Employees.objects.filter(id=id).first()
    context = {
        'employee' : employee,
        'departments' : departments,
        'positions' : positions
    }
    return render(request, 'employee_information/view_employee.html',context)