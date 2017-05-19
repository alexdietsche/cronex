# import random
# import sys
# import os
import quandl
import numpy as np
import json
from datetime import datetime, timedelta

# Enter access key
quandl.ApiConfig.api_key = 'uMWdUQWSsVs4ge6zF5yb'

# Variables
discount_rate = 15
safety_margin = 25

# Current date
date_ = datetime.today() - timedelta(days=4)
date = date_.strftime("%Y-%m-%d")

# Read tickers
with open('../res/ticker.txt') as jsonfile:
    companies = json.load(jsonfile)

# loop through all tickers
for company in companies['Data']:

    stock_price_dataframe = quandl.get_table('WIKI/PRICES',
                                             ticker=company['Ticker'],
                                             qopts={'columns': 'close'},
                                             date={'gte': date},
                                             paginate=True)

    eps_dataframe = quandl.get('SF0/' + company['Ticker'] + '_EPS_MRY')
    ek_dataframe = quandl.get('SF0/' + company['Ticker'] + '_BVPS_MRY')
    fcf_dataframe = quandl.get('SF0/' + company['Ticker'] + '_BVPS_MRY')
    revenue_dataframe = quandl.get('SF0/' + company['Ticker'] + '_REVENUE_MRY')

    if stock_price_dataframe.empty or eps_dataframe.empty or ek_dataframe.empty or fcf_dataframe.empty:
        continue

    stock_price = stock_price_dataframe.get_value(0, 'close')  # last closing price
    eps = eps_dataframe['Value'].values  # earnings per share
    ek = ek_dataframe['Value'].values  # equity (book value per share)
    revenue = revenue_dataframe['Value'].values  # revenue
    fcf = fcf_dataframe['Value'].values  # free cash flow

    # Calculate price proposition
    eps_ttm = eps[-1]  # earnings per share trailing twelve months

    if eps_ttm < 0 or ek[-1] < 0 or ek[0] < 0:
        continue

    # Growth

    '''
    
    Improvements:
    - Use least square to calculate growth, ignore outsiders
    - Only consider companies that exceed a certain market valuation (yet to be determined)
    - output format should be search- & filterable (CVS, JSON)
    - find a way to download multiple companies with one api call (takes ages to load all)
    - growth rates should be labeled with a significance factor (volatile BAD, constant GOOD)
    - growth rates should influence final valuation
    
    Assess Model accuracy (with google cloud machine learning engine):
    - Calculate mean error of predicted and actual stock price
    - Find better growth indicators (determine of eps or ek is more significant)
    - Gain access to larger databases (historical fundamentals approximately 20+ years)
    
    Soft Factors:
    - Asses management solely with data?
    - management should influence final valuation
    
    '''

    ek_growth = pow(ek[-1] / ek[0], 1 / (len(ek) - 1)) - 1
    eps_growth = pow(eps[-1] / eps[0], 1 / (len(eps) - 1)) - 1
    revenue_growth = pow(revenue[-1] / revenue[0], 1 / (len(revenue) - 1)) - 1
    fcf_growth = pow(fcf[-1] / fcf[0], 1 / (len(fcf) - 1)) - 1

    # Calculate Growth with least square

    A_ek = np.vstack([range(len(ek)), np.ones(len(ek))]).T
    ek_growth_lstsq = pow(np.linalg.lstsq(A_ek, ek)[0][0], 1/(len(ek)-1)) -1


    eps_future = eps_ttm * pow(1 + ek_growth, len(ek) - 1)
    pe = 18  # Find a way to calculate price earning ratio <-------------------------------------
    stock_price_future = eps_future * pe
    stock_price_discounted = stock_price_future / pow(1 + discount_rate / 100, len(ek))
    stock_price_proposition = stock_price_discounted * (1 - safety_margin / 100)

    if stock_price_proposition > stock_price:
        output_file = open('../output/invest.txt', 'a')  # File with undervalued stocks

        output_file.write('Stock: ')
        output_file.write(company['Name'])
        output_file.write('\n\n')
        output_file.write('Current Price: ')
        output_file.write(str(stock_price))
        output_file.write('\n')
        output_file.write('Price Proposition: ')
        output_file.write(str(stock_price_proposition))
        output_file.write('\n\n')
        output_file.write('Growth: \n')
        output_file.write('EK: ')
        output_file.write(str(ek_growth))
        output_file.write('\n')
        output_file.write('EPS: ')
        output_file.write(str(eps_growth))
        output_file.write('\n')
        output_file.write('REVENUE: ')
        output_file.write(str(revenue_growth))
        output_file.write('\n')
        output_file.write('FREE CASHFLOW: ')
        output_file.write(str(fcf_growth))
        output_file.write('\n\n\n')

        output_file.close()

    print(company['Name'])