import hmac
import hashlib
import requests
import sys
import time
import base64
import json
from collections import OrderedDict

class Fcoin():
    def __init__(self,base_url = 'https://api.fcoin.com/v2/'):
        self.base_url = base_url

    def auth(self, key, secret):
        self.key = key
        self.secret = secret

    def public_request(self, method, api_url, **payload):
        """request public url"""
        r_url = self.base_url + api_url
        try:
            r = requests.request(method, r_url, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        if r.status_code == 200:
            return r.json()

    def get_signed(self, sig_str):
        """signed params use sha512"""
        # sig_str = base64.b64decode(bytes(sig_str))
        sig_str = base64.b64encode(sig_str)
        signature = base64.b64encode(hmac.new(self.secret, sig_str, digestmod=hashlib.sha1).digest())
        #print(signature)
        return signature


    def signed_request(self, method, api_url, **payload):
        """request a signed url"""

        param=''
        if payload:
            sort_pay = payload.items()
            sort_pay.sort()
            for k in sort_pay:
                param += '&' + str(k[0]) + '=' + str(k[1])
            param = param.lstrip('&')
        timestamp = str(int(time.time() * 1000))
        full_url = self.base_url + api_url

        if method == 'GET':
            if param:
                full_url = full_url + '?' +param
            sig_str = method + full_url + timestamp
        elif method == 'POST':
            sig_str = method + full_url + timestamp + param

        signature = self.get_signed(sig_str)

        headers = {
            'FC-ACCESS-KEY': self.key,
            'FC-ACCESS-SIGNATURE': signature,
            'FC-ACCESS-TIMESTAMP': timestamp

        }

        try:
            r = requests.request(method, full_url, headers = headers, json=payload)

            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)
        if r.status_code == 200:
            return r.json()


    def get_server_time(self):
        """Get server time"""
        return self.public_request('GET','/public/server-time')['data']


    def get_currencies(self):
        """get all currencies"""
        return self.public_request('GET', '/public/currencies')['data']

    def get_symbols(self):
        """get all symbols"""
        return self.public_request('GET', '/public/symbols')['data']

    def get_market_ticker(self, symbol):
        """get market ticker"""
        return self.public_request('GET', 'market/ticker/{symbol}'.format(symbol=symbol))

    def get_market_depth(self, level, symbol):
        """get market depth"""
        return self.public_request('GET', 'market/depth/{level}/{symbol}'.format(level=level, symbol=symbol))

    def get_trades(self,symbol):
        """get detail trade"""
        return self.public_request('GET', 'market/trades/{symbol}'.format(symbol=symbol))

    def get_balance(self):
        """get user balance"""
        return self.signed_request('GET', 'accounts/balance')

    def list_orders(self, **payload):
        """get orders"""
        return self.signed_request('GET','orders', **payload)

    def show_orders(self, symbol):
        """get orders"""
        return self.list_orders(symbol=symbol, states='canceled',before='3')

    def create_order(self, **payload):
        """create order"""
        return self.signed_request('POST','orders', **payload)

    def buy(self,symbol, price, amount):
        """buy something"""
        return self.create_order(symbol=symbol, side='buy', type='limit', price=str(price), amount=amount)

    def sell(self, symbol, price, amount):
        """sell someting"""
        return self.create_order(symbol=symbol, side='sell', type='limit', price=str(price), amount=amount)

    def get_order(self,order_id):
        """get specfic order"""
        return self.signed_request('GET', 'orders/{order_id}'.format(order_id=order_id))

    def cancel_order(self,order_id):
        """cancel specfic order"""
        return self.signed_request('POST', 'orders/{order_id}/submit-cancel'.format(order_id=order_id))

    def order_result(self, order_id):
        """check order result"""
        return self.signed_request('GET', 'orders/{order_id}/match-results'.format(order_id=order_id))
    def get_candle(self,resolution, symbol, **payload):
        """get candle data"""
        return self.public_request('GET', 'market/candles/{resolution}/{symbol}'.format(resolution=resolution, symbol=symbol), **payload)
    def sell_all(self,symbol,price,amount):
        """sell all based on price, type int only, float is not acceptable"""
        sell_price  =   float(price)
        sell_price  =   round(sell_price, 8)
        sell_volumn =   amount
        result      =   self.sell(symbol, sell_price, sell_volumn)
        sell_id     =   result['data']
        print result
        sell_cycle_time = 0
        while True:
            time.sleep(24)
            result = self.get_order(sell_id)
            print result
            filled = result['data']['filled_amount']
            if int(float(filled)) == sell_volumn:
                print('sell order done !')
                break;
            sell_cycle_time = sell_cycle_time + 1
            if sell_cycle_time%5 == 0:
                print 'Sell price is too high, cancel order,try again'
                self.cancel_order(sell_id)
                time.sleep(1)
                sell_price      =   sell_price*0.9999 ## price down 0.001
                sell_price      =   round(sell_price,8) ## keep 8 decimal
                sell_volumn     =   sell_volumn - int(float(filled))
                result          =   self.sell(symbol, sell_price, sell_volumn)
                sell_id         =   result['data']
                print ('sell_price  = ',sell_price)
                print ('sell_volumn = ',sell_volumn)
        return 0


    def safe_cancel_order(self,order_id):
        result = self.get_order(buy_id)
        #result = fcoin.show_orders('fteth')
        #print result
        filled = result['data']['filled_amount']
        #print int(filled)
        if float(filled) != 0.0 :
            self.cancel_order(buy_id)
            return 0 
        else:
            print '## Can not cancel as order totally done already!'
            return result





