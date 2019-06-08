#!/usr/bin/python

# ~~~~==============   HOW TO RUN   ==============~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import time
#import numpy as np

from Dyna_Q import *

# ~~~~============== CONFIGURATION  ==============~~~~
# replace REPLACEME with your team name!
team_name="TOURISTS"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=2
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

symbols = ["BOND", "GS", "MS", "USD", "VALBZ", "VALE", "WFC", "XLF"]

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
    actions = ['buy', 'sell', 'nothing']
    gamma = 0.8

    dynaQ = Dyna_Q(actions, gamma)

    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

    symbols = ["BOND", "GS", "MS", "USD", "VALBZ", "VALE", "WFC", "XLF"]


    trainding_history = {"BOND": [],
                         "GS": [],
                         "MS": [],
                         "USD": [],
                         "VALBZ": [],
                         "VALE": [],
                         "WFC": [],
                         "XLF": [],
                         }
    while True:
        # TODO send price information to function
        # TODO function(price)
        # TODO get_decision
        # TODO find the best price for buying the
        # TODO buy
        # TODO 一定時間がたってrewardを送る
        ## learning

        from_exchange = read_from_exchange(exchange)
        symbol = "BOND"
        id = 0

        if from_exchange['type'] != 'trade' and from_exchange['symbol'] != symbol:
            continue

        price = from_exchange['price']
        action = dynaQ.choose_action(price)
        id += 1
        size = 10
        limit = 100


        write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
        hello_from_exchange = read_from_exchange(exchange)
        position = hello_from_exchange['symbols'][symbols.index(symbol)]['position']


        # TODO price は考慮の余地あり
        if action == 'buy' and position + size <= limit:
            buy(symbol, price, id, size, exchange)

        elif action == 'sell' and position - size >= -limit:
            sell(symbol, price, id, size, exchange)

        #TODO 約定しなかったら死ぬ
        wait_trade_complete(exchange, symbol, size, id)

        time.sleep(5)

        #TODO nothingの時の計算がだるい
        reward_dict = reward_calculator(price, symbol, action, exchange)

        dynaQ.learn(price, action, reward_dict['reward'], reward_dict['current_trading_price'])


def wait_trade_complete(exchange, symbol: str, size: int, id: int):
    unfilled_size = size

    while True:
        from_exchange = read_from_exchange(exchange)
        if from_exchange['type'] != 'fill' and from_exchange['order_id'] != id:
            continue

        unfilled_size -= from_exchange['size']

        if unfilled_size == 0:
            break


def buy(symbol: str, price: int, id: int, size: int, exchange):
    write_to_exchange(exchange, {"type": "add", "order_id": id, "symbol": symbol, "dir": "BUY", "price": price, "size": size})


def sell(symbol: str, price: int, id: int, size: int, exchange):
    write_to_exchange(exchange, {"type": "add", "order_id": id, "symbol": symbol, "dir": "SELL", "price": price, "size": size})


def reward_calculator(ordered_price: int, symbol: str, action: str, exchange):
    from_exchange = read_from_exchange(exchange)
    reward_dict = {
        'reward': 0,
        'current_trading_price': 0
    }

    while True:
        if from_exchange['type'] != 'trade' and from_exchange['symbol'] != symbol:
            continue

        current_trading_price = from_exchange['price']

        if action == 'buy':
            reward = current_trading_price - ordered_price
            reward_dict['reward'] = reward

        elif action == 'sell':
            reward = ordered_price - current_trading_price
            reward_dict['reward'] = reward

        else:
            write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})

            hello_from_exchange = read_from_exchange(exchange)
            position = hello_from_exchange['symbols'][symbols.index(symbol)]['position']

            if position > 0:
                # reward小さくするかも
                reward = current_trading_price - ordered_price
                reward_dict['reward'] = reward
            else:
                reward = ordered_price - current_trading_price
                reward_dict['reward'] = reward

        reward_dict['current_trading_price'] = current_trading_price
        break

    return reward_dict


if __name__ == "_main_":
    main()
