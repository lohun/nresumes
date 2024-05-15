from ast import If
from crypt import methods
from datetime import date, timedelta
import datetime
import email
import json
import os
from random import randint
import bcrypt
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user, login_required, login_user, logout_user
from .database import db
from .model import User
from website import login_manager
from weasyprint import HTML, CSS
from werkzeug.utils import secure_filename
import pathlib


UPLOAD_FOLDER = '/website/static/build/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)




views = Blueprint('views', __name__)

collection = db["user"]


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        password = bytes(password, "utf-8")
        
        
        user = collection.find_one({"email": email})
        if user != None or user != {}:
            hashed_password = user['password']
            
            if bcrypt.checkpw(password, hashed_password):
                user = User(user=user, active=True, anonymous=False, authenticated=True)
                login_user(user, remember=True, duration=timedelta(days=365))
                flash("Login successful")
                
                return redirect('/summary')
            else:
                flash('login unsuccessful')
        else:
            flash('login unsuccessful')
        
    return render_template('login.html')

@views.route('/summary')
@login_required
def home():
    user = current_user
    return render_template("profile.html", user=user)

@views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user
    if request.method == "POST":
        _id = user.id
        title = request.form.get("title")
        lastName = request.form.get("last_name")
        firstName = request.form.get("first_name")
        phone = request.form.get("phone_number")
        address = request.form.get("address")
        country = request.form.get("country")
        summary = request.form.get("summary")
        
        collection.update_one( 
            { "_id" : ObjectId(_id) },
            { "$set": { 
                "title": title,
                "first_name": firstName,
                "last_name": lastName,
                "address": address,
                "country": country,
                "summary": summary,
                "phone_number": phone
            }}
        )
        return redirect("/profile")
    return render_template("user_profile.html", user=user)

@views.route('/register', methods=['GET',"POST"])
def register():
    if request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        title = request.form.get("title")
        dob = request.form.get("dob")
        address = request.form.get("address")
        country = request.form.get("country")
        email = request.form.get("email")
        phoneNumber = request.form.get("phoneNumber")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        
        templates = db['template']
        templates = templates.find({})
        template = templates[0]
        
        if(password != confirmPassword):
            flash("Password does not match")
            return redirect("/register")
        password = bytes(password, "utf-8")
        password = bcrypt.hashpw(password, salt=bcrypt.gensalt())

        data = {
            "_id": ObjectId(),
            "title": title,
            "first_name": firstName,
            "last_name": lastName,
            "address": address,
            "country": country,
            "date_of_birth": dob,
            "email": email,
            "email_bool": True,
            "linkedin_bool": False,
            "phone_bool": True,
            "twitter_bool": False,
            "instagram_bool": False,
            "youtube_bool": False,
            "tiktok_bool": False,
            "github_bool": False,
            "personal_bool": False,
            "phone_number": phoneNumber,
            "summary": "",
            "template": template['_id'],
            "password": password,
            "education": [],
            "certifications": [],
            "socials": [],
            "experience": [],
            "projects": [],
            "skills": [],
            "volunteer": [],
            "interests": [],
            "extra": [],
            "builds": []
        }
        
        collection.insert_one(data)

        return redirect("/login")
    return render_template("register.html")


@views.route("/edituser", methods=["POST"])
def edituser():
    _id = current_user.id
    title = request.form.get("title")
    lastName = request.form.get("last_name")
    firstName = request.form.get("first_name")
    phone = request.form.get("phone_number")
    address = request.form.get("address")
    country = request.form.get("country")
    summary = request.form.get("summary")
    
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { "$set": { 
            "title": title,
            "first_name": firstName,
            "last_name": lastName,
            "address": address,
            "country": country,
            "summary": summary,
            "phone_number": phone
        }}
    )
    return redirect("/build")

@views.route('/experience')
@login_required
def experience():
    experience = current_user.experience
    return render_template("experience.html", user=current_user, experience = experience)

@views.route('/editExperience', methods=["POST"])
@login_required
def editExperience():
    _id = current_user.id
    id = request.form.get("id")
    company = request.form.get("company")
    title = request.form.get("title")
    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")
    description = request.form.get("description")
    collection.update_one( 
        { "_id" : ObjectId(_id), "experience._id": ObjectId(id) },
        { "$set": { 
            "experience.$.role": title, 
            "experience.$.company": company, 
            "experience.$.date_started": startDate, 
            "experience.$.date_ended": endDate, 
            "experience.$.description": description
            }
        }
    )
    return redirect("/experience")
    
@views.route('/submitExperience', methods=["POST"])
@login_required
def submitExperience():
    company = request.form.get("company")
    title = request.form.get("title")
    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")
    description = request.form.get("description")
    id = current_user.id

    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "experience": {
                "_id": ObjectId(),
                "company": company,
                "role": title,
                "description": description,
                "date_started": startDate,
                "date_ended": endDate
            } } 
         }
    )
    return redirect("/experience")

@views.route('/education')
@login_required
def education():
    education = current_user.education
    return render_template("education.html", user=current_user, education = education)

@views.route('/editEducation', methods=["POST"])
@login_required
def editEducation():
    _id = current_user.id
    id = request.form.get("id")
    school = request.form.get("school")
    award = request.form.get("award")
    department = request.form.get("department")
    faculty = request.form.get("faculty")
    achievments = request.form.get("achievments")
    date_started = request.form.get("date_started")
    date_ended = request.form.get("date_ended")
    collection.update_one( 
        { "_id" : ObjectId(_id), "education._id": ObjectId(id) },
        { "$set": { 
            "education.$.school": school, 
            "education.$.award": award, 
            "education.$.department": department, 
            "education.$.faculty": faculty, 
            "education.$.achivements": achievments, 
            "education.$.date_started": date_started, 
            "education.$.date_ended": date_ended,
        }}
    )
    return redirect("/education")

@views.route('/submitEducation', methods=["POST"])
@login_required
def submitEducation():
    school = request.form.get("school")
    award = request.form.get("award")
    department = request.form.get("department")
    faculty = request.form.get("faculty")
    achievments = request.form.get("achievments")
    date_started = request.form.get("date_started")
    date_ended = request.form.get("date_ended")
    
    id = current_user.id

    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "education": {
                "_id": ObjectId(),
                "school": school,
                "award": award,
                "department": department,
                "faculty": faculty,
                "achievements": achievments,
                "date_started": date_started,
                "date_ended": date_ended
            } } 
         }
    )
    return redirect("/education")

@views.route('/certification')
@login_required
def certification():
    certification = current_user.certifications
    return render_template("certification.html", user=current_user, certification = certification)

@views.route('/editCertification', methods=["POST"])
@login_required
def editCertification():
    _id = current_user.id
    id = request.form.get("id")
    name = request.form.get("name")
    organization = request.form.get("organization")
    certification_date = request.form.get("date")
    
    collection.update_one( 
        { "_id" : ObjectId(_id), "certifications._id": ObjectId(id) },
        { "$set": { 
            "certifications.$.name": name, 
            "certifications.$.organization": organization, 
            "certifications.$.date": certification_date
        }}
    )
    return redirect("/certification")

@views.route('/submitCertification', methods=["POST"])
@login_required
def submitCertification():
    name = request.form.get("name")
    organization = request.form.get("organization")
    certification_date = request.form.get("date")
    
    id = current_user.id

    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "certifications": {
                "_id": ObjectId(),
                "name": name,
                "organization": organization,
                "date": certification_date
            } } 
         }
    )
    return redirect("/certification")


@views.route('/submitSocial', methods=["POST"])
@login_required
def submitSocial():
    social_type = request.form.get("type")
    link = request.form.get("link")
    
    id = current_user.id

    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "socials": {
                "_id": ObjectId(),
                "type": social_type,
                "link": link
            } } 
         }
    )
    return redirect("/socials")

@views.route('/socials')
@login_required
def socials():
    user = current_user.socials
    return render_template("socials.html", user=current_user, socials=user)

@views.route('/editSocial', methods=["POST"])
@login_required
def editSocial():
    _id = current_user.id
    id = request.form.get("id")
    social_type = request.form.get("type")
    link = request.form.get("link")
    
    collection.update_one( 
        { "_id" : ObjectId(_id), "socials._id": ObjectId(id) },
        { "$set": { 
            "socials.$.type": social_type, 
            "socials.$.link": link
        }}
    )
    return redirect("/socials")

@views.route('/projects')
@login_required
def project():
    project = current_user.projects
    return render_template("projects.html", user=current_user, project = project)

@views.route('/editProject', methods=["POST"])
@login_required
def editProject():
    _id = current_user.id
    id = request.form.get("id")
    name = request.form.get("name")
    link = request.form.get("link")
    description = request.form.get("description")
    date_started = request.form.get("date_started")
    date_ended = request.form.get("date_ended")
    
    collection.update_one( 
        { "_id" : ObjectId(_id), "projects._id": ObjectId(id) },
        { "$set": { 
            "projects.$.name": name, 
            "projects.$.link": link, 
            "projects.$.description": description,
            "projects.$.date_started": date_started,
            "projects.$.date_ended": date_ended
        }}
    )
    return redirect("/projects")

@views.route('/submitProject', methods=["POST"])
@login_required
def submitProject():
    name = request.form.get("name")
    link = request.form.get("link")
    description = request.form.get("description")
    date_started = request.form.get("date_started")
    date_ended = request.form.get("date_ended")
    id = current_user.id
    
    collection.update_one(
        { "_id" : ObjectId(id) },
        { "$push": { "projects": {
                "_id": ObjectId(),
                "name": name,
                "link": link,
                "description": description,
                "date_started": date_started,
                "date_ended": date_ended
            } } 
         }
    )
    return redirect("/projects")

@views.route('/skills')
@login_required
def skills():
    skills = current_user.skills
    return render_template("skills.html", user=current_user, skills = skills)

@views.route('/editSkills', methods=["POST"])
@login_required
def editSkills():
    _id = current_user.id
    id = request.form.get("id")
    name = request.form.get("name")
    
    collection.update_one( 
        { "_id" : ObjectId(_id), "skills._id": ObjectId(id) },
        { "$set": { 
            "skills.$.name": name
        }}
    )
    return redirect("/skills")

@views.route('/submitSkills', methods=["POST"])
@login_required
def submitSkills():
    name = request.form.get("name")
    
    id = current_user.id

    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "skills": {
                "_id": ObjectId(),
                "name": name,
            } } 
         }
    )
    return redirect("/skills")

@views.route('/volunteer')
@login_required
def volunteer():
    volunteer = current_user.volunteer
    return render_template("volunteer.html", user=current_user, volunteer = volunteer)

@views.route('/editVolunteer', methods=["POST"])
@login_required
def editVolunteer():
    _id = current_user.id
    id = request.form.get("id")
    organization = request.form.get("organization")
    role = request.form.get("role")
    date_started = request.form.get("date_started")
    date_ended = request.form.get("date_ended")
    
    collection.update_one( 
        { "_id" : ObjectId(_id), "volunteer._id": ObjectId(id) },
        { "$set": { 
            "volunteer.$.organization": organization,
            "volunteer.$.role": role,
            "volunteer.$.date_started": date_started,
            "volunteer.$.date_ended": date_ended
        }}
    )
    return redirect("/volunteer")

@views.route('/submitVolunteer', methods=["POST"])
@login_required
def submitVolunteer():
    organization = request.form.get("organization")
    role = request.form.get("role")
    date_started = request.form.get("date_started")
    date_ended = request.form.get("date_ended")
    
    id = current_user.id

    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "volunteer": {
                "_id": ObjectId(),
                "organization": organization,
                "role": role,
                "date_started": date_started,
                "date_ended": date_ended
            } } 
         }
    )
    return redirect("/volunteer")

@views.route('/interests')
@login_required
def interests():
    interest = current_user.interests
    return render_template("interests.html", user=current_user, interest = interest)

@views.route('/editInterests', methods=["POST"])
@login_required
def editInterests():
    _id = current_user.id
    id = request.form.get("id")
    name = request.form.get("name")
    
    collection.update_one( 
        { "_id" : ObjectId(_id), "interests._id": ObjectId(id) },
        { "$set": { 
            "interests.$.name": name
        }}
    )
    return redirect("/interests")

@views.route('/submitInterests', methods=["POST"])
@login_required
def submitInterests():
    name = request.form.get("name")
    
    id = current_user.id

    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "interests": {
                "_id": ObjectId(),
                "name": name
            } } 
         }
    )
    return redirect("/interests")

@views.route('/extra')
@login_required
def extra():
    extra = current_user.extra
    return render_template("extra.html", user=current_user, extra = extra)

@views.route('/editExtra', methods=["POST"])
@login_required
def editExtra():
    _id = current_user.id
    id = request.form.get("id")
    title = request.form.get("title")
    description = request.form.get("description")
    
    collection.update_one( 
        { "_id" : ObjectId(_id), "extra._id": ObjectId(id) },
        { "$set": { "extra.$.title": title, "extra.$.description": description}}
    )
    return redirect("/extra")

@views.route('/submitExtra', methods=["POST"])
@login_required
def submitExtra():
    title = request.form.get("title")
    description = request.form.get("description")    
    id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "extra": {
                "_id": ObjectId(),
                "title": title,
                "description": description
            } } 
         }
    )
    return redirect("/extra")


@views.route("/socialsallowed", methods=["POST"])
@login_required
def socialsallowed():
    id = current_user.id
    personal_bool = request.form.get('personal_bool')
    email_bool = request.form.get('email_bool')
    linkedin_bool = request.form.get('linkedin_bool')
    phone_bool = request.form.get('phone_bool')
    twitter_bool = request.form.get('twitter_bool')
    instagram_bool = request.form.get('instagram_bool')
    youtube_bool = request.form.get('youtube_bool')
    tiktok_bool = request.form.get('tiktok_bool')
    github_bool = request.form.get('github_bool')
    collection.update_one( 
        { "_id" : id },
        { "$set": { "email_bool": email_bool,
            "linkedin_bool": linkedin_bool,
            "phone_bool": phone_bool,
            "twitter_bool": twitter_bool,
            "instagram_bool": instagram_bool,
            "youtube_bool": youtube_bool,
            "tiktok_bool": tiktok_bool,
            "github_bool": github_bool,
            "personal_bool": personal_bool,
            } } 
    )
    return redirect("/build")


@views.route('/build')
@login_required
def preview():
    if not current_user.is_authenticated():
        redirect("/login")
    
    user = current_user
    template = user.template
    templates_collection = db.template
    template = templates_collection.find_one({"_id": ObjectId(template)})
    preview = open(template['location'], "r").read()
    experienceTemplate = template['experience_template']
    certificationsTemplate = template['certifications_template']
    educationTemplate = template['education_template']
    projectsTemplate = template['projects_template']
    skillsTemplate = template['skills_template']
    volunteerTemplate = template['volunteering_template']
    interestsTemplate = template['interests_template']
    extraTemplate = template['extra_template']
    experience_history = ""
    education_history = ""
    socials_history = ""
    projects_history = ""
    certifications_history = ""
    skills_history = ""
    volunteer_history = ""
    interests_history = ""
    extra_history = ""
    basic_info = ""
    preview = preview.replace("{{title}}", f"{user.title}")
    preview = preview.replace("{{fullname}}", f"{user.last_name} {user.first_name}")
    
    if user.email_bool == "on":
        temp = template['basic']
        basic_info = basic_info + temp.replace("{{basic}}", f"{user.email}")
        
    if user.address_bool == "on":
        temp = template['basic']
        basic_info = basic_info + temp.replace("{{basic}}", f"{user.address}")
    
    if user.phone_bool == "on":
        temp = template['basic']
        basic_info = basic_info + temp.replace("{{basic}}", f"{user.phone_number}")
    
    for row in user.experience:
        print(row)
        temp_experience = template["experience"]
        temp_experience = temp_experience.replace("{{end_date}}", row["date_ended"])
        temp_experience = temp_experience.replace("{{start_date}}", row['date_started'])
        temp_experience = temp_experience.replace("{{company}}", row['company'])
        temp_experience = temp_experience.replace("{{role}}", row['role'])
        temp_experience = temp_experience.replace("{{role_description}}", row['description'])
        experience_history = experience_history + temp_experience
        
    for row in user.education:
        temp_education = template["education"]
        temp_education = temp_education.replace("{{school}}", row['school'])
        temp_education = temp_education.replace("{{award}}", row['award'])
        temp_education = temp_education.replace("{{department}}", row['department'])
        temp_education = temp_education.replace("{{faculty}}", row['faculty'])
        temp_education = temp_education.replace("{{achievements}}", row['achievements']or "")
        temp_education = temp_education.replace("{{date_started}}", row['date_started'])
        temp_education = temp_education.replace("{{date_ended}}", row['date_ended'])
        education_history = education_history + temp_education
        
    for row in user.projects:
        temp_projects = template["projects"]
        temp_projects = temp_projects.replace("{{name}}", row['name'])
        temp_projects = temp_projects.replace("{{link}}", row['link'])
        temp_projects = temp_projects.replace("{{description}}", row['description'])
        temp_projects = temp_projects.replace("{{date_started}}", row['date_started'])
        temp_projects = temp_projects.replace("{{date_ended}}", row['date_ended'])
        projects_history = projects_history + temp_projects
        
    for row in user.certifications:
        temp_certifications = template["certification"]
        temp_certifications = temp_certifications.replace("{{name}}", row['name'])
        temp_certifications = temp_certifications.replace("{{organization}}", row['organization'])
        temp_certifications = temp_certifications.replace("{{date}}", row['date'])
        certifications_history = certifications_history + temp_certifications
        
    for row in user.skills:
        temp_skills = template["skills"]
        temp_skills = temp_skills.replace("{{name}}", row['name'])
        skills_history = skills_history + temp_skills
        
    for row in user.volunteer:
        temp_volunteer = template["volunteer"]
        temp_volunteer = temp_volunteer.replace("{{organization}}", row['organization'])
        temp_volunteer = temp_volunteer.replace("{{role}}", row['role'])
        temp_volunteer = temp_volunteer.replace("{{date_started}}", row['date_started'])
        temp_volunteer = temp_volunteer.replace("{{date_ended}}", row['date_ended'])
        volunteer_history = volunteer_history + temp_volunteer
        
    for row in user.interests:
        temp_interests = template["interests"]
        temp_interests = temp_interests.replace("{{name}}", row['name'])
        interests_history = interests_history + temp_interests
        
    for row in user.socials:
        temp_socials = template["socials"]
        try:
            social_type = f"{row['type']}_bool"
            if getattr(user, social_type) == "on":
                temp_socials = temp_socials.replace("{{type}}", row['type'])
                temp_socials = temp_socials.replace("{{link}}", row['link'])
            else:
                temp_socials = ""
        except AttributeError:
            temp_socials = ""
        socials_history = socials_history + temp_socials
        
    for row in user.extra:
        temp_extra = template["extra"]
        temp_extra = temp_extra.replace("{{title}}", row['title'])
        temp_extra = temp_extra.replace("{{description}}", row['description'])
        extra_history = extra_history + temp_extra
    if experience_history != "":
        experienceTemplate = experienceTemplate.replace('{{employment_history}}', experience_history)
    else:
        experienceTemplate = ""
        
    if education_history != "":
        educationTemplate = educationTemplate.replace('{{education_history}}', education_history)
    else:
        educationTemplate = ""
        
    if projects_history != "":
        projectsTemplate = projectsTemplate.replace('{{projects_history}}', projects_history)
    else:
        projectsTemplate = ""
    
    if skills_history != "":
        skillsTemplate = skillsTemplate.replace('{{skills_history}}', skills_history)
    else:
        skillsTemplate = ""
        
    if certifications_history != "":
        certificationsTemplate = certificationsTemplate.replace('{{certifications_history}}', certifications_history)
    else:
        certificationsTemplate = ""
        
    if volunteer_history != "":
        volunteerTemplate = volunteerTemplate.replace('{{volunteer_history}}', volunteer_history)
    else:
        volunteerTemplate = ""
        
    if interests_history != "":
        interestsTemplate = interestsTemplate.replace('{{interests_history}}', interests_history)
    else:
        interestsTemplate = ""
        
    if user.extra != []:
        extraTemplate = extraTemplate.replace('{{extra_history}}', extra_history)
    else:
        extraTemplate = ""
    
    complete_template = experience_history+ " " + educationTemplate+ " " + certificationsTemplate + " " + projectsTemplate+ " " + skillsTemplate+ " " + volunteerTemplate+ " " + interestsTemplate+ " " + extraTemplate+ " "
    
    basic_info = basic_info + socials_history
    preview = preview.replace("{{basic_info}}", basic_info)
    preview = preview.replace("{{info}}", complete_template)
    
    random_number = randint(0, 10000)
    filename = f"My Resume {random_number}"
    
    return render_template('preview.html', info = preview, user = user, filename = filename)

@views.route('/download', methods=["POST"])
@login_required
def download():
    filename = request.form.get("filename")
    default_name = request.form.get("default_name")
    if not current_user.is_authenticated():
        redirect("/login")
        
    if filename == None or filename == "":
        filename = default_name
    
    
    user = current_user
    id = user.id
    template = user.template
    templates_collection = db.template
    template = templates_collection.find_one({"_id": ObjectId(template)})
    preview = open(template['location'], "r").read()
    experienceTemplate = template['experience_template']
    certificationsTemplate = template['certifications_template']
    educationTemplate = template['education_template']
    projectsTemplate = template['projects_template']
    skillsTemplate = template['skills_template']
    volunteerTemplate = template['volunteering_template']
    interestsTemplate = template['interests_template']
    extraTemplate = template['extra_template']
    experience_history = ""
    education_history = ""
    socials_history = ""
    projects_history = ""
    certifications_history = ""
    skills_history = ""
    volunteer_history = ""
    interests_history = ""
    extra_history = ""
    basic_info = ""
    preview = preview.replace("{{title}}", f"{user.title}")
    preview = preview.replace("{{fullname}}", f"{user.last_name} {user.first_name}")
    
    if user.email_bool == "on":
        temp = template['basic']
        basic_info = basic_info + temp.replace("{{basic}}", f"{user.email}")
        
    if user.address_bool == "on":
        temp = template['basic']
        basic_info = basic_info + temp.replace("{{basic}}", f"{user.address}")
    
    if user.phone_bool == "on":
        temp = template['basic']
        basic_info = basic_info + temp.replace("{{basic}}", f"{user.phone_number}")
    
    for row in user.experience:
        print(row)
        temp_experience = template["experience"]
        temp_experience = temp_experience.replace("{{end_date}}", row["date_ended"])
        temp_experience = temp_experience.replace("{{start_date}}", row['date_started'])
        temp_experience = temp_experience.replace("{{company}}", row['company'])
        temp_experience = temp_experience.replace("{{role}}", row['role'])
        temp_experience = temp_experience.replace("{{role_description}}", row['description'])
        experience_history = experience_history + temp_experience
        
    for row in user.education:
        temp_education = template["education"]
        temp_education = temp_education.replace("{{school}}", row['school'])
        temp_education = temp_education.replace("{{award}}", row['award'])
        temp_education = temp_education.replace("{{department}}", row['department'])
        temp_education = temp_education.replace("{{faculty}}", row['faculty'])
        temp_education = temp_education.replace("{{achievements}}", row['achievements']or "")
        temp_education = temp_education.replace("{{date_started}}", row['date_started'])
        temp_education = temp_education.replace("{{date_ended}}", row['date_ended'])
        education_history = education_history + temp_education
        
    for row in user.projects:
        temp_projects = template["projects"]
        temp_projects = temp_projects.replace("{{name}}", row['name'])
        temp_projects = temp_projects.replace("{{link}}", row['link'])
        temp_projects = temp_projects.replace("{{description}}", row['description'])
        temp_projects = temp_projects.replace("{{date_started}}", row['date_started'])
        temp_projects = temp_projects.replace("{{date_ended}}", row['date_ended'])
        projects_history = projects_history + temp_projects
        
    for row in user.certifications:
        temp_certifications = template["certification"]
        temp_certifications = temp_certifications.replace("{{name}}", row['name'])
        temp_certifications = temp_certifications.replace("{{organization}}", row['organization'])
        temp_certifications = temp_certifications.replace("{{date}}", row['date'])
        certifications_history = certifications_history + temp_certifications
        
    for row in user.skills:
        temp_skills = template["skills"]
        temp_skills = temp_skills.replace("{{name}}", row['name'])
        skills_history = skills_history + temp_skills
        
    for row in user.volunteer:
        temp_volunteer = template["volunteer"]
        temp_volunteer = temp_volunteer.replace("{{organization}}", row['organization'])
        temp_volunteer = temp_volunteer.replace("{{role}}", row['role'])
        temp_volunteer = temp_volunteer.replace("{{date_started}}", row['date_started'])
        temp_volunteer = temp_volunteer.replace("{{date_ended}}", row['date_ended'])
        volunteer_history = volunteer_history + temp_volunteer
        
    for row in user.interests:
        temp_interests = template["interests"]
        temp_interests = temp_interests.replace("{{name}}", row['name'])
        interests_history = interests_history + temp_interests
        
    for row in user.socials:
        temp_socials = template["socials"]
        try:
            social_type = f"{row['type']}_bool"
            if getattr(user, social_type) == "on":
                temp_socials = temp_socials.replace("{{type}}", row['type'])
                temp_socials = temp_socials.replace("{{link}}", row['link'])
            else:
                temp_socials = ""
        except AttributeError:
            temp_socials = ""
        socials_history = socials_history + temp_socials
        
    for row in user.extra:
        temp_extra = template["extra"]
        temp_extra = temp_extra.replace("{{title}}", row['title'])
        temp_extra = temp_extra.replace("{{description}}", row['description'])
        extra_history = extra_history + temp_extra
    if experience_history != "":
        experienceTemplate = experienceTemplate.replace('{{employment_history}}', experience_history)
    else:
        experienceTemplate = ""
        
    if education_history != "":
        educationTemplate = educationTemplate.replace('{{education_history}}', education_history)
    else:
        educationTemplate = ""
        
    if projects_history != "":
        projectsTemplate = projectsTemplate.replace('{{projects_history}}', projects_history)
    else:
        projectsTemplate = ""
    
    if skills_history != "":
        skillsTemplate = skillsTemplate.replace('{{skills_history}}', skills_history)
    else:
        skillsTemplate = ""
        
    if certifications_history != "":
        certificationsTemplate = certificationsTemplate.replace('{{certifications_history}}', certifications_history)
    else:
        certificationsTemplate = ""
        
    if volunteer_history != "":
        volunteerTemplate = volunteerTemplate.replace('{{volunteer_history}}', volunteer_history)
    else:
        volunteerTemplate = ""
        
    if interests_history != "":
        interestsTemplate = interestsTemplate.replace('{{interests_history}}', interests_history)
    else:
        interestsTemplate = ""
        
    if user.extra != []:
        extraTemplate = extraTemplate.replace('{{extra_history}}', extra_history)
    else:
        extraTemplate = ""
    
    complete_template = experience_history+ " " + educationTemplate+ " " + certificationsTemplate + " " + projectsTemplate+ " " + skillsTemplate+ " " + volunteerTemplate+ " " + interestsTemplate+ " " + extraTemplate+ " "
    
    basic_info = basic_info + socials_history
    preview = preview.replace("{{basic_info}}", basic_info)
    preview = preview.replace("{{info}}", complete_template)
    
    html = HTML(string=preview)
    css = CSS(string='@page { size: A4; margin: 1cm }')
    path = pathlib.Path(f"website/static/build/{user.last_name} {user.first_name}")
    path.mkdir(parents=True, exist_ok=True)
    
    html.write_pdf(f'{path}/{filename}.pdf', stylesheets=[css])
    
    collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "builds": {
                "_id": ObjectId(),
                "path": f'build/{user.last_name} {user.first_name}/{filename}.pdf',
                "name": filename,
                "date": datetime.datetime.now()
            } } 
         }
    )
    return redirect("/builds")

@views.route('/builds')
@login_required
def builds():
    builds = current_user.builds
    return render_template("build.html", user=current_user, builds = builds)


@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/uploadfile', methods=["POST"])
@login_required
def upload():
    user = current_user
    _id = user.id
    path = pathlib.Path(f"website/static/build/{user.last_name} {user.first_name}/profile")
    path.mkdir(parents=True, exist_ok=True)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect("/profile")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(f"{path}/{filename}")
        collection.update_one( 
            { "_id" : ObjectId(_id) },
            { "$set": { "profile_picture": f"build/{user.last_name} {user.first_name}/profile/{filename}"}}
        )
        return redirect("/profile")

@views.route("/deleteEducation/<id>")
@login_required
def deleteEducation(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "education":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/education")

@views.route("/deleteExperience/<id>")
@login_required
def deleteExperience(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "experience":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/experience")

@views.route("/deleteCertification/<id>")
@login_required
def deleteCertification(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "certifications":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/certification")

@views.route("/deleteSocial/<id>")
@login_required
def deleteSocial(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "socials":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/socials")

@views.route("/deleteProject/<id>")
@login_required
def deleteProject(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "projects":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/projects")

@views.route("/deleteSkill/<id>")
@login_required
def deleteSkill(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "skills":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/skills")

@views.route("/deleteInterest/<id>")
@login_required
def deleteInterest(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "interests":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/interests")

@views.route("/deleteExtra/<id>")
@login_required
def deleteExtra(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "extra":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/extra")

@views.route("/deleteVolunteer/<id>")
@login_required
def deleteVolunteer(id):
    _id = current_user.id
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "volunteer":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/volunteer")

@views.route("/deleteBuilds/<id>")
@login_required
def deleteBuilds(id):
    user = current_user
    _id = current_user.id
    dirname = os.path.dirname(__file__)
    for row in user.builds:
        if row['_id'] == id:
            if os.path.exists(os.path.join(dirname, f"website/static/{row['path']}")):
                os.remove(os.path.join(dirname, f"website/static/{row['path']}"))
    collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "builds":{ "_id": ObjectId(id)}}
        }
    )
    return redirect("/builds")
    
    

