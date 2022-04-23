from flask_application.models.model_user import User
from flask_application.models.model_portfolio import Stock
from flask_application import application, bcrypt
from flask_application.models import model_user
from flask_application.models import model_portfolio
from flask import render_template,redirect,request,session,flash


@application.route('/')
def index():
    # all_users=User.get_all()
    return render_template('login.html')

@application.route('/register')
def registeruser():
    
    return render_template("index.html")


@application.route('/user/login', methods=['post'])
def login():
    is_valid= User.validator_login(request.form)

    if not is_valid:
        return redirect('/') 

    return redirect('/loggedin')

@application.route('/loggedin')
def loggedin():
    if 'user_id' not in session:
        return redirect('/')
    
    if 'user_id' in session:
        id=session['user_id']
        all_stocks=model_portfolio.Stock.get_my_stocks({'id': id})

    return render_template('logged_in.html', all_stocks=all_stocks)

@application.route('/logout')
def logout():
    del session['user_id']
    return redirect('/')



@application.route('/user/create',methods=['post'])
def create():
    is_valid= User.validator(request.form)
    if not is_valid: 
        return redirect('/register')
    
    hash_pw= bcrypt.generate_password_hash(request.form['pw'])
    print(len(hash_pw))

    data={
        **request.form,
        'pw': hash_pw
    }
    
    id= User.create(data)
    session['user_id']=id
    return redirect('/')


@application.route('/user/edit/<int:id>')
def edit(id):
    user= User.get_one({'id': id})
    return render_template("user_edit.html", user=user)

@application.route('/user/show/<int:id>')
def display(id):
     user= User.get_one({'id': id})
     return render_template("user_edit.html", user=user)


@application.route('/user/update/<int:id>', methods=['post'])
def update(id):
    # User.update(request.form)
    # return redirect('/')
    pass

@application.route('/user/delete/<int:id>')
def delete(id):
    # User.delete({'id':id})
    # return redirect('/')
    pass