from distutils.command import build
import json
import bcrypt
from flask_login import UserMixin
from .database import db
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)



class User(UserMixin):
    collection = db["users"]
    authenticated = False
    anonymous = True
    active = False
    id = 0
    profile_picture = "placeholder.png"
    font = ""
    background_color = ""
    primary_color = ""
    secondary_color = ""
    title = ""
    first_name = ""
    last_name = ""
    email = ""
    email_bool = "on"
    address_bool = "on"
    linkedin_bool = "off"
    phone_bool = "on"
    twitter_bool = None
    instagram_bool = None
    youtube_bool = None
    tiktok_bool = None
    github_bool = None
    address = ""
    country = ""
    date_of_birth = ""
    phone_number = ""
    template = ""
    password = ""
    education = []
    socials = []
    certifications = []
    experience = []
    projects = []
    skills = []
    volunteer = []
    interests = []
    extra = []
    builds = []

    def __init__(self, user, authenticated, anonymous, active):
        self.id = user['_id']
        self.title = user['title']
        self.first_name = user['first_name']
        self.last_name = user['last_name']
        self.email = user['email']
        self.personal_bool = user['personal_bool']
        self.address_bool = user['address_bool']
        self.email_bool = user['email_bool']
        self.linkedin_bool = user['linkedin_bool']
        self.phone_bool = user['phone_bool']
        self.twitter_bool = user['twitter_bool']
        self.instagram_bool = user['instagram_bool']
        self.youtube_bool = user['youtube_bool']
        self.tiktok_bool = user['tiktok_bool']
        self.github_bool = user['github_bool']
        self.address = user['address']
        self.country = user['country']
        self.date_of_birth = user['date_of_birth']
        self.phone_number = user['phone_number']
        self.template = user['template']
        self.password = user['password']
        self.education = user['education']
        self.socials = user['socials']
        self.certifications = user['certifications']
        self.experience = user['experience']
        self.projects = user['projects']
        self.skills = user['skills']
        self.volunteer = user['volunteer']
        self.interests = user['interests']
        self.extra = user['extra']
        self.builds = user['builds']
        self.authenticated = authenticated
        self.anonymous = anonymous,
        self.active = active
        
        if 'profile_picture' in user.keys() and user['profile_picture'] != "":
            self.profile_picture = user['profile_picture']
        
        if 'backgroundColor' in user.keys() and user['backgroundColor'] != "":
            self.font = user['font']
            self.background_color = user['backgroundColor']
            self.primary_color = user['primaryColor']
            self.secondary_color = user['secondaryColor']
        
    def is_authenticated(self):
        return self.authenticated
    
    def get_id(self):
        return JSONEncoder().encode(self.id)
    
    def is_anonymous(self):
        return self.anonymous
    
    def is_active(self):
        return self.active
    
    def get(self, user_id):
        return JSONEncoder().encode(self.collection.find_one({"_id": user_id}))
    
    def auth(self, email, password):
        user = self.collection.find_one({"email": email})
        if user != None or user != {}:
            hashed_password = bytes(user['password'], "utf-8")
            return bcrypt.checkpw(password, hashed_password)
        else:
            return False