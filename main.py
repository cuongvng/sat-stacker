from dotenv import load_dotenv
import os
load_dotenv()

import requests 
import time
import hmac
import json

SAT_STACKER_API_KEY = os.getenv("SAT_STACKER_API_KEY")
SAT_STACKER_API_SECRET = os.getenv("SAT_STACKER_API_SECRET")
BASE_ENDPOINT = "https://ftx.com/api"
SUB_ACCOUNT = os.getenv("SUB_ACCOUNT")
EMAIL = os.getenv("EMAIL")

def authenticate(method, end_point_path, payload=None):
	ts = int(time.time() * 1000)
	signature_payload = f'{ts}{method}/api{end_point_path}'.encode()
	if payload:
		signature_payload = f'{ts}{method}/api{end_point_path}{payload}'.encode()

	signature = hmac.new(SAT_STACKER_API_SECRET.encode(), signature_payload, 'sha256').hexdigest()
	return ts, signature

def get_account_info():
	# Authenticate
	METHOD = "GET"
	END_POINT_PATH = "/account"
	ts, signature = authenticate(METHOD, END_POINT_PATH)

	# Request
	headers = {}
	headers['FTX-KEY'] = SAT_STACKER_API_KEY
	headers['FTX-SIGN'] = signature
	headers['FTX-TS'] = str(ts)
	headers['FTX-SUBACCOUNT'] = SUB_ACCOUNT

	response = requests.get(BASE_ENDPOINT+END_POINT_PATH, headers=headers)
	
	if response.status_code == 200:
		print(response.json()["result"])
	else:
		print("Error:", response.json()["error"])
	
def stack_sats():
	"""
	POST signature example (from https://blog.ftx.com/blog/api-authentication/):

	signature_payload = b'1588591856950POST/api/orders{"market": "BTC-PERP", "side": "buy", "price": 8500, "size": 1, "type": "limit", "reduceOnly": false, "ioc": false, "postOnly": false, "clientId": null}'
	"""

	# Place a spot market order
	MIN_ORDER_SIZE = 0.0001
	payload = json.dumps({
		"market": "BTC/USD",
		"side": "buy",
		"price": None,
		"size": MIN_ORDER_SIZE,
		"type": "market",
		"reduceOnly": False,
		"ioc": False,
		"postOnly": False,
		"clientId": None
	})
	# Authenticate
	METHOD = "POST"
	END_POINT_PATH = "/orders"
	ts, signature = authenticate(METHOD, END_POINT_PATH, payload)

	# Request
	headers = {
		'FTX-KEY': SAT_STACKER_API_KEY,
		'FTX-SIGN': signature,
		'FTX-TS': str(ts),
		'FTX-SUBACCOUNT': SUB_ACCOUNT
	}

	response = requests.post(BASE_ENDPOINT+END_POINT_PATH, data=payload, headers=headers)
	if response.status_code == 200:
		print(response.json()["result"])
	else:
		# Send me an email
		print("Error:", response.json()["error"])
		print(response.json())

if __name__ == "__main__":
	# get_account_info()
	stack_sats()