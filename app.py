from logging import fatal
import os
import json
from tabnanny import check
import rel
from dotenv import load_dotenv
from luno_python.client import Client

load_dotenv()

KEY_ID = os.getenv("KEY_ID")
KEY_SECRET = os.getenv("KEY_SECRET")

authData = json.dumps({
    "api_key_id": KEY_ID,
    "api_key_secret": KEY_SECRET
})

# print(KEY_ID, KEY_SECRET)

c = Client(api_key_id=KEY_ID, api_key_secret=KEY_SECRET)
client_id = c.get_balances('IDR')['balance'][0]['account_id']

# Check IDR balance
# If IDR > 700k, return true
# else return false
def checkBalance(client):
    try:
        result = client.get_balances('IDR')['balance'][0]['balance']
        return float(result) if float(result) > 700000 else False
    except Exception as e:
        print(e)
        return False

# Get top 100 order book based on pair and step
def getTopOrderBook(client, step):
    if step == 1:
        try:
            resultFirst = client.get_order_book('XBTIDR')['asks']
            return resultFirst
        except Exception as e:
            print(e)
            return False
    if step == 2:
        try:
            resultSecond = client.get_order_book('ETHXBT')['asks']
            return resultSecond
        except Exception as e:
            print(e)
            return False
    if step == 3:
        try:
            resultThird = client.get_order_book('ETHIDR')['bids']
            return resultThird
        except Exception as e:
            print(e)
            return False

# Get triangular arbitrage percentage based on top 1 order book
def getPercentage(first, second, third):
    percentage = ((float(third[0]['price']) / float(second[0]['price'])) / float(first[0]['price'])) * 100
    return percentage

def getBestPrice(first, second, third):
    cleanPrices = {}
    cleanPrices['1'] = float(first[0]['price']) * float(first[0]['volume'])
    cleanPrices['2'] = float(second[0]['price']) * float(second[0]['volume']) * float(first[0]['price'])
    cleanPrices['3'] = float(third[0]['price']) * float(third[0]['volume'])
    
    lowestPrice, bestPrice = min(cleanPrices.items(), key=lambda x:x[1])
    print(f'bestprice is {lowestPrice} with volume {bestPrice}')
    
    return lowestPrice
    
    # volume1 = bestPrice / float(first[0]['price'])
    # volume2 = bestPrice / (float(second[0]['price']) * float(third[0]['price']))
    # volume3 = bestPrice / float(third[0]['price'])
    
    # return "{:.6f}".format(volume1), "{:.6f}".format(volume2), "{:.6f}".format(volume3)
    
def getTransactionVolume(lowestPrice):
    print(type(lowestPrice))
    

# Create market order
def createOrder(client, price1, volume1, price2, volume2, price3, volume3):
    try:
        client.post_limit_order('XBTIDR', price1, 'ASK', volume1)
        try:
            client.post_limit_order('ETHXBT', price2, 'ASK', volume2)
            try:
                client.post_limit_order('ETHIDR', price3, 'BID', volume3)
            except Exception as e:
                print('error 3rd: ', e)
                return
        except Exception as e:
            print('error 2nd: ', e)
            return    
    except Exception as e:
        print('error 1st: ', e)
        return
    
    print('triagular arbitrage done')

while True:
    first = getTopOrderBook(c, 1)
    second = getTopOrderBook(c, 2)
    third = getTopOrderBook(c, 3)
    
    print(f'price1: {first[0]["price"]}. volume1: {first[0]["volume"]}')
    print(f'price2: {second[0]["price"]}. volume2: {second[0]["volume"]}')
    print(f'price3: {third[0]["price"]}. volume3: {third[0]["volume"]}')
    
    percentage = getBestPrice(first, second, third)
    print(f'percentage is {percentage}')
    
    if percentage > 100.5:
        price1 = first[0]['price']
        price2 = second[0]['price']
        price3 = third[0]['price']
        volume1, volume2, volume3 = getVolume(first, second, third)
        print(price1, price2, price3)
        print(type(price1), type(price2), type(price3))
        print(volume1, volume2, volume3)
        print(type(volume1), type(volume2), type(volume3))
        # createOrder(c, price1, volume1, price2, volume2, price3, volume3)
        break

# first = getTopOrderBook(c, 1)
# second = getTopOrderBook(c, 2)
# third = getTopOrderBook(c, 3)
# print(c.get_balances('IDR')['balance'][0]['account_id'])