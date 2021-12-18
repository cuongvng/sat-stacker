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

def main():
	# Authenticate
	ts = int(time.time() * 1000)

	signature_payload = f'{ts}'.encode()
	signature = hmac.new(SAT_STACKER_API_SECRET.encode(), signature_payload, 'sha256').hexdigest()

	headers = {}
	
	headers['FTX-KEY'] = SAT_STACKER_API_KEY
	headers['FTX-SIGN'] = signature
	headers['FTX-TS'] = str(ts)
	headers['FTX-SUBACCOUNT'] = SUB_ACCOUNT

	response = requests.get(BASE_ENDPOINT+"/markets/BTC/USD", headers=headers)
	print(response.json())


if __name__ == "__main__":
	main()