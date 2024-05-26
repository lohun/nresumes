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

