from flask_application.config.mysqlconnection import connectToMySQL
from flask import flash, session
from flask_application import bcrypt
from flask_application.models import model_portfolio
import re

DATABASE='stocks_db'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.pw = data['pw']
        self.email = data['email']
        self.fullname=f"{self.first_name} {self.last_name}"

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(DATABASE).query_db(query)
        if results:
            user_list = []
            for u in results:
                user_list.append( cls(u) )
            return user_list

    @classmethod
    def create(cls, data):
        query = "INSERT INTO users (first_name,last_name,email,pw) VALUES (%(first_name)s,%(last_name)s,%(email)s,%(pw)s);"
        # comes back as the new row id
        person_id = connectToMySQL(DATABASE).query_db(query,data)
        return person_id

    @classmethod
    def get_one(cls,data):
        query  = "SELECT * FROM users WHERE id = %(id)s;"
        result = connectToMySQL(DATABASE).query_db(query,data)
        if result:
            return cls(result[0])
        return False


    @classmethod
    def get_one_by_email(cls,data):
        query  = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(DATABASE).query_db(query,data)
        if result:
            return cls(result[0])
        return False

    @classmethod
    def update(cls,data):
        query = "UPDATE users SET first_name=%(first_name)s,last_name=%(last_name)s,email=%(email)s, pw=%(pw)s  WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query,data)

    @classmethod
    def delete(cls,data):
        query  = "DELETE FROM users WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query,data)

    @staticmethod
    def validator(form_data):
        is_valid= True

        if len(form_data['first_name']) <2 or form_data['first_name'].isalpha()== False:
            is_valid= False
            flash("First Name Required and only letters!", "err_user_first_name")
            # session['err_first_name']= "First Name Required"

        if len(form_data['last_name']) <2  or form_data['last_name'].isalpha()== False:
            is_valid= False
            flash("Last Name Required and only letters!", "err_user_last_name")
            # session['err_last_name']= "Last Name Required"
        
        if len(form_data['email']) <1 :
            is_valid= False
            flash("Email Required", "err_user_email")
            # session['err_last_name']= "Last Name Required"
        elif not EMAIL_REGEX.match(form_data['email']): 
            flash("Invalid email address!", "err_user_email")
            is_valid = False
        else:
            potential_user= User.get_one_by_email({'email': form_data['email']})
            
            if potential_user:
                flash("Email taken", "err_user_email")
                is_valid= False


        if len(form_data['pw']) <8 :
            is_valid= False
            flash("Password length must be 8 or more characters", "err_user_pw")
            # session['err_pw']= "Last Name Required"
        
        if len(form_data['confirm_pw']) <8 :
            is_valid= False
            flash("Password length must be 8 or more characters", "err_user_confirm_pw")
            # session['err_confirm_pw']= "Last Name Required"

        elif form_data['confirm_pw'] != form_data['pw']:
            is_valid= False
            flash("Passwords dont match", "err_user_confirm_pw")
            # session['err_confirm_pw']= "Last Name Required"

        elif is_valid==True:
            flash("User registered", "user_success")
            

        return is_valid

    @staticmethod
    def validator_login(form_data):
        is_valid= True

        if len(form_data['email']) <1 :
            is_valid= False
            flash("Email address required!", "err_user_email_login")
            # session['err_pw']= "Last Name Required"
        
        elif not EMAIL_REGEX.match(form_data['email']): 
            flash("Invalid email address!", "err_user_email_login")
            is_valid = False

        if len(form_data['pw']) <8 :
            is_valid= False
            flash("Invalid Password", "err_user_pw_login")
            # session['err_pw']= "Last Name Required"
        
        else:
            potential_user= User.get_one_by_email({'email': form_data['email']})
            if not potential_user:
                is_valid= False
                print(potential_user)
                flash("User not found", "err_user_pw_login")
            elif not bcrypt.check_password_hash(potential_user.pw, form_data['pw']):
                is_valid=False
                flash("Wrong Password", "err_user_pw_login")
            else:
                session['user_id']=potential_user.id
                # session['user_name']=potential_user.first_name
                # print(session['user_name'])


        return is_valid