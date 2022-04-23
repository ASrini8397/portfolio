from flask_application import application
from flask_application.controllers import controller_portfolios, controller_users

# ...server.py


if __name__ == "__main__":
    application.run(debug=True)
