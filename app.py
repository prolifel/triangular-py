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

def checkBalance(client, currency):
    try:
        result = client.get_balances(currency)['balance'][0]['balance']
        return float(result)
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
    percentage = ((float(third['price']) / float(second['price'])) / float(first['price'])) * 100
    return percentage

def getBestPrice(first, second, third):
    cleanPrices = {}
    cleanPrices['1'] = float(first['price']) * float(first['volume'])
    cleanPrices['2'] = float(second['price']) * float(second['volume']) * float(first['price'])
    cleanPrices['3'] = float(third['price']) * float(third['volume'])
    
    lowestPair, bestPrice = min(cleanPrices.items(), key=lambda x:x[1])
    print(f'lowestPair is {lowestPair} with price {bestPrice}')
    
    return float(bestPrice)

    
def getTransactionVolume(client, bestPrice, first, second):
    balanceIDR = checkBalance(client, 'IDR')
    if balanceIDR >= bestPrice:
        volume1 = bestPrice / float(first["price"])
    else:
        volume1 = balanceIDR / float(first["price"])
    
    # volume1 = balanceIDR / float(first["price"])
    volume2 = 99.8 / 100 * volume1 / float(second["price"])
    volume3 = 99.9 / 100 * volume2
    
    # kalau volume > 0.00015, execute
    
    return "{:.6f}".format(volume1), "{:.6f}".format(volume2), "{:.6f}".format(volume3)
    
# Create market order
def createOrder(client, price1, volume1, price2, volume2, price3, volume3):
    try:
        client.post_limit_order('XBTIDR', price1, 'ASK', volume1, post_only=True)
        try:
            client.post_limit_order('ETHXBT', price2, 'ASK', volume2, post_only=True)
            try:
                client.post_limit_order('ETHIDR', price3, 'BID', volume3, post_only=True)
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
    first = getTopOrderBook(c, 1)[0]
    second = getTopOrderBook(c, 2)[0]
    third = getTopOrderBook(c, 3)[0]
    
    # print(f'price1: {first["price"]}. volume1: {first["volume"]}')
    # print(f'price2: {second["price"]}. volume2: {second["volume"]}')
    # print(f'price3: {third["price"]}. volume3: {third["volume"]}')
    
    percentage = getPercentage(first, second, third)
    print(f'percentage is {percentage}')
    
    if percentage > 100.5:
        price1 = first['price']
        price2 = second['price']
        price3 = third['price']
        volume1, volume2, volume3 = getTransactionVolume(c, getBestPrice(first, second, third), first, second)
        
        # print(price1, price2, price3)
        # print(type(price1), type(price2), type(price3))
        # print(volume1, volume2, volume3)
        # print(type(volume1), type(volume2), type(volume3))
        createOrder(c, price1, volume1, price2, volume2, price3, volume3)
        break
