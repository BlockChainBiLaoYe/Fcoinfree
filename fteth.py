from fcoin import Fcoin
#if python3 use fcoin3
#from fcoin3 import Fcoin
from strategy import Strategy
import time

count = 1
while True:
	time.sleep(3)
	print ('#####round ',count,'#####') 
	s1 = Strategy()
	s1.fteth(0.0025, 0.2)
	count = count + 1

print 'done'
