from dhanhq import dhanhq
import pandas as pd 
import datetime 
from json import loads as json_loads, dumps as json_dumps
import logging
import os
from pathlib import Path
import json 
import time
import queue 

pipe_path = "/tmp/jsonpipe"
data_queue = queue.Queue()


def get_credentials():
    """
    Get the credentials of the user from the credentials.txt file
    Returns: client_id and access_token of the user
    """
    client_id = None
    access_token = None
    file_path = "credentials.txt"
    if os.path.exists("credentials.txt"):
        with open(file_path) as file:
            for line in file:
                if line.startswith("client_id"):
                    client_id = line.split('=')[1].strip().strip('"')
                if line.startswith("access_token"):
                    access_token = line.split('=')[1].strip().strip('"')
    else:
        print("credentials.txt file not found in the current directory")
    return client_id, access_token

def listen_from_pipe():
    print("[Listener] Started pipe listener...")
    while True:
        try:
            with open(pipe_path, "r") as pipe:
                for line in pipe:
                    try :
                        data = line.strip()
                        print("[Listner] Received :", data)
                        data_queue.put(data)
                    except json.JSONDecodeError:
                        print("[Main] Invalid JSON: ", line.strip()) 
        except FileNotFoundError :
            print(f"[Listener] Waiting for pipe path to be created...")
            time.sleep(1)

# Returns Holdings 
def get_holdings(dhan):
    """
    Retrieve all holdings bought/sold in previous trading sessions.

    Returns:
        dict: The response containing holdings data.
    return {
                'status': 'failure',
                'remarks': str(e),
                'data': '',
            }
    """
    try:
        data_holdings = dhan.get_holdings()
        print(data_holdings)
    except Exception as e:
        print(f"Error while fetching holdings: {e}")


# Returns positions 
def get_positions(dhan):
    try:
        data_positions = dhan.get_positions()
        print(data_positions)
    except Exception as e:
        print(f"Error while fetching positions: {e}")
    

def get_security_id_csv_file(dhan):
    """
    Fetch the security list(security_id_list.csv) once in a day only if the csv file does not exist or
    if the last modified date does not match with today's date 
    and time should be between market opening time and closing time
    """
    if os.path.exists("security_id_list.csv"):
        file_path = "security_id_list.csv"
        timestamp = os.path.getmtime(file_path)
        last_modified = datetime.datetime.fromtimestamp(timestamp)
        now = datetime.datetime.now()   # Output: 2025-04-18 02:19:41.286098
        now_time = now.time().replace(microsecond=0)
        today = now.date()
        market_open = datetime.time(9, 30)
        market_close = datetime.time(15, 30)

        if (last_modified.date()!=today) and (market_open < now_time < market_close):
            result = dhan.fetch_security_list("compact")
            print("\n Security List : ")
            print(result)
    else :
        result = dhan.fetch_security_list("compact")
        print("\n Security List : ")
        print(result)


# Return nearest 50's Strike Price 
def get_round_to_nearest_50(value):
    try:
        return int(round(value / 50.0)) * 50 
    except Exception as e:
        print(f"Error rounding value to nearest 50: {e}")
        return None


def get_current_expiry():
    today = datetime.date.today()
    weekday = today.weekday()  # Monday = 0, Sunday = 6

    if weekday <= 3:
        days_to_thursday = 3 - weekday
    else:
        days_to_thursday = 7 - weekday + 3
    
    expiry_date = today + datetime.timedelta(days=days_to_thursday)

    # Split into day and month
    day = expiry_date.strftime("%d")           # '17'
    month = expiry_date.strftime("%b").upper() # 'APR'
   
    return day, month


# Need to use SEM_CUSTOM_SYMBOL inatead of SEM_TRADING_SYMBOL
def get_security_id(dataframe=None, stock:str=None, day:int=0, month:str=None, price:int=0, position:str=None):
    """
    stock_name is a value from SEM_TRADING_SYMBOL column
    dataframe contains security_id_list.csv data
    ARGUMENTS:
        dataframe - Name of the pandas dataframe of security_id_list.csv
        stock - Name of the stock for example="Nifty" or "MidCapNifty"
        expiry day and month are passed to the function for now, LATER HAS TO BE TAKEN FROM expiry_list()
        price - Current price of the stock
        positoin - pass values as 'CALL' or 'PUT'
    """
    #### need to use expiry_list() function and retrieve the data, but data api need to be purchased
    # day, month = get_current_expiry()
    stock_name = f"{stock.upper()} {day} {month.upper()} {get_round_to_nearest_50(price)} {position.upper()}"
    print("Stock name: ", stock_name)
    if stock_name is None or dataframe is None:
        return None
    else:
        s_id = dataframe.loc[dataframe['SEM_CUSTOM_SYMBOL']==stock_name, 'SEM_SMST_SECURITY_ID']
        if not s_id.empty:
            return int(s_id.values[0])
        else:
            return None


# stop loss order function - Need to call place order manually twice     
def stop_loss_order(dhan):
    try:
        order_id = place_order(dhan, 
                    _security_id = "48198", 
                    _exchange = "NSE_FNO", 
                    _transaction_type = "BUY",
                    _quantity = 75,
                    _order_type="MARKET", 
                    _product_type = "INTRA",  
                    _price = 0 , #ignored for market order
                    _trigger_price=0, 
                    _disclosed_quantity=0,
                    _after_market_order = False , 
                    _validity='DAY', 
                    _amo_time='OPEN', 
                    _bo_profit_value=None, 
                    _bo_stop_loss_Value=None, 
                    _tag = None )
        if (input_price <= 345) :
            order_id = place_order(dhan, 
                    _security_id = "48198", 
                    _exchange = "NSE_FNO", 
                    _transaction_type = "SELL",
                    _quantity = 75,
                    _order_type="STOP_LOSS", 
                    _product_type = "INTRA",  
                    _price = 0 , #enter the price
                    _trigger_price=0, #trigger when the price hits 
                    _disclosed_quantity=0,
                    _after_market_order = False , 
                    _validity='DAY', 
                    _amo_time='OPEN', 
                    _bo_profit_value=None, 
                    _bo_stop_loss_Value=None, 
                    _tag = None )
        if order_id is not None:
            return order_id
        else:
            return None
    except Exception as e:
        print(f"Error placing stop loss order: {e}")
        return None


#bracket order function - sets Buy Price, SL Price & Target Price together 
def Bracket_order(dhan):
    try:
        order_id = place_order(dhan, 
                    _security_id = "48198", 
                    _exchange = "NSE_FNO", 
                    _transaction_type = "BUY",
                    _quantity = 75,
                    _order_type="MARKET", 
                    _product_type = "BO",  
                    _price = 0 , # Ignored if the _order_type is "MARKET"
                    _trigger_price = 0, # Trigger when the price hits (Act as a stop loss for CO order, it is not used for BO order )
                    _disclosed_quantity=0,
                    _after_market_order = False , 
                    _validity='DAY', 
                    _amo_time='OPEN', 
                    _bo_profit_value=10, # Target Profit (in points) for BO order 
                    _bo_stop_loss_Value=5, # Stop Loss (in points) for BO order 
                    _tag = None )
        if order_id is not None:
            return order_id
        else:
            return None
    except Exception as e:
        print(f"Error puting Bracket Order: {e}")
        return None


#cover order function - sets Buy Price & SL price together 
def Cover_order(dhan):
    try:
        order_id = place_order(dhan, 
                    _security_id = "48198", 
                    _exchange = "NSE_FNO", 
                    _transaction_type = "BUY",
                    _quantity = 75,
                    _order_type="MARKET", 
                    _product_type = "CO",   # Important for CO order 
                    _price = 0 , # Ignored if _order_type is MARKET 
                    _trigger_price=0, # Trigger when the price hits (Act as a stop loss for CO order, it is not used for BO order) eg : sell when 340 
                    _disclosed_quantity=0,
                    _after_market_order = False , 
                    _validity='DAY', 
                    _amo_time='OPEN', 
                    _bo_profit_value = None, # Target Profit (in points) for BO order 
                    _bo_stop_loss_Value = None, # Stop Loss (in points) for BO order 
                    _tag = None )
        if order_id is not None:
            return order_id
        else:
            return None
    except Exception as e:
        print(f"Error placing cover order: {e}")
        return None


#returns the product type : CNC - Cash and Carry 
#                           INTRA - Intra Day  
#                           MARGIN - MIS(Margin Intra day Square Off)
#                           CO - Cover Order
#                           BO - Bracket Order
#                           MTF - Mutual fund
def get_product_type(dhan,product_type):
    try:
        match  product_type:
            case "CNC" : 
                return dhan.CNC
            case "INTRA" :
                return dhan.INTRA
            case "MARGIN" :
                return dhan.MARGIN
            case "CO" :
                return dhan.CO
            case "BO" : 
                return dhan.BO
            case "MTF" : 
                return dhan.MTF
            case _:
                print(f"Warning! Unknown product type: '{product_type}'")
                return None
    except Exception as e:
        print(f"Error while getting product type: {e}")
        return None


def get_exchange_segment(dhan, exchange) : 
    try:
        match exchange:
            case "BSE" : 
                return dhan.BSE
            case "NSE" : 
                return dhan.NSE
            case "CUR" : 
                return dhan.CUR 
            case "MCX" : 
                return dhan.MCX 
            case "FNO" :
                return dhan.FNO 
            case "NSE_FNO" : 
                return dhan.NSE_FNO 
            case "BSE_FNO" : 
                return dhan.BSE_FNO 
            case "IDX_I" : 
                return dhan.INDEX
            case _:
                print(f"Warning! Unknown exchange: '{exchange}'")
                return None
    except Exception as e:
        print(f"Error while getting exchange: '{e}'")
        return None


def get_transaction_type(dhan, side) :
    try:
        match side:
            case "BUY" :
                return dhan.BUY 
            case "SELL" : 
                return dhan.SELL
            case _:
                print(f"Warning! Unknown transaction type: '{side}'")
                return None
    except Exception as e:
        print(f"Error while getting transaction type: '{e}'")
        return None


def get_order_type(dhan,order_type):
    try:
        match order_type :
            case "LIMIT" :
                return dhan.LIMIT
            case "MARKET" :
                return dhan.MARKET
            case "STOP_LOSS" :
                return dhan.SL
            case "STOP_LOSS_MARKET" :
                return dhan.SLM
            case _:
                print(f"Warning! Unknown order type: '{order_type}'")
                return None
    except Exception as e:
        print(f"Error while getting order type: '{e}'")


def get_validity(dhan,validity):
    try:
        match validity :
            case "DAY" :
                return dhan.DAY
            case "IOC" :
                return dhan.IOC
            case _:
                print(f"Warning! Unknown validity: '{validity}'")
                return None
    except Exception as e:
        print(f"Error while getting validity: '{e}'")


def place_order(dhan, _Index , _exchange, _transaction_type, _quantity,  _order_type, 
                _product_type, _price , _trigger_price=0, _disclosed_quantity=0, 
                _after_market_order = False , _validity='DAY', _amo_time='OPEN', 
                _bo_profit_value=None, _bo_stop_loss_Value=None, _tag = None):
    
    #print(dhan.expiry_list(48198,dhan.NSE_FNO)) 
    try:
        security_id_df = pd.read_csv('security_id_list.csv', low_memory=False)
        _security_id = get_security_id(security_id_df, stock=_Index, day=31, month="dec", price=8000, position="Call")  # Security_id: 48047 (NIFTY 31 DEC 8000 CALL)
        if _security_id is None:
            print("Error! Security could not be fetched.")
            return None
        print("Security_id:", _security_id)
        exchange_segment = get_exchange_segment(dhan, _exchange)
        if exchange_segment is None:
            print("Error: Invalid exchange segment.")
            return None
        transaction_type = get_transaction_type(dhan, _transaction_type)
        if transaction_type is None:
            print("Error: Invalid transaction type.")
            return None
        order_type = get_order_type(dhan, _order_type)
        if order_type is None:
            print("Error: Invalid order type.")
            return None
        product_type = get_product_type(dhan, _product_type)
        if product_type is None:
            print("Error: Invalid product type.")
            return None
        order_id = dhan.place_order(security_id =_security_id, 
                                    exchange_segment = exchange_segment,
                                    transaction_type = transaction_type,
                                    quantity = _quantity,
                                    order_type = order_type,
                                    product_type = product_type,
                                    price =_price,
                                    trigger_price = _trigger_price,
                                    disclosed_quantity = _disclosed_quantity,
                                    after_market_order =_after_market_order,
                                    validity = _validity,
                                    amo_time = _amo_time,
                                    bo_profit_value = _bo_profit_value,
                                    bo_stop_loss_Value = _bo_stop_loss_Value,
                                    tag = _tag)
        return order_id
    except Exception as e:
        print(f"Error placing order: {e}")
        return None
    

def strategy_one(dhan):
    print("[Logic] Started logic process...")
    while True :
        # Retriving the data from listener thread function 
        if not data_queue.empty():
            data = data_queue.get()
            print("[Logic] processing : ",data)
            data = json.loads(data) # Converting the string data to json format


            # Parsing the necessary data 
            Ticker = data["ticker"] #"Nifty"
            Price = data["price"] #23000
            Trade_type = data["trade_type"] #"Buy"
            Position_size = data["position_size"] # 1 / 0 / -1 
            Exchange = data["Exchange"] # NSE, BSE, MCX 

            print("Ticker: {0} Price: {1} TradeType: {2} Position_size:{3}".format(Ticker,Price,Trade_type,Position_size))

            match Trade_type:
                case "buy":
                    position = "CALL"
                case "sell":
                    position = "PUT"              

            
            # Getting the security ID 

            security_id_df = pd.read_csv('security_id_list.csv', low_memory=False)
            _security_id = get_security_id(security_id_df, Ticker, 24, "APR", float(json.loads(Price)), position)
            print(_security_id)

            
            if Trade_type == "buy" and Position_size == 0:
                 order = dhan.place_super_order( _security_id = _security_id, 
                                    _exchange_segment = "NSE_FNO",
                                    _transaction_type = Trade_type.upper(),
                                    _quantity = 75,
                                    _order_type = "CNC", 
                                    _product_type = "MARGIN", 
                                    _price = 0,
                                    _targetPrice = 350, # need to retrieve the data from data api  
                                    _stopLossprice = 290,  # need to retrieve the data from data api  
                                    _trailingJump = 1, 
                                    _tag = "Super_order_Buy")
            """
            elif Trade_type == "Sell"  and Position_size == 0:
                order = dhan.place_super_order( _security_id = _security_id, 
                                    _exchange_segment = "NSE_FNO",
                                    _transaction_type = Trade_type.upper(),
                                    _quantity = 75,
                                    _order_type = "MARKET", 
                                    _product_type = "MARGIN", 
                                    _price = 0,
                                    _targetPrice = 350, # need to retrieve the data from data api  
                                    _stopLossprice = 290,  # need to retrieve the data from data api  
                                    _trailingJump = 1, 
                                    _tag = "Super_order_Sell")
            elif Trade_type == "Buy" and Position_size == -1: 
            """


                # pending need to complete





            
            

            time.sleep(1)
        else : 
            time.sleep(0.2)

    
    


    return None 