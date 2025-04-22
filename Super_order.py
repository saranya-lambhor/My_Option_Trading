import Functions as Fun
from json import loads as json_loads, dumps as json_dumps
import logging

class Super_order(Fun.dhanhq):
    def place_super_order(self, _security_id, _exchange_segment, _transaction_type, _quantity, 
                      _order_type, _product_type, _price, _targetPrice, _stopLossprice, _trailingJump, _tag):

        """
        Place a super order in the Dhan account 

        Args: 
            security_id (str): The ID of the security to trade 
            exchange_segment (str): The exchange segment (e.g, NSE, BSE)
            transaction_type (str): The type of transaction (BUY/SELL)
            quantity (int): The quantity of the order 
            order_type (str): The type of order (LIMIT, MARKET etc.)
            product_type (str): The product type (CNC, INTRA, etc.)
            price (float): The price of the order 
            targetPrice (float): The Target price 
            stopLossprice (float): The stop loss price 
            trailingJump (float): Trailing stop loss, how much points does the stop loss price has to be incremented 
            tag (str): Optional correlation ID for tracking 
            
        Returns: 
            dict: The response containing the status of the order placement 
    
        """
        try:
            url = self.base_url + '/super/orders'
            payload = {
                "dhanClientId": self.client_id,
                "transactionType": _transaction_type.upper(),
                "exchangeSegment": _exchange_segment.upper(),
                "productType": _product_type.upper(),
                "orderType": _order_type.upper(),
                "securityId": _security_id,
                "quantity": int(_quantity),
                "price": float(_price),
                "targetPrice" : float(_targetPrice),
                "stopLossPrice" : float(_stopLossprice),
                "trailingJump" : float(_trailingJump)
            }
            if _tag is not None and _tag != '':
                    payload["correlationId"] = _tag
            
            payload = json_dumps(payload)
            response = self.session.post(url, data=payload, headers=self.header, timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>place_order: %s', e)
            return {
                'status': 'failure',
                'remarks': str(e),
                'data': '',
            }

    def cancel_super_order(self, order_id, order_leg):
        """
        User can cancel any leg of a super order which is PENDING using this API.

        Args: 
            order_id : Order ID of the Order being cancelled
            order_leg : Order leg to be cancelled (ENTRY_LEG, STOP_LOSS_LEG, TARGET_LEG)
        
        Returns : 
            order_id & OrderStatus 

        """
        
        try:
            url = self.base_url + f'/super/orders/{order_id}/{order_leg}'
            response = self.session.delete(url, headers=self.header, timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>cancel_super_order: %s', e) 
            return {
                    'status': 'failure',
                    'remarks': str(e),
                    'data': '',
                }

    def get_current_super_order_list(self):
        """
        The API lets you retrieve an array of all orders with their last updated status along with legdetails

        Args: Nothing 

        Returns : dhanClientId, orderId, exchangeOrderId, correlationId, orderStatus(transit, pending, Rejected, cancelled, part traded, traded, closed, expired),
                    transactionType(Buy/Sell), exchangeSegment(NSE_EQ,NSE_FNO,BSE_EQ,BSE_FNO,MCX_COMM), productType(CNC, INTRADAY, MARGIN, MTF), 
                    orderType(LIMIT/MARKET), validity(DAY,IOC(Immediate or cancel)), tradingSymbol, securityId, quantity
                    remainingQuantity,ltp, price, afterMarketOrder, legName, createTime, updateTime, exchangeTime,
                    omsErrorDescription, algoID, legDetails(orderId, legName, transactionType,remainingQuantity, price, orderStatus, trailingJump), averageTradePrice, filledQty. 

        """

        try:
            url = self.base_url + '/super/orders'
            response = self.session.get(url, headers=self.header, timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_super_order_list : %s', e)
            return {
                'status': 'failure',
                'remarks': f'Exception in dhanhq>>get_super_order_list : {e}',
                'data': '',
            }

    def modify_super_order(self, order_id, order_type, leg_name, quantity, price, targetPrice,
                           stopLossPrice, trailingJump):
        """
        Modiify a pending super order in the orderbook 

        Args:
            order_id (str): The ID of the order to modify.
            order_type (str): The type of order (e.g., LIMIT, MARKET).
            leg_name (str): The name of the leg to modify.
            quantity (int): The new quantity for the order.
            price (float): The new price for the order.
            targetPrice (float): The target price of the order 
            stopLossPrice (float): The stop loss price of the order 
            tailingJump (float): The trailing jump value

        Return:
            dict: The response containing the status of the modification.
        """
        
        try:
            url = self.base_url + f'/super/orders/{order_id}'
            payload = {
                "dhanClientId": self.client_id,
                "orderId": str(order_id),
                "orderType": order_type,
                "legName": leg_name,
                "quantity": quantity,
                "price": float(price),
                "targetPrice": float(targetPrice),
                "stopLossPrice": float(stopLossPrice),
                "trailingJump": float(trailingJump)
            }
            payload = json_dumps(payload)
            response = self.session.put(url, headers=self.header, timeout=self.timeout, data=payload)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>modify_order: %s', e)
            return {
                'status': 'failure',
                'remarks': str(e),
                'data': '',
            }


"""
link : https://api.dhan.co/v2/#/operations/modifysuperorder

Allowed values for super order functions :

Place Super Order : 

    transactionType = BUY / SELL 
                      _________________________________________
    exchangeSegment = | NSE_EQ   |  NSE  |   Equity Cash       |
                      | NSE_FNO  |  NSE  |   Futures & Options |
                      | BSE_EQ   |  BSE  |   Equity Cash       |
                      | BSE_FNO  |  BSE  |   Futures & Options |
                      | MCX_COMM |  MCX  |   Commodity         |
                      |________________________________________|
    
                      ____________________________________________________
    ProducType      = | CNC      | Cash & Carry for equity deliveries    |
                      | INTRADAY | Intraday for Equity, Futures & Options| 
                      | MARGIN   | Carry Forward in Futures & options    |
                      | MTF      | Margin Traded Fund                    |
                      |__________________________________________________|

                       __________________________________
    orderType       = | LIMIT    | For Limit Order Types |
                      | MARKET   | For Market Order Types|
                      |__________________________________|


    Responses : 

        ____________________________________________________________
        | TRANSIT    |  did not reach the exchange server           |
        | PENDING    |  Reached at exchange end, awaiting execution |
        | REJECTED   |  Rejected at exchange / brokers end          |
        | CANCELLED  |  Cancelled by the user                       |
        | PART_TRADED|  partially executed                          |
        | TRADED     |  Executed                                    |
        | EXPIRED    |  Validity of order is expired                |
        | MODIFIED   |                                              |
        | TRIGGERED  |                                              |
        | INACTIVE   |                                              |
        |___________________________________________________________|

    



"""