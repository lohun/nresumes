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
    schema = {
        "id": "UID",
        "first_name": "string",
        "last_name": "string",
        "date_of_birth": "string",
        "email": "string",
        "phone_number": "string",
        "summary": "string",
        "template": "string",
        "password": "string",
        "education": """[
            {
                "id": "UID",
                "school": "string",
                "award": "string",
                "department": "string",
                "faculty": "string",
                "achievements": "string",
                "date_started": "string",
                "date_ended": "string"
            }
                      ]""",
                      
        "socials": """[
                "id": "UID",
                "type": (),
                "link": "string"
            ]""",
        
        "certifications": """[
                "id": "UID",
                "name": string,
                "organization": string
                "date": string
            ]""",
        
        "experience": """[
            {
                "id": "UID",
                "company": "string",
                "role": "string",
                "description": "string",
                "date_started": "string",
                "date_ended": "string"
            }
                      ]""",
        
        "projects": """[
            {
                "id": "UID",
                "name": "string",
                "link": "string",
                "description": "string",
                "date_started": "string",
                "date_ended": "string"
            }
                      ]""",
                      
        "skills": """[
            {
                "id": "UID",
                "name": "string",
                "experience_id": [],
                "project_id": []
            }
                      ]""",
                      
        "volunteer": """[
            {
                "id": "UID",
                "organization": "string",
                "role": string,
                "date_started": "string",
                "date_ended": "string"
            }
                      ]""",
                      
        "interests": """[
        {
            "id": "UID",
            "name": "string",
        }
                    ]""",
                    
        "extra": """[
        {
            "id": "UID",
            "title": "string",
            "description": "string",
        }
                    ]""",
                      
            
    }


    def __init__(self, id, first_name, last_name, email, authenticated, anonymous, active):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
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