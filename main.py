#!/Users/artem/PycharmProjects/huobi_turnover/venv/bin/python3
from datetime import datetime
import time
import csv
from tqdm import tqdm
import argparse
import os, sys
import logging
from huobi import HuobiRestClient

# setup paths
current_path = os.path.dirname(__file__)
abs_path = os.path.abspath(current_path)

USDT_MIN_BALANCE_TO_TRADE = 15
TRADE_FEES_PERCENTAGE = 0.2
SOL_MIN_BALANCE_TO_TRADE = 0.1
TARGET_TURNOVER=120

parser = argparse.ArgumentParser('batch trading huobi accounts')
parser.add_argument("-v","--verbose", help="level of verbosing ('debug'-print all messages, 'warning'-only important, 'none'-no printing", choices=['debug', 'warning', 'critical', 'd', 'w'],default='warning')
parser.add_argument("-t","--target_turnover", help="turnover to get on the accounts", type=int, default=TARGET_TURNOVER)
parser.add_argument('-p', "--price_of_solana", help='current price of solana -5$', type=float, default=125)
# parser.add_argement("-a",
args = parser.parse_args()
TARGET_TURNOVER = args.target_turnover
current_solana_price = args.price_of_solana

# create our own logger
main = logging.getLogger('main')
main.propagate = False
main.setLevel(args.verbose.upper())

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
main.addHandler(console_handler)

file_handler = logging.FileHandler(abs_path + '/log.txt')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(console_formatter)
main.addHandler(file_handler)

# read wallet keys
try:
    with open(abs_path+'/settings.txt', 'r') as f:
        # print('opend')
        s = f.read()
        keys_list_splitted = s.split('\n')
except:
    main.critical('Problem in reading API keys, file settings.txt not found, put it the same folder (each row is access_key:secret_key)')

if keys_list_splitted and len(keys_list_splitted):
    keys_list_splitted = [key for key in keys_list_splitted if key]
    main.debug(f'API found: {len(keys_list_splitted)} pairs')
else:
    main.critical('Problem in reading API key, check settings.txt if it contains key pairs access_key:secret_key')

def save_dict_line(file_name, item):
    fields = item.keys()
    file_exists = os.path.isfile(file_name)
    with open(file_name, 'a', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter='|')
        if not file_exists:
            writer.writeheader()  # file doesn't exist yet, write a header
        writer.writerow(item)

# get account balance
def get_assets_list(client, account_id):
    accounts = client.accounts().data 
    balance_raw = client.balance(account_id=account_id).data
    balance = balance_raw['data']['list']
    assets_list = []
    for asset in balance:
        value = asset['balance']
        if float(value)>0.01 and asset['type']=='trade':
            item = {'asset':asset['currency'],'amount':asset['balance']}
            assets_list.append(item)
            # print(item)
    return assets_list 

def place_order(client, spot_account_id):
    order_type = 'buy-market'
    symbol = 'usdcusdt'
    amount = 7
    client.place(account_id=spot_account_id, amount=amount,symbol=symbol, type=order_type)

def get_spot_account_id(client):
    accounts = client.accounts().data['data']
    spot_account_id = [acc['id'] for acc in accounts if acc['type']=='spot'][0]
    return spot_account_id

def convert_all_assets_to_usdt():
    pass

def get_trade_volume_including_fees(amount, precision_numbers_after_point):
    amount = amount/(1+(TRADE_FEES_PERCENTAGE*1.25/100))
    koef = 10**precision_numbers_after_point
    # print('-'*10, amount)
    rounded_amount = int(amount*koef)/koef
    return rounded_amount

def buy_usdc(client, account_id, usdt_balance):
    symbol = 'usdcusdt'
    amount = get_trade_volume_including_fees(usdt_balance,4)
    order_type='buy-market'
    # print(amount)
    result = client.place(account_id=spot_account_id, amount=amount,symbol=symbol, type=order_type)
    trade_status = result.data['status']
    if trade_status!="ok":
        amount = 0
    # print(result.data)
    return amount

def sell_sol(client, account_id, sol_balance):
    amount = get_trade_volume_including_fees(sol_balance,2)
    # print('sol amount to trade: ', amount)
    symbol = 'solusdt'
    order_type = 'sell-market'
    result = client.place(account_id=spot_account_id, amount=amount,symbol=symbol, type=order_type)
    trade_status = result.data['status']
    if trade_status!="ok":
        amount = 0
    # print(result.data)
    return amount

def buy_sol(client, account_id, sol_balance):
    amount = get_trade_volume_including_fees(sol_balance,2)
    # print('sol amount to trade: ', amount)
    symbol = 'solusdt'
    order_type = 'buy-market'
    result = client.place(account_id=spot_account_id, amount=amount,symbol=symbol, type=order_type)
    trade_status = result.data['status']
    if trade_status!="ok":
        amount = 0
    # print(result.data)
    return amount

def sell_usdc(client, account_id, usdt_balance):
    symbol = 'usdcusdt'
    amount = get_trade_volume_including_fees(usdt_balance,4)
    order_type='sell-market'
    # print(amount)
    result = client.place(account_id=spot_account_id, amount=amount,symbol=symbol, type=order_type)
    trade_status = result.data['status']
    if trade_status!="ok":
        amount = 0
    # print(result.data)
    return amount

def parse_assets_list(assets_list):
    usdt_balance, usdc_balance, sol_balance = 0, 0, 0
    for asset in assets_list:
        if asset['asset']=='usdt':
            usdt_balance = asset['amount']
        elif asset['asset']=='usdc':
            usdc_balance = asset['amount']
        elif asset['asset']=='sol':
            sol_balance = asset['amount']

    return float(usdt_balance), float(usdc_balance), float(sol_balance)
   
def get_usdt_usdc_sol_balances(client, account_id, acc_nickname):
    assets_list = get_assets_list(client, account_id)
    usdt_balance, usdc_balance, sol_balance = parse_assets_list(assets_list)
    item = {'wallet':acc_nickname, 'usdt':usdt_balance, 'usdc':usdc_balance, 'sol':sol_balance}
    return item

global_trades_counter = 0
start_time = datetime.now()
for index, wallet_key_pair in enumerate(tqdm(keys_list_splitted[:])):
    index +=1
    actual_turnover = 0
    trades_counter = 0
    
    if not wallet_key_pair:
        break

    access_key = wallet_key_pair.split(':')[0].strip()
    secret_key =  wallet_key_pair.split(':')[1].strip()
    acc_nickname = access_key[-5:]
    # print('-'*25, index)#, acc_nickname, access_key, secret_key)

    # get wallet
    try:
        client = HuobiRestClient(access_key=access_key, secret_key=secret_key) 
    except:
        main.warning(f'wallet "{acc_nickname}"(ending symbols) not found')
        item = {'wallet':acc_nickname, 'usdt':0, 'usdc':0, 'sol':0, 'error':1, 'turnover':0, 'time':datetime.now()}
        save_dict_line('operations.csv', item)
        continue

    try:
        spot_account_id = get_spot_account_id(client)
    except:
        main.warning(f'wallet "{acc_nickname}"(ending symbols) not found or doesnt exists')
        item = {'wallet':acc_nickname, 'usdt':0, 'usdc':0, 'sol':0, 'error':1, 'turnover':0, 'time':datetime.now()}
        save_dict_line('operations.csv', item)
        continue

    main.debug(f'wallet -{acc_nickname}- has spot account id: {spot_account_id}')
    error_counter = 0

    while True:

        main.debug(f'actual turnover is: {actual_turnover}')

        if actual_turnover>TARGET_TURNOVER:
            main.debug(f'wallet {acc_nickname} has traded {actual_turnover}$, and reached target limit {TARGET_TURNOVER}$ in {trades_counter} trades')
            item['turnover']=actual_turnover
            item['time']=datetime.now()
            item['error']=0
            save_dict_line('operations.csv', item)
            break

        if error_counter > 3:
            main.warning(f'wallet {acc_nickname} has a strange error in attempting to make trades, pls contact developer @TomTamNan (telegram)')
            item['turnover']=0
            item['time']=datetime.now()
            item['error']=1
            save_dict_line('operations.csv', item)
            break


        assets_list = get_assets_list(client, spot_account_id)
        usdt_balance, usdc_balance, sol_balance = parse_assets_list(assets_list)
        
        item = get_usdt_usdc_sol_balances(client, spot_account_id, acc_nickname)
        main.debug(f'initial wallet state (balances) {acc_nickname}: '+str(item))
        # print(item)

        if usdc_balance>USDT_MIN_BALANCE_TO_TRADE and usdt_balance<USDT_MIN_BALANCE_TO_TRADE:
            main.debug(f'wallet {acc_nickname} has usdc, start buying usdt')
            # print('sell usdc')
            trading_amount = usdc_balance
            if usdc_balance>TARGET_TURNOVER:
                trading_amount = TARGET_TURNOVER
            volume = sell_usdc(client, spot_account_id, trading_amount)
            if volume == 0:
                error_counter +=1
                continue
            # actual_turnover += volume
            trades_counter +=1
            global_trades_counter+=1
            time.sleep(1)
            item = get_usdt_usdc_sol_balances(client,spot_account_id, acc_nickname)
            main.debug(f'wallet {acc_nickname} state after buying usdt (operation number {trades_counter}): '+str(item))

        # if usdc_balance>USDT_MIN_BALANCE_TO_TRADE and usdt_balance>USDT_MIN_BALANCE_TO_TRADE:

        elif sol_balance>SOL_MIN_BALANCE_TO_TRADE:
            main.debug(f'wallet {acc_nickname} has sol, start sell it for usdt')
            # trading_amount = sol_balance*current_solana_price
            # if (TARGET_TURNOVER-actual_turnover)<trading_amount:
            #     trading_amount = TARGET_TURNOVER-actual_turnover
            # trading_amount = trading_amount/current_solana_price

            volume = sell_sol(client, spot_account_id, sol_balance)
            if volume == 0:
                error_counter +=1
                continue
            actual_turnover += sol_balance*current_solana_price
            trades_counter +=1
            global_trades_counter+=1
            time.sleep(1)
            item = get_usdt_usdc_sol_balances(client,spot_account_id, acc_nickname)
            main.debug(f'wallet {acc_nickname} state after selling sol (operation number {trades_counter}): '+str(item))
            # print(item)

        elif usdt_balance>USDT_MIN_BALANCE_TO_TRADE:
            main.debug(f'wallet {acc_nickname} has usdt, start buying sol')
            trading_amount = usdt_balance
            if usdt_balance>TARGET_TURNOVER:
                trading_amount = TARGET_TURNOVER+25
            if (TARGET_TURNOVER-actual_turnover)<trading_amount:
                trading_amount = TARGET_TURNOVER-actual_turnover
            if trading_amount<15:
                trading_amount = 25
            # print(trading_amount)
            volume = buy_sol(client, spot_account_id, trading_amount)
            if volume == 0:
                error_counter +=1
                continue
            actual_turnover += volume
            trades_counter +=1
            global_trades_counter+=1
            time.sleep(1) 
            item = get_usdt_usdc_sol_balances(client,spot_account_id, acc_nickname)
            main.debug(f'wallet {acc_nickname} state after buying sol (operation number {trades_counter}): '+str(item))
            # print(item)
        else:
            main.warning(f'wallet {acc_nickname} not enough funds, minimum amounts sol, usdt, usdc: {SOL_MIN_BALANCE_TO_TRADE}, {USDT_MIN_BALANCE_TO_TRADE}, {USDT_MIN_BALANCE_TO_TRADE}')
            item['turnover']=0
            item['time']=datetime.now()
            item['error']=1
            save_dict_line('operations.csv', item)
            break
         
elapsed_time = datetime.now()-start_time
try:
    average_trade_processing_duration = elapsed_time/global_trades_counter
except:
    average_trade_processing_duration = 0
average_wallet_processing_duration = elapsed_time/len(keys_list_splitted)
print(f'---------- finished! duration {elapsed_time} for {global_trades_counter} trades in {len(keys_list_splitted)} wallets')
print(f'average speed is {average_trade_processing_duration} per trade and {average_wallet_processing_duration} per wallet')

