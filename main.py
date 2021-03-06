from __future__ import print_function
import hmac
import time
import urllib.parse
from typing import Optional, Dict, Any, List
from requests import Request, Session, Response
from dotenv import load_dotenv
import os
load_dotenv()

BTC_USD = "BTC/USD"	
class FtxClient:
	def __init__(
		self,
		base_url: str = "https://ftx.com/api/",
		api_key: Optional[str] = os.getenv("SAT_STACKER_API_KEY"),
		api_secret: Optional[str] = os.getenv("SAT_STACKER_API_SECRET"),
		subaccount_name: Optional[str] = os.getenv("SUB_ACCOUNT"),
	) -> None:
		self._session = Session()
		self._base_url = base_url
		self._api_key = api_key
		self._api_secret = api_secret
		self._subaccount_name = subaccount_name

	def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
		return self._request('GET', path, params=params)

	def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
		return self._request('POST', path, json=params)

	def _request(self, method: str, path: str, **kwargs) -> Any:
		request = Request(method, self._base_url + path, **kwargs)
		if self._api_key:
			self._sign_request(request)
		response = self._session.send(request.prepare())

		return self._process_response(response)

	def _sign_request(self, request: Request) -> None:
		ts = int(time.time() * 1000)
		prepared = request.prepare()
		signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode(
		)
		if prepared.body:
			signature_payload += prepared.body
		signature = hmac.new(self._api_secret.encode(), signature_payload,
							 'sha256').hexdigest()
		request.headers['FTX-KEY'] = self._api_key
		request.headers['FTX-SIGN'] = signature
		request.headers['FTX-TS'] = str(ts)
		if self._subaccount_name:
			request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(
				self._subaccount_name)

	@staticmethod
	def _process_response(response: Response) -> Any:
		try:
			data = response.json()
		except ValueError:
			response.raise_for_status()
			raise
		else:
			if not data['success']:
				raise Exception(data['error'])
			return data['result']

	#
	# Authentication required methods
	#
	def authentication_required(fn):
		"""Annotation for methods that require auth."""

		def wrapped(self, *args, **kwargs):
			if not self._api_key:
				raise TypeError("You must be authenticated to use this method")
			else:
				return fn(self, *args, **kwargs)

		return wrapped

	@authentication_required
	def get_account_info(self) -> dict:
		return self._get('account')

	@authentication_required
	def get_order_history(self,
						  market: Optional[str] = None,
						  side: Optional[str] = None,
						  order_type: Optional[str] = None,
						  start_time: Optional[float] = None,
						  end_time: Optional[float] = None) -> List[dict]:
		return self._get(
			'orders/history', {
				'market': market,
				'side': side,
				'orderType': order_type,
				'start_time': start_time,
				'end_time': end_time
			})

	def get_market(self, market: str) -> dict:
		return self._get(f'markets/{market}')

	@authentication_required
	def stack_sats(self,
					market: str = BTC_USD,
					side: str = "buy",
					size: float = 0.0001,
					price: Optional[float] = None,
					type: str = 'market',
					reduce_only: bool = False,
					ioc: bool = False,
					post_only: bool = False,
					client_id: Optional[str] = None,
					reject_on_price_band: Optional[bool] = False) -> dict:
		order = self._post(
			'orders', {
				'market': market,
				'side': side,
				'price': price,
				'size': size,
				'type': type,
				'reduceOnly': reduce_only,
				'ioc': ioc,
				'postOnly': post_only,
				'clientId': client_id,
				'rejectOnPriceBand': reject_on_price_band
			})
		# Wait a second for order to be filled
		time.sleep(1)
		return self._get(f"orders/{order['id']}")

def notify_me(message, info):
	import smtplib
	from email.message import EmailMessage

	sender = os.getenv("SENDER")
	receiver = os.getenv("EMAIL")
	password = os.getenv("SENDER_PASSWORD")

	msg = EmailMessage()
	msg['subject'] = "Sat-Stacker" + info
	msg['from'] = sender
	msg['to'] = receiver
	msg.set_content(message)

	with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
		smtp.login(sender, password)
		smtp.send_message(msg)
		print("Email Sent!")

if __name__ == "__main__":
	client = FtxClient()
	prices = client.get_market(BTC_USD)
	ask_price = prices["ask"]
	if ask_price < 35000.0:
		order_size = 0.0003
	else:
		order_size = 0.0002

	try:
		result = client.stack_sats(size=order_size)
		
		filledSize = result["filledSize"]
		avgFillPrice = result["avgFillPrice"]
		info = f"Stacked {filledSize} BTCs = {int(filledSize*10**8)} SATs for {avgFillPrice*filledSize:2f} USD, at price {avgFillPrice:.0f}!"
		print(info)
		print(result)
		# notify_me(info, " ORDER CONFIRMATION")
	
	except Exception as ex:
		print("ERROR:", ex)
		notify_me(str(ex), " ERROR!!!")