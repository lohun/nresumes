from flask import Blueprint, render_template, request, redirect
from .database import initialize, db
from html import unescape

cursor = initialize()

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/submitBasic', methods=["POST"])
def submitBasic():
    firstName = request.form.get("firstName")
    lastName = request.form.get("lastName")
    title = request.form.get("title")
    address = request.form.get("address")
    country = request.form.get("country")
    email = request.form.get("email")
    phoneNumber = request.form.get("phoneNumber")

    sql = "INSERT INTO users(first_name, last_name, title, address, country, email, phone_number) VALUES(%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (firstName, lastName, title, address, country, email, phoneNumber))

    db.commit()

    return redirect("/", 201)

@views.route('/submitExperience', methods=["POST"])
def submitExperience():
    company = request.form.get("company")
    companyAddress = request.form.get("companyAddress")
    title = request.form.get("title")
    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")
    description = request.form.get("description")

    sql = "INSERT INTO experience(user_id, company, company_address, job_title, start_date, end_date, description) VALUES(1, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (company, companyAddress, title, startDate, endDate, description))

    db.commit()
    return redirect("/", 201)


@views.route('/preview')
def preview():
    sql = "CALL firstGroupOfInfo(1)"
    cursor.execute(sql)
    result = cursor.fetchall()
    template = open(result[0]['template'], "r")
    preview = template.read()
    template = ""
    experienceTemplate = result[0]['experience_template']
    experience_history = set()
    
    for row in result:
        temp_experience = row['experience'].replace("end_date", row['job_date'])
        temp_experience = temp_experience.replace("start_date", row['job_start'])
        temp_experience = temp_experience.replace("company", row['company'])
        temp_experience = temp_experience.replace("role", row['job_title'])
        temp_experience = temp_experience.replace("role_description", row['job_description'])
        experience_history.add(temp_experience)
        
    experience_string = ""
    for row in experience_history:
        experience_string = experience_string + row
    experienceTemplate = experienceTemplate.replace('employment_history', experience_string)
    
    preview = preview.replace("info", experienceTemplate)
    
    return render_template('preview.html', info = preview)

@views.route('/update', methods = ['POST'])
def update():
    pass

@views.route('/download')
def download():
    return render_template('download.html')

