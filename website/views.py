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
    sql = "SELECT * FROM users u JOIN experience e ON u.id = e.user_id"
    cursor.execute(sql)
    result = cursor.fetchone()
    template = open("./resumetemplates/first.asp", "r")
    preview = template.read()
    preview = preview.replace("fullname", result[1] + " " + result[2])
    preview = preview.replace("address", "Surulere, Lagos")
    preview = preview.replace("email", result[6])
    preview = preview.replace("phone_number", result[7])
    preview = preview.replace("start_date", result[13])
    preview = preview.replace("end_date", result[14])
    preview = preview.replace("company", result[10])
    preview = preview.replace("role_description", result[15])
    print(preview)

    return render_template('preview.html', info = preview)

@views.route('/update', methods = ['POST'])
def update():
    pass

@views.route('/download')
def download():
    return render_template('download.html')

