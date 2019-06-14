#!/usr/bin/python3

from __future__ import print_function

import sys
import socket
import json
import time
import pickle
import sys
import os

from Dyna_Q import *

# ~~~~============== CONFIGURATION  ==============~~~~
# replace REPLACEME with your team name!
team_name="TOURISTS"
test_mode = False

test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

symbols = ["BOND", "GS", "MS", "USD", "VALBZ", "VALE", "WFC", "XLF"]
filename = "Dyna_Q_"
#sym = None
actions = ['buy', 'sell', 'nothing']
gamma = 0.8

# ~~~~============== NETWORKING CODE ==============~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())


# ~~~~============== MAIN LOOP ==============~~~~
def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = try_read_from_exchange(None, "", exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

    index = 0
    order_id = 0
    for i in range(8):
        newpid = os.fork()
        if newpid == 0:
            order_id = index * 100
            break
        else:
            index += 1

    position = 0
    # position = hello_from_exchange['symbols'][index]['position']
    sym = symbols[index]
    dynaQ = Dyna_Q(actions, gamma)
    if os.path.exists('~/Dyna_Q_' + sym + '.pickle'):
        with open(filename+sym+'.pickle', 'wb') as handle:
            dynaQ = pickle.load(handle)


    while True:
        from_exchange = try_read_from_exchange(dynaQ, sym, exchange)

        if from_exchange['type'] != 'trade' or from_exchange['symbol'] != sym:
            continue

        price = from_exchange['price']
        action = dynaQ.choose_action(price)
        order_id += 1
        size = 10
        limit = 100

        print('------------------------------------------------')
        print('action', action)
        print('order_id', order_id)

        print('postion', position)

        if action == 'buy' and position + size <= limit:
            buy(sym, price, order_id, size, exchange)
            position += size

        elif action == 'sell' and position - size >= -limit:
            sell(sym, price, order_id, size, exchange)
            position -= size

        print('action start')

        if action != 'nothing':
            wait_trade_complete(exchange, sym, size, order_id)

        print('action complete')

        time.sleep(5)

        reward_dict = reward_calculator(price, sym, action, position, sym, dynaQ, exchange)

        print('reward calculated')
        print('reward', reward_dict['reward'])
        print('reward', reward_dict['current_trading_price'])
        print('a', action)
        print('s', price)
        dynaQ.learn(price, action, reward_dict['reward'], reward_dict['current_trading_price'])

        print('learning complete')
        print('--------------------------------------------------')


def try_read_from_exchange(dynaQ, sym, exchange):
    try:
        from_exchange = read_from_exchange(exchange)
    except:
        with open(filename+sym+'.pickle', 'wb') as handle:
            pickle.dump(dynaQ, handle)
        sys.exit(1)
    
    return from_exchange
        


def wait_trade_complete(exchange, symbol, size, order_id):
    print('start filling')
#    while True:
#        from_exchange = try_read_from_exchange(exchange)
#        if from_exchange['type'] != 'fill' or from_exchange['order_id'] != order_id:
#            continue

#       break
    print('end filling')


def buy(symbol, price, order_id, size, exchange):
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "BUY", "price": price, "size": size})


def sell(symbol, price, order_id, size, exchange):
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "SELL", "price": price, "size": size})


def reward_calculator(ordered_price, symbol, action, position, sym, dynaQ, exchange):
    reward_dict = {
        'reward': 0,
        'current_trading_price': 0
    }

    print('start caluculating reward')

    while True:
        from_exchange = try_read_from_exchange(dynaQ, sym, exchange)
        if from_exchange['type'] != 'trade' or from_exchange['symbol'] != symbol:
            continue

        print('trade founded')
        current_trading_price = from_exchange['price']

        if action == 'buy':
            reward = current_trading_price - ordered_price
            reward_dict['reward'] = reward

        elif action == 'sell':
            reward = ordered_price - current_trading_price
            reward_dict['reward'] = reward

        else:
            print('calculating nothing')
            print('calculating going on')
            if position > 0:
                reward = current_trading_price - ordered_price
                reward_dict['reward'] = reward
            else:
                reward = ordered_price - current_trading_price
                reward_dict['reward'] = reward

        reward_dict['current_trading_price'] = current_trading_price
        break
       
    print('calcu completed')

    return reward_dict


if __name__ == "__main__":
    main()
