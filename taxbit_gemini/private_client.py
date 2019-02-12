# private_client.py
# Mohammad Usman
#
# A python wrapper for Gemini's public API
from typing import Union

from .public_client import PublicClient
import requests
import json
import hmac
import hashlib
import base64
import time

TIME_LENGTH = 18


class PrivateClient(PublicClient):
    def __init__(self, public_api_key, private_api_key, sandbox=False, cached=True):
        super().__init__(sandbox, cached)
        self._public_key = public_api_key
        self._private_key = private_api_key
        if sandbox:
            self._base_url = 'https://api.sandbox.gemini.com'
        else:
            self._base_url = 'https://api.gemini.com'

    def api_query(self, method, payload=None, **kwargs) -> Union[dict, tuple]:
        if payload is None:
            payload = {}
        request_url = self._base_url + method

        payload['request'] = method
        payload['nonce'] = str(int(time.time() * 1000))
        while len(payload['nonce']) < TIME_LENGTH:
            payload['nonce'] += "0"
        b64_payload = base64.b64encode(json.dumps(payload).encode('utf-8'))
        signature = hmac.new(self._private_key.encode('utf-8'), b64_payload, hashlib.sha384).hexdigest()

        headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self._public_key,
            'X-GEMINI-PAYLOAD': b64_payload,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
        }

        r = requests.post(request_url, headers=headers)
        if 'return_status' in kwargs and kwargs['return_status']:
            return r.json(), r.status_code
        return r.json()

    # Order Placement API
    def new_order(self, symbol, amount, price, side, options=["immediate-or-cancel"]):
        """
        This endpoint is used for the creation of a new order.
        Requires you to provide the symbol, amount, price, side and options.
        Options is an array and should include on the following:
        "maker-or-cancel","immediate-or-cancel", auction-only"
        So far Gemini only supports "type" as "exchange limit".

        Args:
            product_id(str): Can be any value in self.symbols()
            amount(str): The amount of currency you want to buy.
            price(str): The price at which you want to buy the currency/
            side(str): Either "buy" or "ask"
            options(list): Currently, can only be ["immediate-or-cancel"]

        Returns:
            dict: These are the same fields returned by order/status
            example: {
                'order_id': '86403510',
                'id': '86403510',
                'symbol': 'btcusd',
                'exchange': 'gemini',
                'avg_execution_price': '0.00',
                'side': 'buy',
                'type': 'exchange limit',
                'timestamp': '1510403257',
                'timestampms': 1510403257453,
                'is_live': True,
                'is_cancelled': False,
                'is_hidden': False,
                'was_forced': False,
                'executed_amount': '0',
                'remaining_amount': '0.02',
                'options': ['maker-or-cancel'],
                'price': '6400.28',
                'original_amount': '0.02'
            }
        """
        payload = {
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'side': side,
            'options': options,
            'type': 'exchange limit'
        }
        return self.api_query('/v1/order/new', payload)

    def cancel_order(self, order_id):
        """
        Used for the cancellation of an order via it's ID. This ID is provided
        when the user creates a new order.

        Args:
            order_id(str): Order must be not be filled

        Results:
            dict: These are the same fields returned by order/cancel
            example: {
                'order_id': '86403510',
                'id': '86403510',
                'symbol': 'btcusd',
                'exchange': 'gemini',
                'avg_execution_price': '0.00',
                'side': 'buy',
                'type': 'exchange limit',
                'timestamp': '1510403257',
                'timestampms': 1510403257453,
                'is_live': False,
                'is_cancelled': True,
                'is_hidden': False,
                'was_forced': False,
                'executed_amount': '0',
                'remaining_amount': '0.02',
                'options': ['maker-or-cancel'],
                'price': '6400.28',
                'original_amount': '0.02'
            }
        """
        payload = {
            'order_id': order_id
        }
        return self.api_query('/v1/order/cancel', payload)

    def cancel_session_orders(self):
        """
        Used for the cancellation of all orders in a session.

        Results:
            dict: The response will be a dict with two keys: "results"
            and "details"
            example: {
                'result': 'ok',
                'details': {
                    'cancelledOrders': [86403350, 86403386, 86403503, 86403612],
                    'cancelRejects': []
                }
            }
        """
        return self.api_query('/v1/order/cancel/session')

    def cancel_all_orders(self):
        """
        Cancels all current orders open.

        Results: Same as cancel_session_order
        """
        return self.api_query('/v1/order/cancel/all')

    # Order Status API
    def status_of_order(self, order_id):
        """
        Get's the status of an order.
        Note: the API used to access this endpoint must have the "trader"
        functionality assigned to it.

        Args:
            order_id(str): Order can be in any state

        Results:
            dict: Returns the order_id, id, symbol, exchange, avh_execution_price,
            side, type, timestamp, timestampms, is_live, is_cancelled, is_hidden,
            was_forced, exucuted_amount, remaining_amount, options, price and
            original_amount
            example: {
                'order_id': '44375901',
                'id': '44375901',
                'symbol': 'btcusd',
                'exchange': 'gemini',
                'avg_execution_price': '400.00',
                'side': 'buy',
                'type': 'exchange limit',
                'timestamp': '1494870642',
                'timestampms': 1494870642156,
                'is_live': False,
                'is_cancelled': False,
                'is_hidden': False,
                'was_forced': False,
                'executed_amount': '3',
                'remaining_amount': '0',
                'options': [],
                'price': '400.00',
                'original_amount': '3'
            }
        """
        payload = {
            'order_id': order_id
        }
        return self.api_query('/v1/order/status', payload)

    def active_orders(self):
        """
        Returns all the active_orders associated with the API.

        Results:
            array: An array of the results of /order/status for all your live orders.
            Each entry is similar to status_of_order
        """
        return self.api_query('/v1/orders')

    def get_past_trades(self, symbol, limit_trades=None, timestamp=0, **kwargs):
        """
        Returns all the past trades associated with the API.
        Providing a limit_trade is optional.

        Args:
            symbol(str): Can be any value in self.symbols()
            limit_trades(int): Default value is 500
            timestamp(int): Default value is 0

        Results:
            array: An array of of dicts of the past trades
        """
        payload = {
            "symbol": symbol,
            "limit_trades": 500 if limit_trades is None else limit_trades,
            "timestamp": timestamp
        }
        return self.api_query('/v1/mytrades', payload, **kwargs)

    def get_trade_volume(self):
        """
        Returns the trade volume associated with the API for the past
        30 days.

        Results:
            array: An array of dicts of the past trades
        """
        return self.api_query('/v1/tradevolume')

    # Fund Management API
    def get_balance(self):
        """
        This will show the available balances in the supported currencies.

        Results:
            array: An array of elements, with one block per currency
            example: [
                {
                    'type': 'exchange',
                    'currency': 'BTC',
                    'amount': '19.17997442',
                    'available': '19.17997442',
                    'availableForWithdrawal': '19.17997442'
                },
                {
                    'type': 'exchange',
                    'currency': 'USD',
                    'amount': '4831517.78',
                    'available': '4831389.45',
                    'availableForWithdrawal': '4831389.45'
                }
            ]
        """
        return self.api_query('/v1/balances')

    def get_transfers(self, timestamp=0, limit_transfers=50, **kwargs):
        """
        This endpoint shows deposits and withdrawals in the supported currencies. When deposits show as Advanced or
        Complete they are available for trading.

        This endpoint does not currently show cancelled advances, returned outgoing wires or ACH transactions, admin
        credits and debits, or other exceptional transaction circumstances.

        Results:
            array: An array of elements, with one block per transfer
            example: [
               {
                  "type":"Deposit",
                  "status":"Advanced",
                  "timestampms":1507913541275,
                  "eid":320013281,
                  "currency":"USD",
                  "amount":"36.00",
                  "method":"ACH"
               },
               {
                  "type":"Deposit",
                  "status":"Advanced",
                  "timestampms":1499990797452,
                  "eid":309356152,
                  "currency":"ETH",
                  "amount":"100",
                  "txHash":"605c5fa8bf99458d24d61e09941bc443ddc44839d9aaa508b14b296c0c8269b2"
               },
               {
                  "type":"Deposit",
                  "status":"Complete",
                  "timestampms":1495550176562,
                  "eid":298112782,
                  "currency":"BTC",
                  "amount":"1500",
                  "txHash":"163eeee4741f8962b748289832dd7f27f754d892f5d23bf3ea6fba6e350d9ce3",
                  "outputIdx":0
               },
               {
                  "type":"Deposit",
                  "status":"Advanced",
                  "timestampms":1458862076082,
                  "eid":265799530,
                  "currency":"USD",
                  "amount":"500.00",
                  "method":"ACH"
               },
               {
                  "type":"Withdrawal",
                  "status":"Complete",
                  "timestampms":1450403787001,
                  "eid":82897811,
                  "currency":"BTC",
                  "amount":"5",
                  "txHash":"c458b86955b80db0718cfcadbff3df3734a906367982c6eb191e61117b810bbb",
                  "outputIdx":0,
                  "destination":"mqjvCtt4TJfQaC7nUgLMvHwuDPXMTEUGqx"
               },
               {
                  "type": "Withdrawal",
                  "status": "Complete",
                  "timestampms": 1535451930431,
                  "eid": 341167014,
                  "currency": "USD",
                  "amount": "1.00",
                  "txHash": "7bffd85893ee8e72e31061a84d25c45f2c4537c2f765a1e79feb06a7294445c3",
                  "destination": "0xd24400ae8BfEBb18cA49Be86258a3C749cf46853"
               }
            ]
        """
        payload = {
            'timestamp': timestamp,
            'limit_transfers': limit_transfers
        }
        return self.api_query('/v1/transfers', payload, **kwargs)

    def create_deposit_address(self, currency, label=None):
        """
        This will create a new cryptocurrency deposit address with an optional label.

        Args:
            currency(str): Can either be btc or eth
            label(str): Optional

        Results:
            dict: A dict of the following fields: currency, address, label
        """
        if label:
            payload = {
                "label": label
            }
        else:
            payload = {}
        return self.api_query('/v1/deposit/{}/newAddress'.format(currency), payload)

    def withdraw_to_address(self, currency, address, amount):
        """
        This will allow you to withdraw currency from the address
        provided.
        Note: Before you can withdraw cryptocurrency funds to a whitelisted
        address, you need three things: cryptocurrency address whitelists
        needs to be enabled for your account, the address you want to withdraw
        funds to needs to already be on that whitelist and an API key with the
        Fund Manager role added.

        Args:
            current(str): Can either be btc or eth
            address(str): The address you want the money to be sent to
            amount(str): Amount you want to transfer

        Results:
            dict: A dict of the following fields: destination, amount, txHash
        """
        payload = {
            "address": address,
            "amount": amount
        }
        return self.api_query('/v1/withdraw/{}'.format(currency), payload)

    # HeartBeat API
    def revive_hearbeat(self):
        """
        Revive the heartbeat if 'heartbeat' is selected for the API.
        """
        return self.api_query('/v1/heartbeat')
