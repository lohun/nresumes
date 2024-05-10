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
    first_name = ""
    last_name = ""
    email = ""
    date_of_birth = ""
    phone_number = ""
    summary = ""
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

    def __init__(self, user, authenticated, anonymous, active):
        self.id = user['_id']
        self.first_name = user['first_name']
        self.last_name = user['last_name']
        self.email = user['email']
        self.date_of_birth = user['date_of_birth']
        self.phone_number = user['phone_number']
        self.summary = user['summary']
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
        self.authenticated = authenticated
        self.anonymous = anonymous,
        self.active = active
        
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