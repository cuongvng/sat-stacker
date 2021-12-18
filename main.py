from dotenv import load_dotenv
import os

import requests 
load_dotenv()

import time
import hmac
import json
from requests import Request

SAT_STACKER_API_KEY = os.getenv("SAT_STACKER_API_KEY")
SAT_STACKER_API_SECRET = os.getenv("SAT_STACKER_API_SECRET")
BASE_ENDPOINT = "https://ftx.com/api"
SUB_ACCOUNT = os.getenv("SUB_ACCOUNT")

def authenticate(method, end_point_path):
	ts = int(time.time() * 1000)
	signature_payload = f'{ts}{method}/api{end_point_path}'.encode()
	signature = hmac.new(SAT_STACKER_API_SECRET.encode(), signature_payload, 'sha256').hexdigest()
	return ts, signature

def place_spot_market_order():
	pass

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
	

if __name__ == "__main__":
	get_account_info()