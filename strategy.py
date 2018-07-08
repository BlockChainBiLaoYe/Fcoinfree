from fcoin import Fcoin

#if python3 use fcoin3
#from fcoin3 import Fcoin
import json
import sys
import time 
import base64



key2 		=	'your key'
secret2 	=	'your secret'

class Strategy():
	## fteth1:
	## buy condition:  first buy price , once failed try again;
	## sell condition: sell out with buy_price*profit_margin
	## once failed, down price to previously one *99.9%;
	## try sell again until all sold out;
	def fteth(self, profit_margin, volumn_rate):
		fcoin = Fcoin()
		#print(fcoin.get_symbols())

		fcoin.auth(key2, secret2) 

		balance = (fcoin.get_balance())['data']

		for i in balance:
			if i['currency'] == u'eth' :
				#print i
				eth_balance 	=	i['balance']
				eth_available	=	i['available']
				if eth_balance != eth_available:
					print('Warning: Some ETH frozen: ', i)
					sys.exit(0)

		for i in balance:
			if i['currency'] == u'ft' :
				#print i
				ft_balance 		=	i['balance']
				ft_available	=	i['available']
				if ft_available != ft_balance:
					print('Warning: Some FT frozen: ', i)
					sys.exit(0)

		result=(fcoin.get_market_ticker(u'fteth'))
		#result=(fcoin.get_currencies())
		#print(result)
		#print(result['status'])
		#print(result['data']['ticker'])

		_latest_trans_price	=	result['data']['ticker'][0]
		_latest_volumn  	= 	result['data']['ticker'][1]
		_max_buy_price 		=	result['data']['ticker'][2]
		_max_buy_volumn		=	result['data']['ticker'][3]
		_min_sell_price		= 	result['data']['ticker'][4]
		_min_sell_volumn	= 	result['data']['ticker'][5]

		#buy_price 	=	_latest_trans_price*0.92
		buy_price 	=	_latest_trans_price*1.0
		buy_price 	= 	round(buy_price,8) ## keep 8 decimal
		can_buy_ft 	=	int(float(eth_available)/buy_price)
		buy_volumn 	=	int (float(can_buy_ft)*float(volumn_rate))

		result 	=	fcoin.buy('fteth', buy_price, buy_volumn)


		sell_price 	= 	buy_price * (1.0 + profit_margin)
		sell_price 	= 	round(sell_price,8) ## keep 8 decimal
		sell_volumn = 	buy_volumn  # sell all 

		print ('ticker fteth latest price:' ,_latest_trans_price)
		print ("order_price = ", buy_price, "order_volumn = ",buy_volumn)
		print ("sell_price  = " , sell_price)

		#print result
		buy_id	=	result['data']
		buy_order_done  = 0;
		sell_order_done = 0;
		#buy_id_decode = base64.b64decode(bytes(buy_id))
		print buy_id
		#print buy_id_decode
		buy_cycle_time 	= 	3   ## wait 5 seconds * 3 times = 15 seconds 
		sell_cycle_time =	180	## wait 10 seconds  * 180 times = 30 mins 
		while (buy_cycle_time>0):
			time.sleep(5)
			result = fcoin.get_order(buy_id)
			#result	= fcoin.show_orders('fteth')
			#print result
			filled = result['data']['filled_amount']
			#print int(filled)
			if int(float(filled)) == buy_volumn:
				print('buy order done !')
				buy_order_done = 1
				break;
			buy_cycle_time = buy_cycle_time - 1
		if buy_cycle_time == 0:
			print 'Timeout!! Buy price is too low, please try again'
			print 'Cancel buy order!'
			fcoin.cancel_order(buy_id)

		if buy_order_done == 1: 
			result 		= 	fcoin.sell('fteth', sell_price, sell_volumn)
			sell_id		=	result['data']
			while(sell_cycle_time > 0):
				time.sleep(20)
				result = fcoin.get_order(sell_id)
				#print result
				filled = result['data']['filled_amount']
				if int(float(filled)) == sell_volumn:
					print('sell order done !')
					sell_order_done = 1
					break;
				sell_cycle_time = sell_cycle_time - 1
				if sell_cycle_time%5 == 0:
					print 'Sell price is too high, cancel order,try again'
					fcoin.cancel_order(sell_id)
					time.sleep(1)
					sell_price 		= 	sell_price*0.999 ## price down 0.001
					sell_price 		= 	round(sell_price,8) ## keep 8 decimal
					sell_volumn 	=	sell_volumn - int(float(filled))
					result 			= 	fcoin.sell('fteth', sell_price, sell_volumn)
					sell_id			=	result['data']
					print ('sell_price  = ',sell_price)
					print ('sell_volumn = ',sell_volumn)
