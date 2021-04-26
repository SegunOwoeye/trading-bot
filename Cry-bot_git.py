#Notes this projects currently runs in python 3.6.5 32 Bit

#Importing modules to be used for creating the trading bot
import os
from os import environ
import time
import numpy as np
import math
from datetime import datetime
from binance.client import Client
from binance.enums import *

os.system('cls') #Clears the terminal

#Api keys
apikey = environ['apikey']
Sec_apikey = environ['Sec_apikey']
client = Client(apikey,Sec_apikey)#When returns true,  user has logged onto Api

print("=============")
print("||logged in||")
print("=============")
print("")


#Functions get the average for the past 10 units

"""
For the scope of this project, the price of BNB will be looked at the
on an hourly basis (1 Hr)
"""
def gathering_closing_prices():
    #NOTES:
        #Klines are the same thing as candle sticks
        #As aim is to use 1 hour interval from past days use: "KLINE_INTERVAL_1HOUR"
        #OHLCV: Opens, High, Low, Close, Volume
        
        #order of how to read kline array
        #[Not Known, Open, High,Low, Close, Volume, Note Known,TXN]
        #[1618963200000, '0.01040000', '0.01100000', '0.01017900', '0.01033960', '832944.00000000', 1619006399999, '8823.24816912', 453487, '433519.78000000', '4593.18605919', '0']

    #Trading: buying BNB using GBP | UTC is the same as GMT
    klines = client.get_historical_klines("BNBGBP", Client.KLINE_INTERVAL_1HOUR, "10 hours ago UTC") #3Hour lag glitch
    BNB_in_GBP_Closing_Price = []
    #Goes through list of Klines, obtaining the OHLCV data
    #Takes the last 10 closing averages within a 10 hour period
    for i in range(10):
        Live_coin_data = klines[i]
        BNB_in_GBP_Closing_Price.append(str(Live_coin_data[4]))

    return BNB_in_GBP_Closing_Price
    
#Gets the moving average of BNBGBP across 5 units
def five_unit_MA():
    BNB_in_GBP_Closing_Price = gathering_closing_prices()
    BNB_in_GBP_Closing_price_5_units = []

    #This takes the last 5 closing prices
    for i in range(5): #number of places in list is 9
        BNB_in_GBP_Closing_price_5_units.append(BNB_in_GBP_Closing_Price[len(BNB_in_GBP_Closing_Price)-1-i])

    #Calculating the 5 unit moving average
    MA_5 = 0
    for n in range(5):
        MA_5 += float(BNB_in_GBP_Closing_price_5_units[n])
    MA_5 = MA_5/5
    MA_5 = round(MA_5, 3)

    return MA_5

#Gets the moving average of BNBGBP across 10 units
def ten_unit_MA():
    BNB_in_GBP_Closing_Price = gathering_closing_prices()

    #Calculating the 10 unit moving average
    MA_10 = 0
    for n in range(10):
        MA_10 += float(BNB_in_GBP_Closing_Price[n])
    MA_10 = MA_10/10
    MA_10 = round(MA_10, 3)

    return MA_10

#Goes back 1 hours to check whether the slope leading up t0 MA(5) is positive or negative
def five_MA_State():
    BNB_in_GBP_Closing_Price = gathering_closing_prices()
    BNB_in_GBP_Closing_price_7_units = []

    #This takes the last 7 closing prices
    for i in range(7): #number of places in list is 9
        BNB_in_GBP_Closing_price_7_units.append(BNB_in_GBP_Closing_Price[len(BNB_in_GBP_Closing_Price)-1-i])

    #Calculating the 5 unit moving average 1 hour ago (Working)
    MA_5_1hr = 0
    for n in range(1,6):
        MA_5_1hr += float(BNB_in_GBP_Closing_price_7_units[n])
    MA_5_1hr = MA_5_1hr/5
    MA_5_1hr = round(MA_5_1hr, 3)
   
    five_unit_slope = (five_unit_MA()-MA_5_1hr)/2
    
    return five_unit_slope

#Goes back 1 hours to check whether the slope leading up t0 MA(10) is positive or negative
def ten_MA_State():
    klines = client.get_historical_klines("BNBGBP", Client.KLINE_INTERVAL_1HOUR, "11 hours ago UTC") #+3 the origional value
    BNB_in_GBP_Closing_Price_11_units = []
    #Goes through list of Klines, obtaining the OHLCV data
    #Takes the last 11 closing averages within a 10 hour period
    for i in range(11):

        Live_coin_data = klines[i]
        BNB_in_GBP_Closing_Price_11_units.append(str(Live_coin_data[4]))

    #Calculating the 5 unit moving average 1 hour ago (Working)
    MA_10_1hr = 0
    for n in range(1,11):
        MA_10_1hr += float(BNB_in_GBP_Closing_Price_11_units[n])
    MA_10_1hr = MA_10_1hr/10

    ten_unit_slope = (ten_unit_MA()-MA_10_1hr)/2
    
    return ten_unit_slope

#Stating if Slope of MA(5) is positive or negative
def stating_five_unit_state():
    if five_MA_State() > 0:
        return "POSITIVE"

    elif five_MA_State() < 0:
        return "NEGATIVE"
        
    else:
        return "An unknown error has occurred"

#Stating if Slope of MA(10) is positive or negative
def stating_ten_unit_state():
    if ten_MA_State() > 0:
        return "POSITIVE"

    elif ten_MA_State() < 0:
        return "NEGATIVE"
        
    else:
        return "An unknown error has occurred"

#Checking whether the MA(5) and MA(10) have crossed
def MA_cross_check():
    """
    If the absolute value of the difference between MA(5) and MA(10)
    rounded to a whole number is 0, then the moving averages count as crossing
    """
    cross_MA_Value = abs(five_unit_MA()-ten_unit_MA())
    cross_MA_Value = round(cross_MA_Value)

    if cross_MA_Value == 0:
        return "CROSSED"

    else:
        return "NOT CROSSED"
    
#Tells computer what to do from getting the state of the slopes
def buy_or_sell_state(): #Create more analysis
    if stating_five_unit_state() == "POSITIVE" and stating_ten_unit_state() == "POSITIVE":
        return "CONSIDERING to BUY"

    elif stating_five_unit_state() == "NEGATIVE" or stating_ten_unit_state()  == "NEGATIVE":
        return "CONSIDERING to SELL"

    else:
        return "An error has occurred"
        
#Checks Current GBP Balance
def GBP_balance_checker():
    #Allawable limit of three decimal places (0.000)
    GBP_balance = client.get_asset_balance(asset='GBP') # Gets information on balance
    GBP_balance_values =GBP_balance.values()#Gets the values of GBP Balance
    GBP_Balance_list = list(GBP_balance_values)#Turns the values into a list
    GBP_balance = GBP_Balance_list
    Number_of_GBP = float(GBP_balance[1])#Takes the number of GBP tokens from the Lists
    RNumber_of_GBP = round((Number_of_GBP-0.001), 3)#Rounds GBP down to 3 decimal places
    
    return (RNumber_of_GBP)

#Checks Current BNB Balance
def BNB_balance_checker():
    #Allawable limit of three decimal places (0.000)
    BNB_balance = client.get_asset_balance(asset='BNB') # Gets information on balance
    BNB_balance_values =BNB_balance.values()#Gets the values of BNB Balance
    BNB_Balance_list = list(BNB_balance_values)#Turns the values into a list
    BNB_balance = BNB_Balance_list
    Number_of_BNB = float(BNB_balance[1])#Takes the number of BNB tokens from the Lists
    RNumber_of_BNB = abs(round((Number_of_BNB-0.001), 3))#Rounds BNB down to 3 decimal places
    if RNumber_of_BNB < 0:
        return 0
    else:
        return (RNumber_of_BNB)

#Confirming whether to buy or sell
def Buy_or_sell_decision():
    #Using if or else function
    if MA_cross_check() == "CROSSED": # Checks to see if moving averages have cross
        if five_unit_MA()>ten_unit_MA():#Buyers Market
            print("Time to Buy")
            if str(stating_five_unit_state()) == "POSITIVE" and str(stating_ten_unit_state()) == "POSITIVE":
                print("Checks Complete, Purchasing BNB")
                BNB_Buy()

            else: # Wait for 1 hour 30 minutes to see if it's time to all checks give green light, if not, won't do anything
                print("Conditions not yet met, waiting")
                time.sleep(60*60+60*60/2)
                if str(stating_five_unit_state()) == "POSITIVE" and str(stating_ten_unit_state()) == "POSITIVE":
                    print("Checks Complete, Purchasing BNB")
                    BNB_Buy()

                else:
                    return

        elif ten_unit_MA()>five_unit_MA(): # Sellers market
            print("Time to Sell") 
            Sell_BNB_to_GBP()

        else:
            print("Error")

    else:
        print("Waiting for Moving Averages to Cross")
 
#Purchases BNB  
def BNB_Buy():
    all_coin_price = client.get_all_tickers() #Gets the current price of 1 BNB in GBP
    GBP_Balance = GBP_balance_checker()

    
    #Checks to see my the current rates of 1BNB to GBP, and tells how much BNB I can buy with current balance
    for i in range(3000): 
        
        all_coin_prices = list(all_coin_price[i].values())
        if all_coin_prices[0] == "BNBGBP": #Matches up symbol
            BNBGBP_Price = all_coin_prices[1] # Gets the current price of 1 BNB in GBP
            GBP_quantity = GBP_Balance/float(BNBGBP_Price) 
            GBP_quantity = round((GBP_quantity-0.001),3) #Quantity of BNB I can buy with GBP to 1 decimal place
            
            try:
                order = client.create_order(
                    symbol = "BNBGBP",
                    side = SIDE_BUY,
                    type = ORDER_TYPE_MARKET,
                    quantity = GBP_quantity, #Number of Coins BNB
                )

                break
            except:
                break
        else:
            pass

#Checks to see if it's profitable to purchase BNB or not
def BNB_Sell_profitability_checker():
    #Buys GBP Using BNB
    all_coin_price = client.get_all_tickers() #Gets the current price of 1 BNB in GBP
    trades = client.get_my_trades(symbol='BNBGBP')

    #Checks to see what the price was the last time BNB was purchased from account
    recent_purchase = [] #List to get the most recent purchase price
    for i in range(len(trades)):
        historical_trades = trades[i]
        if historical_trades['isBuyer'] == True: # Checks to see if the trades made were a purchase order or a sell order
            if i+1 == (len(trades)):
                recent_purchase.append(historical_trades["price"])#Makes sure that the purchase price is the most recent one

            else:
                pass

        else:
            pass
    recent_purchase_price = recent_purchase[0]

    #Getting the Price of 1 BNB in GBP
    for i in range(3000):
        all_coin_prices = list(all_coin_price[i].values())
        if all_coin_prices[0] == "BNBGBP": #Matches up symbol
            BNBGBP_Price = all_coin_prices[1] # Gets the current price of 1 BNB in GBP
            
            break

    #Checks whether it is profitable to sell BNB or not
    if recent_purchase_price < BNBGBP_Price:

        return "Profitable"

    else:
        return "Not-Profitable"

#Sells BNB on the assumption that BNB_Sell_profitability_checker() has deemed the sell order to be profitable
def Sell_BNB_to_GBP():
    if BNB_Sell_profitability_checker() == "Profitable":
        print("Selling BNB")
        try:
            order = client.create_order(
                symbol = "BNBGBP",
                side = SIDE_SELL,
                type = ORDER_TYPE_MARKET,
                quantity = BNB_balance_checker(), #Number of BNB used to Purchase GBP
            )
        except:
            pass

    elif str(BNB_Sell_profitability_checker) == "Not-Profitable":
        print("Not Selling yet, wait 30 minutes")
        time.sleep(60*60/2)
        
        if str(BNB_Sell_profitability_checker) == "Profitable": #Checks again to see if trade will be profitable
            print("Selling BNB")

            try:
                order = client.create_order(
                    symbol = "BNBGBP",
                    side = SIDE_SELL,
                    type = ORDER_TYPE_MARKET,
                    quantity = BNB_balance_checker(), #Number of BNB used to Purchase GBP
                )

            except:
                pass

        else:
            pass

    else:
        print('Error')
    
#Main Execution Function
def Starter_function():
    print("GBP Balance " + str(GBP_balance_checker()))
    print("BNB Balance " + str(BNB_balance_checker()))
    print("")
    print("MA(5): " + str(five_unit_MA()))
    print("MA(10): " + str(ten_unit_MA()))
    print("MA(5) has a " + str(stating_five_unit_state()) + " Slope: " + str(five_MA_State()))
    print("MA(10) has a " + str(stating_ten_unit_state()) + " Slope: " + str(ten_MA_State()))
    print("Moving Averages have " + MA_cross_check())
    print(str(buy_or_sell_state()))
    print('')#Spacer
    Buy_or_sell_decision() #Makes a decision on whether it's time to buy or sell crypto depending on market information
    time.sleep(60*30) #Function Checks live data every 30 minutes 
    Starter_function() #Loops the function again

#Initialising starter function
Starter_function()

