from sklearn.model_selection import RepeatedStratifiedKFold
from flask_application.models.model_portfolio import Stock
from flask_application.models.model_user import User
from flask_application.models import model_portfolio
from flask_application.models import model_user
from flask_application import application, bcrypt
from dateutil.relativedelta import relativedelta
import requests
import nasdaqdatalink
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation
from pypfopt.discrete_allocation import get_latest_prices
import scipy as sc
import scipy.optimize as sc
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR
import pandas as pd
from datetime import datetime
import numpy as np
import pandas_datareader.data as web
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import json
from flask import render_template, redirect, request, session, flash, jsonify




@application.route('/stock')
def new_stock():

    return render_template('search.html')


@application.route('/getstocks', methods=['post'])
def stockform():

    stocks= request.form['stocks']
    # print(request.form['stocks'])
    # This route is for users to search for stocks, the objective is to make it easy to search for companies if the user doesn't 
    # know the exact ticker symbol. This way they can search for the company and still get the result


    url = "https://yh-finance.p.rapidapi.com/auto-complete"

    querystring = {"q": f'{stocks}'}

    headers = {
        "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
        "X-RapidAPI-Key": "8724a05bafmsh7092dbe2bfb89b5p11cc18jsn862c8f2a4bf0"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    stockdata =response.json()
    stockarr=[]
    
    for stock in stockdata['quotes']:
        stockname= stock['shortname']
        stockticker= stock['symbol']
        stockindex=stock['exchDisp']
        # print(stockname)
        # print(stockticker)
        data= {
            'name': stockname,
            'ticker': stockticker,
            'exchange': stockindex
        }
        stockarr.append(data)
    # print(stockarr)
    return render_template("search.html",stockarr=stockarr)



@application.route('/setstock', methods=['post'])
def show_stock():
    #This route is to take the user's chosen security and get the ticker symbol and store the needed info to the db
    # it will take the security name, ticker, price at the time they added it and the user_id so only that user can access their portfolio



    ticker=request.form['ticker']
    name=request.form['name']
    user_id=request.form['user_id']
    print(ticker)
    url = "https://yh-finance.p.rapidapi.com/stock/v3/get-chart"

    querystring = {"interval":"1mo","symbol":f"{ticker}","range":"1d","includePrePost":"false","useYfid":"true","includeAdjustedClose":"true","events":"capitalGain,div,split"}

    headers = {
        "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
        "X-RapidAPI-Key": "8724a05bafmsh7092dbe2bfb89b5p11cc18jsn862c8f2a4bf0"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    stonks=response.json()
    # test= json.dumps(stonks, indent=2)
    # print(test)
    #This is to destructure the JSON result and get the ticker & price
    for vals in stonks['chart']['result']:
        price= vals['meta']['regularMarketPrice']
    data={
            'ticker': ticker,
            'name':name,
            'price': price,
            'user_id': user_id
        }
    # print(data)
    #     resultarr.append(data)
    # print(resultarr)
    new=Stock.createstocks(data) 
    #This will send the info to the MySQL db

    return redirect('/loggedin')


    

@application.route('/stock/optimize', methods=['post'])
def stock_opt():
    
    is_valid= Stock.capital_validator(request.form)

    if not is_valid:
        capital=10000
    else:
        capital= int(request.form['capital'])

    # print(capital)
    # print(type(capital))
    #This route is to calculate the optimal weightage of the user's overall portfolio
    #It can be called any number of times so the user can add or remove stocks and can update weightage after any kind of price movement
    #The purpose is to automate it and not have to enter in the data for each stock individually using pandas-datareader in an ipnyb file
    id=session['user_id']
    portfolio=model_portfolio.Stock.get_my_stocks({'id': id})
    res=[]
    for stocks in portfolio:
        res.append(stocks.ticker)
    # print(res)
    
    weights2=[]
    length=len(res) #get the length of the portfolio to create the equal weightage of all stocks
    weightage=round((1/length),4) # eg if there is 5 stocks the weightage to start is 1/5 = .2
    print(weightage)
    
    for stocks in res:
        # weights3=np.append(weights,weightage)  #this is to fill the array with the calculated weightage using the specific np append method
        weights2.append(weightage)
    #     count+=1
    weights=np.array(weights2)

    
    startdate= '2015-01-01'
    today= datetime.today().strftime('%Y-%m -%d')

    #Now we need to store the adjusted closng price of the stocks within the user's portfolio to calculate daily returns
    df=pd.DataFrame()
    for stock in res:
        df[stock]= web.DataReader(stock, data_source='yahoo', start=startdate, end=today)['Adj Close']

    ret= df.pct_change().dropna()
    # meanreturns=ret.mean()

    #covariance-variance matrix

    cov=ret.cov()


    #Portfolio variance -> Pvar= portfolio variance

    wd= {}
    for stocks in res:
        wd[stocks]=weightage
    
    
    pvar= np.dot(weights.T, np.dot(cov, weights)) *252

    # #p std dev or volatility -> pvol= Portfolio Volitility

    pvol= np.sqrt(pvar)
    # print(pvol)
    rff=.02
    # # #annual returns
    returns= np.sum((ret.mean())* weights) * 252
    stddeviation=np.sqrt(np.dot(weights.T, np.dot(cov, weights)))* np.sqrt(252)
    # pvar=np.dot(weights.T, np.dot(cov, weights))* (252)
    # negativesharpe=(returns-rff)/stddeviation

     # #expected anret, vol (risk), std dev of overall p

    pvars=str(round(pvar,3)  *100)+ '%'
    pvols=str(round(pvol,3)*100) + '%'
    pret= str(round(returns,3) *100) +'%'

    # print(pvars, pvols, pret)

    show={
        'ER': pret,
        'OR': pvols,
        'Var': pvars
    }
    
    #negative sharpe ratio calculations using pvars pvols and pret from above
    
    # rf= nasdaqdatalink.get("FRED/DGS10",start_date="2015-01-01", end_date="2022-04-01")
    #Module not working with deployment
    # This is to get the most recent risk free rate available from FRED data
    # if rf is None:
   
    # print(newret)
    # else:
    # rff=(rf['Value'].iloc[-1])/100
    # print(rff)

    sharpe= ((returns-rff)/stddeviation)
    # print(nsharpe)

    mu=expected_returns.mean_historical_return(df)
    S= risk_models.sample_cov(df)
    # print(mu, S)
    
    em=EfficientFrontier(mu,S)
    ef=EfficientFrontier(mu, S)
    w=ef.max_sharpe(risk_free_rate=rff)
    minvol=em.min_volatility()
    performance=em.portfolio_performance(verbose=True, risk_free_rate=rff)

    # print(minvol, "minimum vol")
    cw=ef.clean_weights()
    # print(w)
    data2=ef.portfolio_performance(verbose=False, risk_free_rate=rff)
    
    #Allocation of shares
    lp=get_latest_prices(df)
    da=DiscreteAllocation(w, lp, total_portfolio_value= capital)
    dc=DiscreteAllocation(minvol, lp, total_portfolio_value= capital)
    dd= DiscreteAllocation(wd, lp, total_portfolio_value= capital)
    allocation, leftover = da.lp_portfolio()
    minallocation, leftover2= dc.lp_portfolio()
    eqbalance, leftover3=dd.lp_portfolio()

    data4={
        'ma': minallocation,
        'rc': leftover2,
        'ER': (str(round(performance[0],3)  *100)+ '%'),
        'AV': (str(round(performance[1],2)  *100)+ '%'),
        'SR': round(performance[2],3)
    }
    # print(data4)

    data5={
        'eq': eqbalance,
        'rc': leftover3,
        'w': wd
    }
    # print(allocation, "Allocation")
    # print(leftover, "Leftover money")
    # print(type(mu))
    # print(type(S))
    # print(type(allocation))
    # print(type(leftover))
    # print(data2)
    data3={
        'ER': (str(round(data2[0],3)  *100)+ '%'),
        'AV': (str(round(data2[1],3)  *100)+ '%'),
        'SR': data2[2],

    }
    # print(data3)

    data={
        'mu': mu,
        'allocation': allocation,
        'weightage': w,
        'Efficient Frontier': ef,
        'leftover': leftover
    }
    
    # print(data)



    return render_template('mystocks.html', data=data, data3=data3, w=w, show=show, minvol=minvol, data4=data4, data5=data5, sharpe=sharpe )
    # return render_template('mystocks.html')









@application.route('/stock/forecast/<int:id>')
def forecast_stock(id):
    stock = Stock.get_one_ticker({'id': id})
    stockticker=stock[0]['ticker']
    print(stockticker)
    
    today= datetime.today().strftime('%Y-%m -%d')
    startdate = datetime.today()-relativedelta(months=3)
    # print(today, startdate)
   

    # Now we need to store the adjusted closng price of the stocks within the user's portfolio to calculate daily returns
    df=pd.DataFrame()
    df= web.DataReader(stockticker, data_source='yahoo', start=startdate, end=today)
    comparison_price=df.tail(1)
    df=df.head(len(df)-1)
    newarr=[]
    days=df.index.values[:]
    for day in days:
        y=(str(day).split('T'))
        z=y[0].split('-')[2]
        newarr.append(int(z))
          
    
    priceslist=list()
    close=df.loc[:, 'Adj Close']
    for price in close:
        priceslist.append(price)
    print(len(newarr))
    daysarr = np.reshape(newarr, (-1, 1))
    # print(daysarr)
    # print(priceslist)
    
   

    lin_svr=SVR(kernel='linear', C= 1000)
    lin_svr.fit(daysarr, priceslist)

    poly_svr=SVR(kernel='poly', C= 1000, degree=2)
    poly_svr.fit(daysarr, priceslist)

    rbf_svr=SVR(kernel='rbf', C= 1000, gamma=0.85)
    rbf_svr.fit(daysarr, priceslist)

    # 
    numberofdays=len(newarr)-1
    #show the predicted price
    day=[[numberofdays]]
    forecastedate=numberofdays+1
    tomorrow=[[forecastedate]]
    rbf30=rbf_svr.predict(day)
    poly30=poly_svr.predict(day)
    lin30=lin_svr.predict(day)
    rbft=rbf_svr.predict(tomorrow)
    polyt=poly_svr.predict(tomorrow)
    lint=lin_svr.predict(tomorrow)
    # print(comparison_price['Adj Close'])
    differencerbf=abs(((comparison_price['Adj Close']-rbf30)/((comparison_price['Adj Close']+rbf30)/2))*100)
    print("Price difference",differencerbf)
    differencepoly=abs(((comparison_price['Adj Close']-poly30)/((comparison_price['Adj Close']+poly30)/2))*100)
    differencelin=abs(((comparison_price['Adj Close']-lin30)/((comparison_price['Adj Close']+lin30)/2))*100)
    # print( "RBF Tomorrow Forecast:",rbft)
    # print( "Poly Tomorrow Forecast:",polyt)
    # print( "Lin Tomorrow Forecast:",lint)
    forecastdata={
        'hprices': priceslist,
        'days': daysarr,
        'rbfc': rbf30,
        'polyc': poly30,
        'linc': lin30,
        'rbft': rbft,
        'polyt': polyt,
        'lint': lint,
    }
    labels=[]
    for day in daysarr:
        labels.append(int(day[0]))

    values=[]
    for price in priceslist:
        values.append(price)
    # values.append(rbf30[0])
    # values.append( poly30[0])
    # values.append( lin30[0])
    # values.append( rbft[0])
    # values.append( polyt[0])
    # values.append( lint[0])
    # legend='Chart'
    print(labels)

    legend = 'Adjusted Close'
    # labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    # values = [10, 9, 8, 7, 6, 4, 7, 8]
  

    return render_template("forecast.html", forecastdata=forecastdata, labels=labels, values=values, legend=legend,)
    

@application.route('/stock/delete/<int:id>')
def delete_show(id):
    model_portfolio.Stock.delete({'id': id})
    return redirect('/loggedin')



