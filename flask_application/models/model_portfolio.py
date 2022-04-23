from jinja2 import Undefined
from flask_application.config.mysqlconnection import connectToMySQL
from flask import flash, session
from flask_application import bcrypt
from flask_application.models import model_user
import re

from flask import jsonify


DATABASE='stocks_db'

class Stock:
    def __init__(self, data):
        self.id = data['id']
        self.ticker = data['ticker']
        self.price = data['price']
        self.name=data['name']
        self.updated_at=data['updated_at']
        self.created_at = data['created_at']
        self.user_id=data['user_id']

    @classmethod
    def get_all_stocks(cls):
        query = "SELECT * FROM stocks;"
        results = connectToMySQL(DATABASE).query_db(query)
        if results:
            stocks_list = []
            for b in results:
                stocks_list.append( cls(b) )
            return stocks_list
 

    @classmethod
    def get_my_stocks(cls,data):
        query = "SELECT * FROM stocks JOIN users on stocks.user_id= users.id WHERE users.id= %(id)s;"
        results = connectToMySQL(DATABASE).query_db(query,data)
        # if results:
        #     my_list=[]
        #     for stocks in results:
        #         stocks=cls(stocks)
        #         dict={
        #             'id': stocks['id'],
        #             'ticker': stocks['ticker'],
        #             'price': stocks['price'],
        #             'name': stocks['name'],
        #             'updated_at': stocks['updated_at'],
        #             'created_at': stocks['created_at'],
        #             'user_id': stocks['user_id']

        #         }
        #         my_list.append(stocks)
        #         print(my_list)
        #     return my_list
                
        # return []
        if results:
            stocks_list = []
            for b in results:
                stocks_list.append( cls(b) )
            return stocks_list
        

    @classmethod
    def createstocks(cls, data):
        query = "INSERT INTO stocks (ticker,name, price, user_id,created_at,updated_at) VALUES (%(ticker)s,%(name)s, %(price)s, %(user_id)s,  NOW() , NOW() );"
        return connectToMySQL(DATABASE).query_db(query,data)
        

    @classmethod
    def get_one_ticker(cls,data):
        query  = "SELECT ticker FROM stocks WHERE id = %(id)s;"
        result = connectToMySQL(DATABASE).query_db(query,data)
        return result

    @classmethod
    def getone(cls,data):
        query  = "SELECT * FROM stocks WHERE id = %(id)s;"
        result = connectToMySQL(DATABASE).query_db(query,data)
        return result
    
    @classmethod
    def getusername(cls,data):
        query  = "SELECT first_name, last_name FROM users LEFT JOIN stocks ON stocks.user_id=users.id WHERE stocks.id= %(id)s;"
        result = connectToMySQL(DATABASE).query_db(query,data)
        if result:
            poster=[]
            for stocks in result:
                poster.append(stocks)
            print(poster)
            return poster
        return False

    @classmethod
    def updatestocks(cls,data):
        query = "UPDATE stocks SET ticker = %(ticker)s, price = %(price)s, upadate_at= %(updated_at)s, created_at= %(created_at)s WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query,data)

    @classmethod
    def delete(cls,data):
        query  = "DELETE FROM stocks WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query,data)

    @staticmethod
    def stocks_validator(form_data):
        stock_valid= True

        if len(form_data['tcker']) ==0 :
            stock_valid= False
            flash("stock must have a ticker symbol", "err_title")
        
        if len(form_data['price']) <=1 :
            stock_valid= False
            flash("Stock must have a price", "err_stock_network")
    
        return stock_valid

    @staticmethod
    def capital_validator(form_data):
        capital_valid= True

        if not int(form_data['capital']) > 0 or int(form_data['capital']== Undefined):
            capital_valid= False
            flash("Must enter capital to be invested", "err_capital")
    
    
        return capital_valid

