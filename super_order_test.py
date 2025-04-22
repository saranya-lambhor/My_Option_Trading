import Super_order as SO
import Functions as fd


def super_order_buy(dhan):

    order = dhan.place_super_order( _security_id = 14366,  # Vodafone Idea : NSE : Equity
                _exchange_segment = "NSE_EQ",
                _transaction_type = "BUY",
                _quantity = 1,
                _order_type = "MARKET", 
                _product_type = "INTRADAY", 
                _price = 0,
                _targetPrice = 10, # need to retrieve the data from data api  
                _stopLossprice = 5,  # need to retrieve the data from data api  
                _trailingJump = 1, 
                _tag = "Super_order_Buy")
    print(order)

def super_order_sell_same_buy_order(dhan):
    order = dhan.place_super_order( _security_id = 14366,  # Vodafone Idea : NSE : Equity
                _exchange_segment = "NSE_EQ",
                _transaction_type = "SELL",
                _quantity = 1,
                _order_type = "MARKET", 
                _product_type = "INTRADAY", 
                _price = 0,
                _targetPrice = 10, # need to retrieve the data from data api  
                _stopLossprice = 5,  # need to retrieve the data from data api  
                _trailingJump = 1, 
                _tag = "Super_order_Sell")
    print(order)

def super_order_sell(dhan):
    order = dhan.place_super_order( _security_id = 14366,  # Vodafone Idea : NSE : Equity
                _exchange_segment = "NSE_EQ",
                _transaction_type = "SELL",
                _quantity = 1,
                _order_type = "MARKET", 
                _product_type = "INTRADAY", 
                _price = 0,
                _targetPrice = 3, # need to retrieve the data from data api  
                _stopLossprice = 10,  # need to retrieve the data from data api  
                _trailingJump = 1, 
                _tag = "Super_order_Sell")
    print(order)
    
def super_order_sell_same_sell_order(dhan):
    order = dhan.place_super_order( _security_id = 14366,  # Vodafone Idea : NSE : Equity
                _exchange_segment = "NSE_EQ",
                _transaction_type = "BUY",
                _quantity = 1,
                _order_type = "MARKET", 
                _product_type = "INTRADAY", 
                _price = 0,
                _targetPrice = 3, # need to retrieve the data from data api  
                _stopLossprice = 10,  # need to retrieve the data from data api  
                _trailingJump = 1, 
                _tag = "Super_order_Sell")
    print(order)

def super_order_get_current_order_list(dhan):
     result = dhan.get_current_super_order_list()
     print(result)

def super_order_cancel(dhan, order_id, leg):
    result = dhan.cancel_super_order(order_id, leg)
    print(result)

def place_order_fun(dhan, _security_id, exchange_segment, transaction_type, _quantity,order_type, product_type, _price , _trigger_price, _disclosed_quantity
                    ,_after_market_order, _validity, _amo_time, _bo_profit_value, _bo_stop_loss_Value , _tag):
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
    print(order_id)
    
    



if __name__ == '__main__':

    client_id, access_token = fd.get_credentials()
    if client_id is not None and access_token is not None:
        dhan = SO.Super_order(client_id, access_token)
    else:
        print("credentials issue: client_id or access_token should not be empty")

    super_order_buy(dhan) 
    #place_order_fun(dhan,14366,"NSE_EQ", "SELL", 1,"MARKET","INTRADAY",0, 0, 1, False, 'DAY',False, False,False, "Super_order_buy "  )
    #super_order_sell_same_buy_order(dhan) -- not working 
    #super_order_sell(dhan) 
    #super_order_sell_same_sell_order(dhan)
    #super_order_get_current_order_list(dhan)
    #super_order_cancel(dhan, 932504225345971, "TARGET_LEG") #STOP_LOSS_LEG, TARGET_LEG



    
    
    





