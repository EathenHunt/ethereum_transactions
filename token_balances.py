import requests
import json
from web3 import Web3

# Replace with the token address you want to monitor
TOKEN_ADDRESS = '0x3845badAde8e6dFF049820680d1F14bD3903a5d0'

# API endpoints for getting token balances
UNISWAP_API = f'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2?query=\
{{pairs(where: {{token0: "{TOKEN_ADDRESS}"}}) {{token1Price}}}}'

BYBIT_API = f'https://api.bybit.com/v2/public/tickers?symbol={TOKEN_ADDRESS}USDT'

BINANCE_API = f'https://api.binance.com/api/v3/ticker/price?symbol={TOKEN_ADDRESS}USDT'

# Web3 connection
w3 = Web3(Web3.HTTPProvider(
    'https://mainnet.infura.io/v3/your_infura_project_id'))

# Replace with your Ethereum address
MY_ADDRESS = '0x1234567890123456789012345678901234567890'

# Get the token balance for the specified address
token_balance = w3.eth.get_balance(TOKEN_ADDRESS)
token_balance = token_balance / 10 ** 18

# Get the token prices from different exchanges
uniswap_price = json.loads(requests.get(UNISWAP_API).text)[
    'data']['pairs'][0]['token1Price']
bybit_price = json.loads(requests.get(BYBIT_API).text)[
    'result'][0]['last_price']
binance_price = json.loads(requests.get(BINANCE_API).text)['price']

# Calculate the value of the token holdings
uniswap_value = uniswap_price * token_balance
bybit_value = bybit_price * token_balance
binance_value = binance_price * token_balance
total_value = uniswap_value + bybit_value + binance_value

# Print the token balance and values
print(f'Token Balance: {token_balance}')
print(f'Uniswap Price: {uniswap_price} | Uniswap Value: {uniswap_value}')
print(f'Bybit Price: {bybit_price} | Bybit Value: {bybit_value}')
print(f'Binance Price: {binance_price} | Binance Value: {binance_value}')
print(f'Total Value: {total_value}')
