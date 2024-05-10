from datetime import timedelta
import json
import bcrypt
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, flash
from flask_login import current_user, login_required, login_user, logout_user
from .database import db
from .model import User
from website import login_manager
from weasyprint import HTML, CSS


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
                
                return redirect('/preview')
            else:
                flash('login unsuccessful')
        else:
            flash('login unsuccessful')
        
    return render_template('login.html')

@views.route('/')
@login_required
def home():
    user = current_user

    return render_template("profile.html", data=user)

@views.route("/basic_info")
@login_required
def basic_info():
    if not current_user.is_authenticated():
        redirect("/login")
    
    user = current_user

    return render_template("profile.html", data=user)

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
            return redirect("/", code=403)
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
            "extra": []
        }
        
        collection.insert_one(data)

        return redirect("/", 201)
    return render_template("register.html")


@views.route('/experience')
@login_required
def experience():
    experience = current_user.experience
    return render_template("experience.html", experience = experience)
    
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
    return redirect("/", 201)

@views.route('/education')
@login_required
def education():
    education = current_user.education
    return render_template("experience.html", education = education)

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
    return redirect("/", 201)

@views.route('/certification')
@login_required
def certification():
    certification = current_user.certification
    return render_template("experience.html", certification = certification)

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
    return redirect("/", 201)


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
    return redirect("/", 201)

@views.route('/project')
@login_required
def project():
    project = current_user.project
    return render_template("experience.html", project = project)

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
    return redirect("/", 201)

@views.route('/skills')
@login_required
def skills():
    skills = current_user.skills
    return render_template("experience.html", skills = skills)

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
    return redirect("/", 201)

@views.route('/volunteer')
@login_required
def volunteer():
    volunteer = current_user.volunteer
    return render_template("experience.html", volunteer = volunteer)

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
    return redirect("/", 201)

@views.route('/interest')
@login_required
def interest():
    interest = current_user.interest
    return render_template("experience.html", interest = interest)

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
    return redirect("/", 201)

@views.route('/extra')
@login_required
def extra():
    extra = current_user.extra
    return render_template("experience.html", extra = extra)

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
    return redirect("/", 201)


@views.route('/preview')
def preview():
    if not current_user.is_authenticated():
        redirect("/login")
    
    id = current_user.id

    user = collection.find_one({"_id": id})
    template = user['template']
    templates_collection = db["template"]
    template = templates_collection.find_one({"_id": ObjectId(template)})
    preview = open(template["location"], "r").read()
    experienceTemplate = template['experience_template']
    certificationsTemplate = template['certifications_template']
    educationTemplate = template['education_template']
    socialsTemplate = template['socials_template']
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
    preview = preview.replace("fullname", f"{user['last_name']} {user['first_name']}")
    preview = preview.replace("address", f"{user['address']}")
    preview = preview.replace("email", f"{user['email']}")
    preview = preview.replace("phone_number", f"{user['phone_number']}")
    
    for row in user["experience"]:
        print(row)
        temp_experience = template["experience"]
        temp_experience = temp_experience.replace("end_date", row["date_ended"])
        temp_experience = temp_experience.replace("start_date", row['date_started'])
        temp_experience = temp_experience.replace("company", row['company'])
        temp_experience = temp_experience.replace("role", row['role'])
        temp_experience = temp_experience.replace("role_description", row['description'])
        experience_history = experience_history + temp_experience
        
    for row in user["education"]:
        temp_education = template["education"]
        temp_education = temp_education.replace("school", row['school'])
        temp_education = temp_education.replace("award", row['award'])
        temp_education = temp_education.replace("department", row['department'])
        temp_education = temp_education.replace("faculty", row['faculty'])
        temp_education = temp_education.replace("achievements", row['achievements']or "")
        temp_education = temp_education.replace("date_started", row['date_started'])
        temp_education = temp_education.replace("date_ended", row['date_ended'])
        education_history = education_history + temp_education
        
    for row in user["projects"]:
        temp_projects = template["projects"]
        temp_projects = temp_projects.replace("name", row['name'])
        temp_projects = temp_projects.replace("link", row['link'])
        temp_projects = temp_projects.replace("description", row['description'])
        temp_projects = temp_projects.replace("date_started", row['date_started'])
        temp_projects = temp_projects.replace("date_ended", row['date_ended'])
        projects_history = projects_history + temp_projects
        
    for row in user["certifications"]:
        temp_certifications = template["certification"]
        temp_certifications = temp_certifications.replace("name", row['name'])
        temp_certifications = temp_certifications.replace("organization", row['organization'])
        temp_certifications = temp_certifications.replace("date", row['date'])
        certifications_history = certifications_history + temp_certifications
        
    for row in user["skills"]:
        temp_skills = template["skills"]
        temp_skills = temp_skills.replace("name", row['name'])
        skills_history = skills_history + temp_skills
        
    for row in user["volunteer"]:
        temp_volunteer = template["volunteer"]
        temp_volunteer = temp_volunteer.replace("organization", row['organization'])
        temp_volunteer = temp_volunteer.replace("role", row['role'])
        temp_volunteer = temp_volunteer.replace("date_started", row['date_started'])
        temp_volunteer = temp_volunteer.replace("date_ended", row['date_ended'])
        volunteer_history = volunteer_history + temp_volunteer
        
    for row in user["interests"]:
        temp_interests = template["interests"]
        temp_interests = temp_interests.replace("name", row['name'])
        interests_history = interests_history + temp_interests
        
    for row in user["socials"]:
        temp_socials = template["socials"]
        temp_socials = temp_socials.replace("type", row['type'])
        temp_socials = temp_socials.replace("link", row['link'])
        socials_history = socials_history + temp_socials
        
    for row in user["extra"]:
        temp_extra = template["extra"]
        temp_extra = temp_extra.replace("title", row['title'])
        temp_extra = temp_extra.replace("description", row['description'])
        extra_history = extra_history + temp_extra
    if experience_history != "":
        experienceTemplate = experienceTemplate.replace('employment_history', experience_history)
    else:
        experienceTemplate = ""
        
    if education_history != "":
        educationTemplate = educationTemplate.replace('education_history', education_history)
    else:
        educationTemplate = ""
        
    if projects_history != "":
        projectsTemplate = projectsTemplate.replace('projects_history', projects_history)
    else:
        projectsTemplate = ""
    
    if skills_history != "":
        skillsTemplate = skillsTemplate.replace('skills_history', skills_history)
    else:
        skillsTemplate = ""
        
    if certifications_history != "":
        certificationsTemplate = certificationsTemplate.replace('certifications_history', certifications_history)
    else:
        certificationsTemplate = ""
        
    if volunteer_history != "":
        volunteerTemplate = volunteerTemplate.replace('volunteer_history', volunteer_history)
    else:
        volunteerTemplate = ""
        
    if interests_history != "":
        interestsTemplate = interestsTemplate.replace('interests_history', interests_history)
    else:
        interestsTemplate = ""
        
    if user["extra"] != []:
        extraTemplate = extraTemplate.replace('extra_history', extra_history)
    else:
        extraTemplate = ""
        
    if socials_history != "":
        socialsTemplate = socialsTemplate.replace('socials_history', socials_history)
    else:
        socialsTemplate = ""
    
    complete_template = experience_history+ " " + educationTemplate+ " " + certificationsTemplate + " " + projectsTemplate+ " " + skillsTemplate+ " " + volunteerTemplate+ " " + interestsTemplate+ " " + extraTemplate+ " " + socialsTemplate
    
    preview = preview.replace("info", complete_template)
    
    return render_template('preview.html', info = preview)

@views.route('/download')
@login_required
def download():
    if not current_user.is_authenticated():
        redirect("/login")
    
    id = current_user.id

    user = collection.find_one({"_id": id})
    template = user['template']
    templates_collection = db["template"]
    template = templates_collection.find_one({"_id": ObjectId(template)})
    preview = open(template["location"], "r").read()
    experienceTemplate = template['experience_template']
    certificationsTemplate = template['certifications_template']
    educationTemplate = template['education_template']
    socialsTemplate = template['socials_template']
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
    preview = preview.replace("fullname", f"{user['last_name']} {user['first_name']}")
    preview = preview.replace("address", f"{user['address']}")
    preview = preview.replace("email", f"{user['email']}")
    preview = preview.replace("phone_number", f"{user['phone_number']}")
    
    for row in user["experience"]:
        print(row)
        temp_experience = template["experience"]
        temp_experience = temp_experience.replace("end_date", row["date_ended"])
        temp_experience = temp_experience.replace("start_date", row['date_started'])
        temp_experience = temp_experience.replace("company", row['company'])
        temp_experience = temp_experience.replace("role", row['role'])
        temp_experience = temp_experience.replace("role_description", row['description'])
        experience_history = experience_history + temp_experience
        
    for row in user["education"]:
        temp_education = template["education"]
        temp_education = temp_education.replace("school", row['school'])
        temp_education = temp_education.replace("award", row['award'])
        temp_education = temp_education.replace("department", row['department'])
        temp_education = temp_education.replace("faculty", row['faculty'])
        temp_education = temp_education.replace("achievements", row['achievements']or "")
        temp_education = temp_education.replace("date_started", row['date_started'])
        temp_education = temp_education.replace("date_ended", row['date_ended'])
        education_history = education_history + temp_education
        
    for row in user["projects"]:
        temp_projects = template["projects"]
        temp_projects = temp_projects.replace("name", row['name'])
        temp_projects = temp_projects.replace("link", row['link'])
        temp_projects = temp_projects.replace("description", row['description'])
        temp_projects = temp_projects.replace("date_started", row['date_started'])
        temp_projects = temp_projects.replace("date_ended", row['date_ended'])
        projects_history = projects_history + temp_projects
        
    for row in user["certifications"]:
        temp_certifications = template["certification"]
        temp_certifications = temp_certifications.replace("name", row['name'])
        temp_certifications = temp_certifications.replace("organization", row['organization'])
        temp_certifications = temp_certifications.replace("date", row['date'])
        certifications_history = certifications_history + temp_certifications
        
    for row in user["skills"]:
        temp_skills = template["skills"]
        temp_skills = temp_skills.replace("name", row['name'])
        skills_history = skills_history + temp_skills
        
    for row in user["volunteer"]:
        temp_volunteer = template["volunteer"]
        temp_volunteer = temp_volunteer.replace("organization", row['organization'])
        temp_volunteer = temp_volunteer.replace("role", row['role'])
        temp_volunteer = temp_volunteer.replace("date_started", row['date_started'])
        temp_volunteer = temp_volunteer.replace("date_ended", row['date_ended'])
        volunteer_history = volunteer_history + temp_volunteer
        
    for row in user["interests"]:
        temp_interests = template["interests"]
        temp_interests = temp_interests.replace("name", row['name'])
        interests_history = interests_history + temp_interests
        
    for row in user["socials"]:
        temp_socials = template["socials"]
        temp_socials = temp_socials.replace("type", row['type'])
        temp_socials = temp_socials.replace("link", row['link'])
        socials_history = socials_history + temp_socials
        
    for row in user["extra"]:
        temp_extra = template["extra"]
        temp_extra = temp_extra.replace("title", row['title'])
        temp_extra = temp_extra.replace("description", row['description'])
        extra_history = extra_history + temp_extra
    if experience_history != "":
        experienceTemplate = experienceTemplate.replace('employment_history', experience_history)
    else:
        experienceTemplate = ""
        
    if education_history != "":
        educationTemplate = educationTemplate.replace('education_history', education_history)
    else:
        educationTemplate = ""
        
    if projects_history != "":
        projectsTemplate = projectsTemplate.replace('projects_history', projects_history)
    else:
        projectsTemplate = ""
    
    if skills_history != "":
        skillsTemplate = skillsTemplate.replace('skills_history', skills_history)
    else:
        skillsTemplate = ""
        
    if certifications_history != "":
        certificationsTemplate = certificationsTemplate.replace('certifications_history', certifications_history)
    else:
        certificationsTemplate = ""
        
    if volunteer_history != "":
        volunteerTemplate = volunteerTemplate.replace('volunteer_history', volunteer_history)
    else:
        volunteerTemplate = ""
        
    if interests_history != "":
        interestsTemplate = interestsTemplate.replace('interests_history', interests_history)
    else:
        interestsTemplate = ""
        
    if user["extra"] != []:
        extraTemplate = extraTemplate.replace('extra_history', extra_history)
    else:
        extraTemplate = ""
        
    if socials_history != "":
        socialsTemplate = socialsTemplate.replace('socials_history', socials_history)
    else:
        socialsTemplate = ""
    
    complete_template = experience_history+ " " + educationTemplate+ " " + certificationsTemplate + " " + projectsTemplate+ " " + skillsTemplate+ " " + volunteerTemplate+ " " + interestsTemplate+ " " + extraTemplate+ " " + socialsTemplate
    
    preview = preview.replace("info", complete_template)
    
    html = HTML(string=preview)
    css = CSS(string='@page { size: A4; margin: 1cm }')
    
    html.write_pdf('My Resume.pdf', stylesheets=[css])
    return redirect("/basic_info")


@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')



