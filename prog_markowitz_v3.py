# -*- coding: utf-8 -*-
"""Prog Markowitz_V3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TqJ6cqNmNmfAtojFIKkzwosPEVqP9xBF

# ***MARKOWITZ PORTFOLIO OPTIMIZATION***

This code suggest an optimized portfolio based on your current one, improving your portfolio risk-return relation by maximizing its sharpe ratio, based on Markowitz Portfolio Theory.

First, it will analyse your current portfolio. Then, it will show your optimazed portfolio. You need just to insert the stocks on your portfolio, its weights, the money invested, start and end date for the analysed period. Use the sample test to have an idea of how the code its working. 

Hope this code fits you well,

Thiago Honda Mitsunari

## Install and import libraries
"""

!pip install PyPortfolioOpt
!pip install dython
!pip install yfinance

pip install yfinance --upgrade --no-cache-dir

#Import pandas programmms
import pandas as pd
import numpy as np
from pandas_datareader import data as web
from datetime import datetime
import matplotlib.pyplot as plt
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from matplotlib import figure
from pypfopt import risk_models
from pypfopt import expected_returns
from dython import nominal

plt.style.use('seaborn-bright')

"""## Run program"""

#Define Assets:
assets = input("Write the assets in your portfolio: ")
assets = assets.split()
 
#Define weights
weights = input("Write the weights of the assets on your portfolio: ")
weights = weights.split()
weights = np.array(weights, dtype=float)
 
#Invested money
money = int(input("How much money do you invest?"))
 
#Start and end day ---- Analysed period
startDate = input("Choose a start date: ")
endDate = input("Choose an end date: ")
today = datetime.today().strftime("%Y-%m-%d")
 
#End date: today or else
if endDate == "today":
  endDate = today
else:
  endDate = endDate
 
#Create DF with adj closing prices
df = yf.download(assets, data_source='yahoo', start = startDate, end = endDate)['Adj Close']
  
print('............................................................................................')
print("These are the adjusted closing prices for your stocks: ")
display(df)
 
#Daily return for the stocks:
returns = df.pct_change()
cumreturns = (returns+1).cumprod()
 
#Plotting graph: Cum return for stocks
plt.figure(figsize=(25,10))
for a in cumreturns.columns.values:
  plt.plot(cumreturns[a], label = a)
 
plt.title("Growth over time")
plt.xlabel('Date', fontsize = 18)
plt.ylabel('Growth', fontsize = 18)
plt.legend(df.columns.values, loc="upper left")
plt.show()
 
#Create and show the annulazied covar matrix
cov_matrix_annual = returns.cov()*252
 
#calculate the portfolio variance 
port_var = np.dot(weights.T, np.dot(cov_matrix_annual, weights)) #weights transposed * covar matrix * weights
 
#Calculate portfolio volatitlity(STDEV)
port_vol= np.sqrt(port_var)
 
#Annual portfolio return
portfolioSimpleAnnualReturn = np.sum(returns.mean() * weights * 252)  #mean return*weights*working days
portfolioSimpleAnnualReturn = np.sum(returns.mean() * weights * 252)
 
#Graph: Portfolio sum growth over time
portfolioDailyReturn = cumreturns
portfolioDailyReturn["Portfolio Return"] = (cumreturns*weights).sum(axis=1)
portfolioDailyReturn["Date"] = portfolioDailyReturn.index
portfolioDailyReturn.plot(x="Date", y="Portfolio Return", kind="line")

#Portfolio beta (Benchmark: Ibovespa)
portlogreturns = df.copy()
portlogreturns["portret"] = (df*weights).sum(axis=1)
portlogreturns["log"] = np.log(portlogreturns['portret']) - np.log(portlogreturns['portret'].shift(1))

ibovlogReturns = yf.download("^BVSP", data_source='yahoo', start = startDate, end = endDate)
ibovlogReturns['log'] = np.log(ibovlogReturns["Adj Close"]) - np.log(ibovlogReturns["Adj Close"].shift(1))

var = ibovlogReturns["log"].var()
covar = ibovlogReturns["log"].cov(portlogreturns["log"])

beta = covar/var


#portfolio correlation table 
nominal.associations(portfolioDailyReturn, figsize=(10,10),mark_columns=True)


#Expected annual return, volatility - risk, and variance
print('............................................................................................')
print("These are the values for you current portfolio: ")
percent_var = str( round(port_var,2) * 100)+ '%'
percent_vols = str( round(port_vol,2) *100)+'%'
percent_ret = str( round(portfolioSimpleAnnualReturn,2)*100)+'%'
beta = str(round(beta,3))
 
print("Expected annual return: " + percent_ret)
print("Annual volatility/risk: " + percent_vols)
print("Annual variance: " + percent_var)
print("Beta: " + beta)
print('............................................................................................')
 
 
#Portfolio optimization:
#Calcuate the expected return and the annualize sample covariance matrix ond assets returns
mu = expected_returns.mean_historical_return(df)                   #CAPM
s = risk_models.sample_cov(df)                                     #Expected return = RF rate + Beta*Market risk premium
                              
print("These are the values for you optimazed portfolio: ")
#Optimize for max sharpe ratio
ef = EfficientFrontier(mu, s)
weights = ef.max_sharpe()
cleaned_weights = ef.clean_weights()
print(cleaned_weights)
ef.portfolio_performance(verbose = True)
 
print('............................................................................................')         #https://pyportfolioopt.readthedocs.io/en/latest/
print('This is how your portfolio should be composed: ')
#Get the discrete allocation of each share per stock
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
 
latest_prices = get_latest_prices(df)
weights = cleaned_weights
da = DiscreteAllocation(weights, latest_prices, total_portfolio_value = money)
 
allocation, leftover = da.lp_portfolio()
print("Dicscreate allocation: ", allocation)
print("Funds remaining: ${:.2f}".format(leftover))
 
#-------------- SAMPLE TEST --------------------#
# ASSETS:            TSLA BEEF3.SA EQTL3.SA HGLG11.SA IGTA3.SA KNRI11.SA MRFG3.SA PETR3.SA SAPR4.SA FB TAEE3.SA WIZS3.SA
# WEIGHTS :          0.09 0.08 0.05 0.09 0.16 0.1 0.1 0.09 0.07 0.03 0.11 0.3
# INVESTMENT:        10000
# Start date:        2017-01-01
# End date:          today                or        01-01-2020


# ^GSPC PRIO3.SA BABA BTC-USD TAEE3.SA ITSA4.SA KNRI11.SA
# 0.26 0.9 0.1 0.14 0.15 0.12 0.13

"""NOTES:

About the current version:
 - Date form: Month/Day/Year
 - The programm will not function if one of your stocks does not have data, check the adjusted closing prices table for n/a values
 - If you input the end date as today, the graphs will plot the expected return for the stocks and current portfolio (it will be a straight line) 

For next version will be added:
 - Beta for current and optimized portfolio
 - Graph for optimized portfolio
 - Efficient Frontier plot

"""