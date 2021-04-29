import ccxt
import settings
import time
from pprint import pprint

# client は取引所によって調整可能
# ex.
# bybit -> ccxt.bybit()
# binance -> ccxt.binance()
client = ccxt.bitget()

# set API key, secret and password
client.apiKey = settings.API_KEY
client.secret = settings.SECRET_KEY
client.password = settings.PASSWORD

# この辺りは取引所に応じて調整する
# ex.
# bybit -> BTCUSD
# binance -> BTCUSDT (spot) 
SYMBOL = 'CMT_BTCUSDT'
CANDLE_INTERVAL = '1m'

RSI_SIZE = 14
NUM_CANDLE = 150

BUY_RSI = 30
SELL_RSI = 45
UNIT_AMOUNT = '1'
has_position = False

def get_prices(client, symbol, timeframe, length):
    res = client.fetchOHLCV(symbol, timeframe=timeframe, limit=length)
    prices = []
    for i in range(len(res)):
        prices.append(res[i][4])

    return prices

def RSI(prices, length):
    base_price = None
    positive = []
    negative = []
    rsi = []
    up = 0
    down = 0
    alpha = 1 / length

    positive.append(0)
    negative.append(0)
    rsi.append(0)
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff < 0:
            u = 0
            d = abs(diff)
        else:
            u = diff
            d = 0
        
        up = (1.0 - alpha) * positive[i - 1] + alpha * u
        positive.append(up)
        down = (1.0 - alpha) * negative[i - 1] + alpha * d
        negative.append(down)
        r = 0
        if down != 0:
            r = 100 - (100 / (1 + up / down))
        rsi.append(r)
    
    print("RSI: ", rsi[-1])

    return rsi[-1]


while True:
    try:
        prices = get_prices(client, SYMBOL, CANDLE_INTERVAL, NUM_CANDLE)
        rsi = RSI(prices, RSI_SIZE)

        # RSI が基準より低く、ポジション無いときに買う
        if rsi < BUY_RSI and not has_position:
            res = client.createOrder(
                symbol=SYMBOL,
                type='market',
                side='buy',
                amount=UNIT_AMOUNT,
                params={
                    'type': '1',
                }
            )
            has_position = True
            pprint(res)
        
        # RSI が基準より高く、ポジションがあるときに売る
        if rsi > SELL_RSI and has_position:
            res = client.createOrder(
                symbol=SYMBOL,
                type='market',
                side='sell',
                amount=UNIT_AMOUNT,
                params={
                    'type': '3',
                }
            )
            has_position = False
            pprint(res)
        
    except Exception as e:
        print(e)

    time.sleep(10)


