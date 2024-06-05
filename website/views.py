from ast import If
from crypt import methods
from datetime import timedelta
import datetime
import json
import os
from random import randint
import bcrypt
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, flash, send_file, send_from_directory, url_for
from flask_login import current_user, login_required, login_user, logout_user
from .database import db
from .model import User
from website import login_manager
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from werkzeug.utils import secure_filename
import pathlib
import re


UPLOAD_FOLDER = '/website/static/build/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)




views = Blueprint('views', __name__)

collection = db["user"]

def validate(request_input, type="string"):
    request_input = request.form.get(request_input).strip()
    results = ""
    match type:
        case "string":
            if re.search(r"^[A-Za-z0-9\s]*.*$", request_input):
                results = request_input
            else:
                flash("Invalid input")
                return False
            
        case "number":
            if re.search(r"^[0-9]+$", request_input):
                results = request_input
            else:
                flash("Please input a valid email")
                return False
            
        case "email":
            regex_string = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if re.search(regex_string, request_input):
                results = request_input
            else:
                flash("Invalid input")
                return False
        
        case "date":
            if re.search(r"^\b\d\d?-\b\d\d?-\d\d\d\d\b$", request_input):
                results = request_input
            else:
                flash("Invalid input")
                return False
            
        case "month":
            if re.search(r"^[A-Za-z]{3}-\d\d\d\d\b$", request_input):
                results = request_input
            else:
                flash("Invalid input")
                return False
            
        case "password":
            if re.search(r"?=.*([A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", request_input):
                results = request_input
            else:
                flash("Please use a password of at leasrt 8 characters with and at least one number")
                return False
            
        case _:
            flash("Invalid input")
            return False
        
    return results


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@views.route("/")
def index():
    return render_template('landing.html')

@views.route("/about")
def about():
    return render_template("about.html")

@views.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == "POST":
        feedback_collection = db["feedback"]
        name = validate(request_input="name", type="string")
        email = validate(request_input="email", type="email")
        feedback = validate(request_input="feedback", type="string")
        
        if name == False or feedback==False:
            return redirect("/feedback")
        
        info = feedback_collection.insert_one({
            "_id": ObjectId(),
            "name": name,
            "email": email,
            "feedback": feedback
        })
        
        if info:
            flash("Thank you, your feedback has been submitted")
            return redirect("/feedback")
        else:
            flash("Feedback not gotten, there seems to be an error. Please try again.")
            return redirect("/feedback")
    return render_template("feedback.html")

@views.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/summary")
    
    if request.method == "POST":
        email = validate(request_input="email", type="email")
        password = validate(request_input="password", type="string")
        if email == False or password == False:
            return redirect("/login")
        password = bytes(password, "utf-8")
        
        
        user = collection.find_one({"email": email})
        if user != None or user != {}:
            hashed_password = user['password']
            
            if bcrypt.checkpw(password, hashed_password):
                user = User(user=user, active=True, anonymous=False, authenticated=True)
                login_user(user, remember=True, duration=timedelta(days=365))
                flash("Login successful")
                
                return redirect('/profile')
            else:
                flash('login unsuccessful')
        else:
            flash('login unsuccessful')
        
    return render_template('login.html')

@views.route('/summary')
@login_required
def home():
    return render_template("profile.html")

@views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user
    if request.method == "POST":
        _id = user.id
        title = validate(request_input="title", type="string")
        lastName = validate(request_input="last_name", type="string")
        firstName = validate(request_input="first_name", type="string")
        phone = validate(request_input="phone_number", type="string")
        address = validate(request_input="address", type="string")
        country = validate(request_input="country", type="string")
        
        if title == False or lastName == False or firstName == False or phone == False or address == False or country == False:
            return redirect("/profile")
        
        info = collection.update_one( 
            { "_id" : ObjectId(_id) },
            { "$set": { 
                "title": title,
                "first_name": firstName,
                "last_name": lastName,
                "address": address,
                "country": country,
                "phone_number": phone
            }}
        )
        if info:
            flash("Hey, your profile has been updated")
            return redirect("/profile")
        else:
            flash("Profile has not been updated, please try again.")
    return render_template("user_profile.html", user=user)

@views.route('/register', methods=['GET',"POST"])
def register():
    if current_user.is_authenticated:
        return redirect("/summary")
    
    if request.method == "POST":
        dob = validate(request_input="dob", type="string")
        email = validate(request_input="email", type="email")
        password = validate(request_input="password", type="password")
        confirmPassword = validate(request_input="confirmPassword", type="password")
        
        if dob == False or email == False or password == False or confirmPassword == False:
            return redirect("/register")
        
        templates = db['template']
        templates = templates.find({})
        template = templates[1]
        
        if(password != confirmPassword):
            flash("Password does not match")
            return redirect("/register")
        password = bytes(password, "utf-8")
        password = bcrypt.hashpw(password, salt=bcrypt.gensalt())

        data = {
            "_id": ObjectId(),
            "title": "",
            "first_name": "",
            "last_name": "",
            "address": "",
            "country": "",
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
            "address_bool": False,
            "phone_number": "",
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
        
        if collection.insert_one(data):
            flash("Welcome!! Welcome!! Please login and get started")
            return redirect("/login")
        else:
            flash("Please try again")
    return render_template("register.html")


@views.route("/edituser", methods=["POST"])
def edituser():
    _id = current_user.id
    title = validate(request_input="title", type="string")
    lastName = validate(request_input="last_name", type="string")
    firstName = validate(request_input="first_name", type="string")
    phone = validate(request_input="phone_number", type="number")
    address = validate(request_input="address", type="string")
    country = validate(request_input="country", type="string")
    
    if title == False or lastName == False or firstName == False or phone == False or title == False or address == False or country == False:
        return redirect("/build")
      
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { "$set": { 
            "title": title,
            "first_name": firstName,
            "last_name": lastName,
            "address": address,
            "country": country,
            "phone_number": phone
        }}
    )
    
    if info:
        flash("Hey, your profile has been updated")
        return redirect("/build")
    else:
        flash("Profile has not been updated, please try again.")
    return redirect("/build")

@views.route('/experience')
@login_required
def experience():
    return render_template("experience.html")

@views.route('/editExperience', methods=["POST"])
@login_required
def editExperience():
    _id = current_user.id
    id = validate(request_input="id", type="string")
    company = validate(request_input="company", type="string")
    title = validate(request_input="title", type="string")
    startDate = validate(request_input="startDate", type="text")
    endDate = validate(request_input="endDate", type="text")
    description = request.form.get("description").strip()
    
    if id == False or company == False or title == False or startDate == False or endDate == False:
        return redirect("/experience")
    
    info = collection.update_one( 
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
    if info:
        flash("Your experience has been updated")
        return redirect("/experience")
    else:
        flash("Your experience has not been updated, please try again.")
    return redirect("/experience")
    
@views.route('/submitExperience', methods=["POST"])
@login_required
def submitExperience():
    company = validate(request_input="company", type="string")
    title = validate(request_input="title", type="string")
    startDate = validate(request_input="startDate", type="text")
    endDate = validate(request_input="endDate", type="text")
    description = request.form.get("description").strip()
    
    if company == False or title == False or startDate == False or endDate == False:
        return redirect("/experience")
    
    id = current_user.id
    
    

    info = collection.update_one( 
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
    if info:
        flash("Expereince added")
        return redirect("/experience")
    else:
        flash("Info not added, please try again.")
    return redirect("/experience")

@views.route('/education')
@login_required
def education():
    return render_template("education.html")

@views.route('/editEducation', methods=["POST"])
@login_required
def editEducation():
    _id = current_user.id
    id = validate(request_input="id", type="string")
    school = validate(request_input="school", type="string")
    award = validate(request_input="award", type="string")
    department = validate(request_input="department", type="string")
    faculty = validate(request_input="faculty", type="string")
    achievments = validate(request_input="achievments", type="string")
    date_started = validate(request_input="date_started", type="text")
    date_ended = validate(request_input="date_ended", type="text")
    
    if id == False or school == False or award == False or department == False or faculty == False or achievments == False or date_started == False or date_ended == False:
        return redirect("/education")
    
    info = collection.update_one( 
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
    if info:
        flash("Education edited")
        return redirect("/education")
    else:
        flash("Info not edited, please try again.")
    return redirect("/education")

@views.route('/submitEducation', methods=["POST"])
@login_required
def submitEducation():
    school = validate(request_input="school", type="string")
    award = validate(request_input="award", type="string")
    department = validate(request_input="department", type="string")
    faculty = validate(request_input="faculty", type="string")
    achievments = validate(request_input="achievments", type="string")
    date_started = validate(request_input="date_started", type="text")
    date_ended = validate(request_input="date_ended", type="text")
    
    if school == False or award == False or department == False or faculty == False or achievments == False or date_started == False or date_ended == False:
        return redirect("/education")
    
    id = current_user.id

    info = collection.update_one( 
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
    if info:
        flash("Education added")
        return redirect("/education")
    else:
        flash("Info not added, please try again.")
    return redirect("/education")

@views.route('/certification')
@login_required
def certification():
    return render_template("certification.html")

@views.route('/editCertification', methods=["POST"])
@login_required
def editCertification():
    _id = current_user.id
    id = validate(request_input="id", type="string")
    name = validate(request_input="name", type="string")
    organization = validate(request_input="organization", type="string")
    certification_date = validate(request_input="date", type="text")
    
    if id == False or name == False or organization == False or certification_date == False:
        return redirect("/certification")
    
    
    info = collection.update_one( 
        { "_id" : ObjectId(_id), "certifications._id": ObjectId(id) },
        { "$set": { 
            "certifications.$.name": name, 
            "certifications.$.organization": organization, 
            "certifications.$.date": certification_date
        }}
    )
    
    if info:
        flash("Certification edited")
        return redirect("/certification")
    else:
        flash("Info not edited, please try again.")
    return 

@views.route('/submitCertification', methods=["POST"])
@login_required
def submitCertification():
    name = validate(request_input="name", type="string")
    organization = validate(request_input="organization", type="string")
    certification_date = validate(request_input="date", type="text")
    
    if name == False or organization == False or certification_date == False:
        return redirect("/certification")
    
    id = current_user.id

    info = collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "certifications": {
                "_id": ObjectId(),
                "name": name,
                "organization": organization,
                "date": certification_date
            } } 
         }
    )
    if info:
        flash("Certification submitted")
        return redirect("/certification")
    else:
        flash("Info not submitted, please try again.")
    return redirect("/certification")


@views.route('/submitSocial', methods=["POST"])
@login_required
def submitSocial():
    social_type = validate(request_input="type", type="string")
    link = validate(request_input="link", type="url")
    
    if social_type == False or link == False:
        return redirect("socials")
    
    id = current_user.id

    info = collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "socials": {
                "_id": ObjectId(),
                "type": social_type,
                "link": link
            } } 
         }
    )
    if info:
        flash("Social media submitted")
        return redirect("/socials")
    else:
        flash("Info not submitted, please try again.")
    return redirect("/socials")

@views.route('/socials')
@login_required
def socials():
    return render_template("socials.html")

@views.route('/editSocial', methods=["POST"])
@login_required
def editSocial():
    _id = current_user.id
    id = validate("id", type="string")
    social_type = validate(request_input="type", type="string")
    link = validate(request_input="link", type="url")
    
    if id == False or social_type == False or link == False:
        return redirect("socials")
    
    if social_type == False or link == False:
        return redirect("socials")
    
    info = collection.update_one( 
        { "_id" : ObjectId(_id), "socials._id": ObjectId(id) },
        { "$set": { 
            "socials.$.type": social_type, 
            "socials.$.link": link
        }}
    )
    
    if info:
        flash("Social media editted")
        return redirect("/socials")
    else:
        flash("Info not edited, please try again.")
    return redirect("/socials")

@views.route('/projects')
@login_required
def project():
    return render_template("projects.html")

@views.route('/editProject', methods=["POST"])
@login_required
def editProject():
    _id = current_user.id
    id = validate(request_input="id", type="string")
    name = validate(request_input="name", type="string")
    link = validate(request_input="link", type="url")
    description = request.form.get("description").strip()
    date_started = validate(request_input="date_started", type="text")
    date_ended = validate(request_input="date_ended", type="text")
    
    if id == False or name == False or link == False or date_started == False or date_ended == False:
        return redirect("/projects")
    
    info = collection.update_one( 
        { "_id" : ObjectId(_id), "projects._id": ObjectId(id) },
        { "$set": { 
            "projects.$.name": name, 
            "projects.$.link": link, 
            "projects.$.description": description,
            "projects.$.date_started": date_started,
            "projects.$.date_ended": date_ended
        }}
    )
    
    if info:
        flash("Project edited")
        return redirect("/projects")
    else:
        flash("Info not edited, please try again.")
    return redirect("/projects")

@views.route('/submitProject', methods=["POST"])
@login_required
def submitProject():
    name = validate(request_input="name", type="string")
    link = validate(request_input="link", type="url")
    description = request.form.get("description").strip()
    date_started = validate(request_input="date_started", type="text")
    date_ended = validate(request_input="date_ended", type="text")
    id = current_user.id
    
    if name == False or link == False or date_started == False or date_ended == False:
        return redirect("/projects")
    
    info = collection.update_one(
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
    
    if info:
        flash("Project submitted")
        return redirect("/projects")
    else:
        flash("Info not submitted, please try again.")
    return redirect("/prskillsojects")

@views.route('/skills')
@login_required
def skills():
    return render_template("skills.html",)

@views.route('/editSkills', methods=["POST"])
@login_required
def editSkills():
    _id = current_user.id
    id = validate(request_input="id", type="string")
    name = validate(request_input="name", type="string")
    
    if id == False or name == False:
        return redirect("skills")
    
    info = collection.update_one( 
        { "_id" : ObjectId(_id), "skills._id": ObjectId(id) },
        { "$set": { 
            "skills.$.name": name
        }}
    )
    
    if info:
        flash("Skill edited")
        return redirect("/skills")
    else:
        flash("Info not edited, please try again.")
    return redirect("/skills")

@views.route('/submitSkills', methods=["POST"])
@login_required
def submitSkills():
    name = validate(request_input="name", type="string")
    
    if name == False:
        return redirect("skills")
    
    id = current_user.id

    info = collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "skills": {
                "_id": ObjectId(),
                "name": name,
            } } 
         }
    )
    
    if info:
        flash("Skill submitted")
        return redirect("/skills")
    else:
        flash("Info not submitted, please try again.")
    return redirect("/skills")

@views.route('/volunteer')
@login_required
def volunteer():
    return render_template("volunteer.html")

@views.route('/editVolunteer', methods=["POST"])
@login_required
def editVolunteer():
    _id = current_user.id
    id = validate(request_input="id", type="string")
    organization = validate(request_input="organization", type="string")
    role = validate(request_input="role", type="string")
    date_started = validate(request_input="date_started", type="text")
    date_ended = validate(request_input="date_ended", type="text")
    
    if id == False or organization == False or role == False or date_started == False or date_ended == False:
        return redirect("/volunteer")
    
    info = collection.update_one( 
        { "_id" : ObjectId(_id), "volunteer._id": ObjectId(id) },
        { "$set": { 
            "volunteer.$.organization": organization,
            "volunteer.$.role": role,
            "volunteer.$.date_started": date_started,
            "volunteer.$.date_ended": date_ended
        }}
    )
    
    if info:
        flash("Volunteer information edited")
        return redirect("/volunteer")
    else:
        flash("Info not edited, please try again.")
    return redirect("/volunteer")

@views.route('/submitVolunteer', methods=["POST"])
@login_required
def submitVolunteer():
    organization = validate(request_input="organization", type="string")
    role = validate(request_input="role", type="string")
    date_started = validate(request_input="date_started", type="text")
    date_ended = validate(request_input="date_ended", type="text")
    
    if organization == False or role == False or date_started == False or date_ended == False:
        return redirect("/volunteer")
    
    id = current_user.id

    info = collection.update_one( 
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
    if info:
        flash("Volunteer information submitted")
        return redirect("/volunteer")
    else:
        flash("Info not submitted, please try again.")
    return redirect("/volunteer")

@views.route('/interests')
@login_required
def interests():
    return render_template("interests.html")

@views.route('/editInterests', methods=["POST"])
@login_required
def editInterests():
    _id = current_user.id
    id = validate(request_input="id", type="string")
    name = validate(request_input="name", type="string")
    
    if id == False or name == False:
        return redirect("/interests")
    
    info = collection.update_one( 
        { "_id" : ObjectId(_id), "interests._id": ObjectId(id) },
        { "$set": { 
            "interests.$.name": name
        }}
    )
    
    if info:
        flash("Information edited")
        return redirect("/interests")
    else:
        flash("Info not edited, please try again.")
    return redirect("/interests")

@views.route('/submitInterests', methods=["POST"])
@login_required
def submitInterests():
    name = validate(request_input="name", type="string")
    
    if name == False:
        return redirect("/interests")
    
    id = current_user.id

    info = collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "interests": {
                "_id": ObjectId(),
                "name": name
            } } 
         }
    )
    
    if info:
        flash("Information submitted")
        return redirect("/interests")
    else:
        flash("Info not submitted, please try again.")
    return redirect("/interests")

@views.route('/extra')
@login_required
def extra():
    extra = current_user.extra
    return render_template("extra.html")

@views.route('/editExtra', methods=["POST"])
@login_required
def editExtra():
    _id = current_user.id
    id = validate(request_input="id", type="string")
    title = validate(request_input="title", type="string")
    description = request.form.get("description").strip()
    
    if id == False or title == False:
        return redirect("/extra")
    
    info = collection.update_one( 
        { "_id" : ObjectId(_id), "extra._id": ObjectId(id) },
        { "$set": { "extra.$.title": title, "extra.$.description": description}}
    )
    
    if info:
        flash("Information edited")
        return redirect("/extra")
    else:
        flash("Info not edited, please try again.")
    return redirect("/extra")

@views.route('/submitExtra', methods=["POST"])
@login_required
def submitExtra():
    title = validate(request_input="title", type="string")
    description = request.form.get("description").strip()
    id = current_user.id
    
    if title == False:
        return redirect("/extra")
    info = collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$push": { "extra": {
                "_id": ObjectId(),
                "title": title,
                "description": description
            } } 
         }
    )
    
    if info:
        flash("Information submitted")
        return redirect("/extra")
    else:
        flash("Info not submitted, please try again.")
    return redirect("/extra")


@views.route("/socialsallowed", methods=["POST"])
@login_required
def socialsallowed():
    id = current_user.id
    personal_bool = validate(request_input='personal_bool', type="string")
    email_bool = validate(request_input='email_bool', type="string")
    linkedin_bool = validate(request_input='linkedin_bool', type="string")
    phone_bool = validate(request_input='phone_bool', type="string")
    twitter_bool = validate(request_input='twitter_bool', type="string")
    instagram_bool = validate(request_input='instagram_bool', type="string")
    youtube_bool = validate(request_input='youtube_bool', type="string")
    tiktok_bool = validate(request_input='tiktok_bool', type="string")
    github_bool = validate(request_input='github_bool', type="string")
    
    if personal_bool == False or email_bool == False or linkedin_bool == False or phone_bool == False or twitter_bool == False or instagram_bool == False or youtube_bool == False or tiktok_bool == False or  github_bool == False:
        return redirect("/build")
    
    info = collection.update_one( 
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
    
    if info:
        flash("Information submitted")
        return redirect("/build")
    else:
        flash("Info not submitted, please try again.")
    return redirect("/build")


@views.route('/build')
@login_required
def preview():
    if not current_user.is_authenticated():
        redirect("/login")
    
    user = current_user
    template = user.template
    templates_collection = db.template
    fonts_collection = db.fonts
    template = templates_collection.find_one({"_id": ObjectId(template)})
    fonts = fonts_collection.find()
    preview = ""
    font_name = ""
    font_location = ""
    font_type = ""
    fonts_list = []
    
    for font in fonts:
        if font["_id"] == user.font:
            font_name = font['name']
            font_location = font['location']
            font_type = font['type']
        elif font["_id"] == template['font']:
            font_name = font['name']
            font_location = font['location']
            font_type = font['type']
        fonts_list.append(font)
        
    font_face = '@font-face { font-family: "' + font_name + '"; font-style: normal; font-weight: 300; src: url("static/' + font_location + '") format("' + font_type + '");}'
    
    if (template['type'] == "skill"):
        preview = skill_preview(current_user, template)
    else:
        preview = basic_preview(current_user, template)
        
    if user.font == "":
        preview = preview.replace("{{font_name}}", font_name)
        preview = preview.replace("{{background_color}}", template['backgroundColor'])
        preview = preview.replace("{{primary_color}}", template['primaryColor'])
        preview = preview.replace("{{secondary_color}}", template['secondaryColor'])
        current_user.font = template['font']
        current_user.background_color = template['backgroundColor']
        current_user.primary_color = template['primaryColor']
        current_user.secondary_color = template['secondaryColor']
    else:
        preview = preview.replace("{{font_name}}", font_name)
        preview = preview.replace("{{background_color}}", current_user.background_color)
        preview = preview.replace("{{primary_color}}", current_user.primary_color)
        preview = preview.replace("{{secondary_color}}", current_user.secondary_color)
        
    preview = preview.replace("{{font_face}}", font_face)
    
    random_number = randint(0, 10000)
    filename = f"My Resume {random_number}"
    
    
    return render_template('preview.html', info = preview, filename = filename, fonts = fonts_list, font_name= font_name, font_location=font_location, font_type=font_type)

@views.route('/download', methods=["POST"])
@login_required
def download():
    filename = validate(request_input="filename", type="string")
    default_name = validate(request_input="default_name", type="string")
    
    if filename == False or default_name == False:
        return redirect("/builds")
    
    if not current_user.is_authenticated():
        redirect("/login")
        
    if filename == None or filename == "":
        filename = default_name
    
    user = current_user
    template = user.template
    templates_collection = db.template
    fonts_collection = db.fonts
    template = templates_collection.find_one({"_id": ObjectId(template)})
    font = fonts_collection.find_one({"_id": ObjectId(current_user.font)})
    preview = ""
    dirname = os.path.dirname(__file__)
    location = f"static/{font['location']}"
    location = re.sub(r' ', "\ ", location)
    if (template['type'] == "skill"):
        preview = skill_preview(current_user, template)
    else:
        preview = basic_preview(current_user, template)
        
    preview = preview.replace("{{font_name}}", font['name'])
    preview = preview.replace("{{background_color}}", current_user.background_color)
    preview = preview.replace("{{primary_color}}", current_user.primary_color)
    preview = preview.replace("{{secondary_color}}", current_user.secondary_color)
    
    preview = preview.replace("{{font_face}}", "")
    font_configuration = FontConfiguration()

    html = HTML(string=preview)
    css = CSS(string="""@page { size: A4; margin: 1cm }
            @font-face { 
                font-family: '""" + font['name'] + """';
                font-style: normal;
                font-weight: 300;
                src: url('""" + location + """');
            }
            
            body{ 
                font-family: '""" + font['name'] + """';
                font-size:13px;
            }
            h1 {
                font-size: 30px;
            }

            h2 {
                font-size: 25px;
            }
            
            h6 {
                font-size: 14px;
            }
            
            h3 {
                font-size: 24px;
            }
            
            h4 {
                font-size: 20px;
            }
            
            h5 {
                font-size: 16px;
            }

            p {
                font-size: 13px;
            }
            """, font_config=font_configuration, base_url=request.base_url)
    path = pathlib.Path(f"website/static/build/{user.last_name} {user.first_name}")
    path.mkdir(parents=True, exist_ok=True)
    
    html.write_pdf(f'{path}/{filename}.pdf', stylesheets=[css], font_config=font_configuration)
    
    collection.update_one( 
        { "_id" : ObjectId(current_user.id) },
        { "$push": { "builds": {
                "_id": ObjectId(),
                "path": f'build/{user.last_name} {user.first_name}/{filename}.pdf',
                "name": filename,
                "date": datetime.date.today().strftime('%x')
            } } 
         }
    )
    full_path = os.path.join(dirname, f"static/build/{user.last_name} {user.first_name}")
    return send_from_directory(full_path, f"{filename}.pdf", as_attachment = True)

@views.route('/builds')
@login_required
def builds():
    return render_template("build.html")

@views.route('/templates')
@login_required
def templates():
    templates_collection = db.template
    template = templates_collection.find({})
    return render_template("templates.html", templates=template)

@views.route('/selecttemplate/<id>')
@login_required
def selecttemplate(id):
    templates_collection = db.template
    template = templates_collection.find_one({"_id": ObjectId(id)})
    if template == [] or template == {}:
        flash("Template does not exist")
        return redirect("templates")
    
    info = collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {
                "template": ObjectId(id),
                "font": template['font'],
                "backgroundColor": template['backgroundColor'],
                "primaryColor": template['primaryColor'],
                "secondaryColor": template['secondaryColor']
            }}
        )
    if info:
        flash("Template selected")
        return redirect("/build")
    else:
        flash("Oops, not updated, please try again.")
        redirect("/templates")

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
        info = collection.update_one( 
            { "_id" : ObjectId(_id) },
            { "$set": { "profile_picture": f"build/{user.last_name} {user.first_name}/profile/{filename}"}}
        )
        
        if info:
            flash("Profile Pic updated")
            return redirect("/profile")
        else:
            flash("Oops, not updated, please try again.")
        return redirect("/profile")

@views.route("/deleteEducation/<id>")
@login_required
def deleteEducation(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "education":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/education")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/education")

@views.route("/deleteExperience/<id>")
@login_required
def deleteExperience(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "experience":{ "_id": ObjectId(id)}}
        }
    )
    if info:
        flash("Information deleted")
        return redirect("/experience")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/experience")

@views.route("/deleteCertification/<id>")
@login_required
def deleteCertification(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "certifications":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/certification")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/certification")

@views.route("/deleteSocial/<id>")
@login_required
def deleteSocial(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "socials":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/socials")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/socials")

@views.route("/deleteProject/<id>")
@login_required
def deleteProject(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "projects":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/projects")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/projects")

@views.route("/deleteSkill/<id>")
@login_required
def deleteSkill(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "skills":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/skills")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/skills")

@views.route("/deleteInterest/<id>")
@login_required
def deleteInterest(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "interests":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/interests")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/interests")

@views.route("/deleteExtra/<id>")
@login_required
def deleteExtra(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "extra":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/extra")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/extra")

@views.route("/deleteVolunteer/<id>")
@login_required
def deleteVolunteer(id):
    _id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "volunteer":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/volunteer")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/volunteer")

@views.route("/deleteBuilds/<id>")
@login_required
def deleteBuilds(id):
    user = current_user
    _id = current_user.id
    dirname = os.path.dirname(__file__)
    for row in user.builds:
        if row['_id'] == id:
            if os.path.exists(os.path.join(dirname, f"website/{row['path']}")):
                os.remove(os.path.join(dirname, row['path']))
    info = collection.update_one( 
        { "_id" : ObjectId(_id) },
        { 
         "$pull": { "builds":{ "_id": ObjectId(id)}}
        }
    )
    
    if info:
        flash("Information deleted")
        return redirect("/builds")
    else:
        flash("Info not deleted, please try again.")
    return redirect("/builds")


@views.route("/editfontsandcolors", methods=['POST'])
@login_required    
def editfontsandcolors():
    font = validate(request_input="font", type="string")
    background_color = validate(request_input="backgroundColor", type="string")    
    primary_color = validate(request_input="primaryColor", type="string") 
    secondary_color = validate(request_input="secondaryColor", type="string")
    
    if font == False or background_color == False or primary_color == False or secondary_color == False:
        return redirect("/build")
    
    id = current_user.id
    info = collection.update_one( 
        { "_id" : ObjectId(id) },
        { "$set": {
                "font": ObjectId(font),
                "backgroundColor": background_color,
                "primaryColor": primary_color,
                "secondaryColor": secondary_color,
            } 
         }
    )
    
    if info:
        flash("Changes made")
        return redirect("/build")
    else:
        flash("Changes not made, please try again.")
    return redirect("/build")
    













def return_item_as_string(items, seperator):
    result = ""
    if seperator == "\n":
        for item in items:
            result = result + f"<p>{item['name']}</p>"
    elif seperator == "li":
        result = "<ul>"
        for item in items:
            result = result + f"<li>{item['name']}</li>"
        result = result + "</ul>"
    else:
        i = 0
        while(i<len(items)):
            if i == (len(items) - 1):
                result = result + f"{items[i]['name']}"
            else:
                result = result + f"{items[i]['name']}{seperator} "
            i = i+1

    return result
            



def basic_preview(user, template):
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
        
    skills_history = return_item_as_string(user.skills, template["skills_seperator"])
        
    for row in user.volunteer:
        temp_volunteer = template["volunteer"]
        temp_volunteer = temp_volunteer.replace("{{organization}}", row['organization'])
        temp_volunteer = temp_volunteer.replace("{{role}}", row['role'])
        temp_volunteer = temp_volunteer.replace("{{date_started}}", row['date_started'])
        temp_volunteer = temp_volunteer.replace("{{date_ended}}", row['date_ended'])
        volunteer_history = volunteer_history + temp_volunteer
        
    interests_history = return_item_as_string(user.interests, template['interests_seperator'])
        
    i=0
    while i < len(user.socials):
        temp_socials = template["socials"]
        row=user.socials[i]
        try:
            social_type = f"{row['type']}_bool"
            if getattr(user, social_type) == "on":
                temp_socials = temp_socials.replace("{{type}}", row['type'])
                temp_socials = temp_socials.replace("{{link}}", row['link'])
            else:
                temp_socials = ""
        except AttributeError:
            temp_socials = ""
        if template['social_seperator'] == "\n":
            socials_history = socials_history + f"<p>{temp_socials}</p>"
        elif template['social_seperator'] == "li":
            socials_history = socials_history + f"<li>{temp_socials}</li>"
        else:
            if(i == (len(user.socials) -1)):
                socials_history = socials_history + f"{temp_socials}"
            else:
                socials_history = socials_history + f"{temp_socials}{template['social_seperator']} "
        i = i+1
        
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
    return preview



def skill_preview(user, template):
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
        
    skills_history = return_item_as_string(user.skills, template["skills_seperator"])
        
    for row in user.volunteer:
        temp_volunteer = template["volunteer"]
        temp_volunteer = temp_volunteer.replace("{{organization}}", row['organization'])
        temp_volunteer = temp_volunteer.replace("{{role}}", row['role'])
        temp_volunteer = temp_volunteer.replace("{{date_started}}", row['date_started'])
        temp_volunteer = temp_volunteer.replace("{{date_ended}}", row['date_ended'])
        volunteer_history = volunteer_history + temp_volunteer
        
    interests_history = return_item_as_string(user.interests, template['interests_seperator'])
    
    for row in user.interests:
        temp_interests = template["interests"]
        temp_interests = temp_interests.replace("{{name}}", row['name'])
        interests_history = interests_history + temp_interests
        
    i=0
    while i < len(user.socials):
        temp_socials = template["socials"]
        row=user.socials[i]
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
        if template['social_seperator'] == "\n":
            socials_history = socials_history + f"<p>{temp_socials}</p>"
        elif template['social_seperator'] == "li":
            socials_history = socials_history + f"<li>{temp_socials}</li>"
        else:
            if(i == (len(user.socials) -1)):
                socials_history = socials_history + f"{temp_socials}"
            else:
                socials_history = socials_history + f"{temp_socials}{template['social_seperator']} "
        i = i+1
        
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
    
    complete_template = experience_history+ " " + educationTemplate+ " " + certificationsTemplate + " " + projectsTemplate + " " + volunteerTemplate+ " " + interestsTemplate+ " " + extraTemplate+ " "
    
    basic_info = basic_info + socials_history
    preview = preview.replace("{{basic_info}}", basic_info)
    preview = preview.replace("{{skill_history}}", skillsTemplate)
    preview = preview.replace("{{info}}", complete_template)
    return preview



