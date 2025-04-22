import Functions as fd 
import Super_order as SO
import threading
import subprocess 
import time
import requests




if __name__ == '__main__':

    # Initiating the webserver, which listens to port 8000 and wait for receiving POST request from POSTMAN tool
    # for developement purpose 
    try : 
        flask_obj = subprocess.Popen("python Flask_dhan.py",
                                    stdin = subprocess.PIPE,
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE,
                                    shell=True)
        
    except FileNotFoundError:
        print("The file 'Flask_dhan.py' was not found")
    except PermissionError:
        print("Permission denied while trying to execute 'Flask_dhan.py'")
    except subprocess.SubprocessError as e:
        print(f"Subprocess error occured :{e}")
    except Exception as e:
        print(f"An unexpected error occurred : {e}")
    else:
        print("Subprocess started successfully.") 
        


    # Retrieve Client_id and Access_token from the credentials.txt file 
    client_id, access_token = fd.get_credentials()
    if client_id is not None and access_token is not None:
        dhan = SO.Super_order(client_id, access_token)
    else:
        print("credentials issue: client_id or access_token should not be empty")

    # Fetch the Security ID list 
    fd.get_security_id_csv_file(dhan)


    # Creating 2 threads, strategy_one for strategy and listen_from_pipe for getting the data from webserver
    p1 = threading.Thread(target=fd.strategy_one, args = [dhan])
    p2 = threading.Thread(target=fd.listen_from_pipe)    


    p1.start()
    p2.start()

    p1.join()
    p2.join()


       

"""
Template : 

    1) NIFTY Normal Place Order Function
    order = fd.place_order(dhan, 
                        _Index = "Nifty",
                        _exchange = "NSE_FNO", 
                        _transaction_type = "BUY", 
                        _quantity = 75,
                        _order_type="MARKET", 
                        _product_type = "INTRA",  
                        _price = 353, 
                        _trigger_price=0, 
                        _disclosed_quantity=0,
                        _after_market_order = False , 
                        _validity='DAY', 
                        _amo_time='OPEN', 
                        _bo_profit_value=None, 
                        _bo_stop_loss_Value=None, 
                        _tag = None )

                        
    2) NIFTY place Super order Function 

    security_id_df = pd.read_csv('security_id_list.csv', low_memory=False)
    _security_id = fd.get_security_id(security_id_df, "Nifty", 24, "APR", 23900, position = "CALL")

    order = dhan.place_super_order( _security_id = _security_id, 
                                    _exchange_segment = "NSE_FNO",
                                    _transaction_type = "BUY",
                                    _quantity = 75,
                                    _order_type = "LIMIT", 
                                    _product_type = "INTRADAY", 
                                    _price = 300,
                                    _targetPrice = 350, 
                                    _stopLossprice = 290,
                                    _trailingJump = 0, 
                                    _tag = "Super_order_Buy")



Supported Functions in dhanhq: 
    1) _parse_response           - Parse the API response.
    2) get_order_list            - Retrieve a list of all orders requested in a day with their last updated status.
    3) get_order_by_id           - Retrieve the details and status of an order from the orderbook placed during the day.
    4) get_order_by_correlationID-Retrieve the order status using a field called correlation ID.
    5) modify_order              - Modify a pending order in the orderbook.
    6) cancel_order              - Cancel a pending order in the orderbook using the order ID. 
    7) place_order               - Place a new order in the Dhan account.
    8) place_slice_order         - Place a new slice order in the Dhan account.
    9) get_positions             - Retrieve a list of all open positions for the day.
    10) get_holdings             - Retrieve all holdings bought/sold in previous trading sessions.
    11) convert_position         - Convert Position from Intraday to Delivery or vice versa.
    12) place_forever            - Place a new forever order in the Dhan account.
    13) modify_forever           - Modify a forever order based on the specified leg name. The variables that can be modified include price, quantity, order type, and validity.
    14) cancel_forever           - Delete Forever orders using the order id of an order
    15) get_forever              - Retrieve a list of all existing Forever Orders.
    16) generate_tpin            - Generate T-Pin on registered mobile number.
    17) open_browser_for_tpin    - Opens the default web browser to enter T-Pin.
    18) edis_inquiry             - Inquire about the eDIS status of the provided ISIN.
    19) kill_switch              - Control kill switch for user, which will disable trading for current trading day.
    20) get_fund_limits          - Get all information of your trading account like balance, margin utilized, collateral, etc.
    21) margin_calculator        - Calculate the margin required for a trade based on the provided parameters.
    22) get_trade_book           - Retrieve a list of all trades executed in a day.
    23) get_trade_history        - Retrieve the trade history for a specific date range.
    24) ledger_report            - Retrieve the ledger details for a specific date range.
    25) intraday_minute_data     - Retrieve OHLC & Volume of minute candles for desired instrument for last 5 trading day.
    26) historical_daily_data    - Retrieve OHLC & Volume of daily candle for desired instrument.
    27) ticker_data              - Retrieve the latest market price for specified instruments.
    28) ohlc_data                - Retrieve the Open, High, Low and Close price along with LTP for specified instruments.
    29) quote_data               - Retrieve full details including market depth, OHLC data, OI and volume along with LTP for specified instruments.
    30) fetch_security_list      - Fetch CSV file from dhan based on the specified mode and save it to the current directory.
    31) option_chain             - Retrieve the real-time Option Chain for a specified underlying instrument.
    32) expiry_list              - Retrieve the dates of all expiries for a specified underlying instrument.
    33) convert_to_date_time     - Convert EPOCH time to Python datetime object in IST.



"""
