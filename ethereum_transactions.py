import json
import time
from datetime import datetime, timedelta
from typing import List, Tuple
import requests
from web3 import Web3
from requests.exceptions import HTTPError

with open('api_keys.json') as f:
    API_KEYS = json.load(f)

with open('erc20_abi.json') as f:
    ERC20_ABI = json.load(f)


ETHERSCAN_API_KEY = API_KEYS['etherscan']
BINANCE_API_KEY = API_KEYS['binance']
BYBIT_API_KEY = API_KEYS['bybit']


TOKEN_ADDRESSES = [
    '0x3845badAde8e6dFF049820680d1F14bD3903a5d0',  # SAND
    '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942',  # MANA
    '0xb23d80f5FefcDDaa212212F028021B41DEd428CF',  # PRIME
]

EXCHANGES = ['uniswap', 'binance', 'bybit']

# Function to get token price from Uniswap
def get_uniswap_token_price(token_address: str) -> float:
    uniswap_url = f'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
    query = f'''{{
        pair(id: "{token_address.lower()}_weth") {{
            token0Price
        }}
    }}'''
    response = requests.post(uniswap_url, json={'query': query})
    if response.ok:
        result = response.json()
        price = float(result['data']['pair']['token0Price'])
        return price
    else:
        response.raise_for_status()

# Function to get token price from Binance
def get_binance_token_price(token_address: str) -> float:
    binance_url = f'https://api.binance.com/api/v3/ticker/price?symbol={token_address.lower()}usdt'
    headers = {'X-MBX-APIKEY': BINANCE_API_KEY}
    response = requests.get(binance_url, headers=headers)
    if response.ok:
        result = response.json()
        price = float(result['price'])
        return price
    else:
        response.raise_for_status()

# Function to get token price from Bybit
def get_bybit_token_price(token_address: str) -> float:
    bybit_url = f'https://api.bybit.com/v2/public/tickers?symbol={token_address.upper()}USDT'
    headers = {'Referer': 'https://www.bybit.com/'}
    response = requests.get(bybit_url, headers=headers)
    if response.ok:
        result = response.json()
        price = float(result['result'][0]['last_price'])
        return price
    else:
        response.raise_for_status()

# Function to get token price from an exchange
def get_token_price(token_address: str, exchange: str) -> float:
    if exchange == 'uniswap':
        return get_uniswap_token_price(token_address)
    elif exchange == 'binance':
        return get_binance_token_price(token_address)
    elif exchange == 'bybit':
        return get_bybit_token_price(token_address)
    else:
        raise ValueError('Invalid exchange provided')


# Function to get the top token holders for a given token
def get_top_token_holders(token_address: str, num_holders: int = 20) -> List[Tuple[str, float]]:
    w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/your-infura-api-key'))
    contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    holders = {}
    total_supply = contract.functions.totalSupply().call()
    if total_supply == 0:
        return []
    for i in range(0, total_supply, 100):
        chunk = contract.functions.topHolders(i, 100).call()
        for holder in chunk:
            address = Web3.toChecksumAddress(holder[0])
            balance = holder[1] / (10 ** 18)
            if balance > 0 and address != '0x0000000000000000000000000000000000000000':
                holders[address] = holders.get(address, 0) + balance
    sorted_holders = sorted(holders.items(), key=lambda x: x[1], reverse=True)
    return sorted_holders[:num_holders]

# Function to get historical token prices for a given token
def get_historical_token_prices(token_address: str, num_days: int = 30, exchange: str = 'uniswap') -> List[Tuple[str, float]]:
    prices = []
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=num_days)
    current_date = start_date
    while current_date <= end_date:
        timestamp = int(current_date.timestamp())
        try:
            price = get_token_price(token_address, exchange)
            prices.append((datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d'), price))
        except HTTPError as e:
            print(f'Error fetching price for date {current_date}: {e}')
        current_date += timedelta(days=1)
        time.sleep(1)
    return prices

# Function to get the transaction history of a wallet

def get_historic_transactions(wallet_address: str, num_days: int = 30) -> Dict[str, List[Dict]]:
    w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/your-infura-api-key'))
    transactions = {'incoming': [], 'outgoing': []}
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=num_days)
    for token_address in TOKEN_ADDRESSES:
        contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
        transfer_events = contract.events.Transfer().process(
            argument_filters={'to': wallet_address},
            fromBlock=w3.eth.block_number - 50000,
            toBlock='latest'
        )
        for event in transfer_events:
            tx = w3.eth.getTransaction(event['transactionHash'].hex())
            timestamp = w3.eth.getBlock(tx['blockNumber'])['timestamp']
            tx_date = datetime.utcfromtimestamp(timestamp)
            if start_date <= tx_date <= end_date:
                amount = float(event['args']['value']) / (10 ** 18)
                direction = 'incoming'
                if tx['from'] == wallet_address:
                    direction = 'outgoing'
                    amount *= -1
                transactions[direction].append({
                    'date': tx_date,
                    'token': token_address,
                    'amount': amount,
                    'tx_hash': event['transactionHash'].hex(),
                    'from': tx['from'],
                    'to': tx['to'],
                    'block_number': tx['blockNumber']
                })
    return transactions











# import json
# import time
# from datetime import datetime, timedelta
# from typing import List, Tuple
# import requests
# from web3 import Web3
# from requests.exceptions import HTTPError

# with open('api_keys.json') as f:
#     API_KEYS = json.load(f)

# with open('erc20_abi.json') as f:
#     ERC20_ABI = json.load(f)


# ETHERSCAN_API_KEY = API_KEYS['etherscan']
# BINANCE_API_KEY = API_KEYS['binance']
# BYBIT_API_KEY = API_KEYS['bybit']


# TOKEN_ADDRESSES = [
#     '0x3845badAde8e6dFF049820680d1F14bD3903a5d0',  # SAND
#     '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942',  # MANA
#     '0xb23d80f5FefcDDaa212212F028021B41DEd428CF',  # PRIME
# ]

# EXCHANGES = ['uniswap', 'binance', 'bybit']

# # Function to get token price from Uniswap
# def get_uniswap_token_price(token_address: str) -> float:
#     uniswap_url = f'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
#     query = f'''{{
#         pair(id: "{token_address.lower()}_weth") {{
#             token0Price
#         }}
#     }}'''
#     response = requests.post(uniswap_url, json={'query': query})
#     if response.ok:
#         result = response.json()
#         price = float(result['data']['pair']['token0Price'])
#         return price
#     else:
#         response.raise_for_status()

# # Function to get token price from Binance
# def get_binance_token_price(token_address: str) -> float:
#     binance_url = f'https://api.binance.com/api/v3/ticker/price?symbol={token_address.lower()}usdt'
#     headers = {'X-MBX-APIKEY': BINANCE_API_KEY}
#     response = requests.get(binance_url, headers=headers)
#     if response.ok:
#         result = response.json()
#         price = float(result['price'])
#         return price
#     else:
#         response.raise_for_status()

# # Function to get token price from Bybit
# def get_bybit_token_price(token_address: str) -> float:
#     bybit_url = f'https://api.bybit.com/v2/public/tickers?symbol={token_address.upper()}USDT'
#     headers = {'Referer': 'https://www.bybit.com/'}
#     response = requests.get(bybit_url, headers=headers)
#     if response.ok:
#         result = response.json()
#         price = float(result['result'][0]['last_price'])
#         return price
#     else:
#         response.raise_for_status()

# # Function to get token price from an exchange
# def get_token_price(token_address: str, exchange: str) -> float:
#     if exchange == 'uniswap':
#         return get_uniswap_token_price(token_address)
#     elif exchange == 'binance':
#         return get_binance_token_price(token_address)
#     elif exchange == 'bybit':
#         return get_bybit_token_price(token_address)
#     else:
#         raise ValueError('Invalid exchange provided')

# # Function to get the top token holders for a given token
# def get_top_token_holders(token_address: str, num_holders: int = 20) -> List[Tuple[str, float]]:
#     w3 = Web3(Web3
# ###########################################################

# def get_top_token_holders(token_address: str, num_holders: int = 20) -> List[Tuple[str, float]]:
#     """
#     Function to get the top token holders for a given token

#     :param token_address: Address of the token contract
#     :param num_holders: Number of top token holders to retrieve
#     :return: List of tuples with token holder addresses and their balances
#     """
#     try:
#         # Get the token contract
#         contract = w3.eth.contract(address=Web3.toChecksumAddress(token_address), abi=token_abi)

#         # Get the token total supply
#         total_supply = contract.functions.totalSupply().call()

#         # Get the top token holders and their balances
#         top_holders = []
#         holder_balances = {}
#         for i, holder in enumerate(contract.functions.topTokenHolders(num_holders).call()):
#             holder_address = holder[0]
#             holder_balance = holder[1]
#             holder_balances[holder_address] = holder_balance
#             percentage = (holder_balance / total_supply) * 100
#             top_holders.append((holder_address, holder_balance, percentage))
#         return top_holders
#     except Exception as e:
#         print(f"Error getting top token holders: {str(e)}")
#         return []


# def get_token_balances(token_address: str, wallet_addresses: List[str]) -> Dict[str, float]:
#     """
#     Function to get the token balances for a list of wallet addresses

#     :param token_address: Address of the token contract
#     :param wallet_addresses: List of wallet addresses
#     :return: Dictionary with wallet addresses as keys and token balances as values
#     """
#     try:
#         # Get the token contract
#         contract = w3.eth.contract(address=Web3.toChecksumAddress(token_address), abi=token_abi)

#         # Get the token balances for the given wallet addresses
#         balances = {}
#         for wallet_address in wallet_addresses:
#             balance = contract.functions.balanceOf(wallet_address).call()
#             balances[wallet_address] = balance
#         return balances
#     except Exception as e:
#         print(f"Error getting token balances: {str(e)}")
#         return {}


# def get_total_token_balances(wallet_addresses: List[str]) -> Dict[str, float]:
#     """
#     Function to get the total token balances for a list of wallet addresses

#     :param wallet_addresses: List of wallet addresses
#     :return: Dictionary with token addresses as keys and total token balances as values
#     """
#     try:
#         # Get the token balances for each wallet address
#         token_balances = {}
#         for wallet_address in wallet_addresses:
#             for token_address in wallet_tokens[wallet_address]:
#                 if token_address not in token_balances:
#                     token_balances[token_address] = 0
#                 contract = w3.eth.contract(address=Web3.toChecksumAddress(token_address), abi=token_abi)
#                 balance = contract.functions.balanceOf(wallet_address).call()
#                 token_balances[token_address] += balance
#         return token_balances
#     except Exception as e:
#         print(f"Error getting total token balances: {str(e)}")
#         return {}


# def get_historic_transactions() -> Dict[str, List[Dict]]:
#     """
#     Function to get historic transactions for a list of wallet addresses

#     :return: Dictionary with wallet addresses as keys and a list of historic transactions as values
#     """
#     try:
#         # Get the historic transactions for each wallet address
#         historic_transactions = {}
#         for wallet_address in wallet_addresses:
#             tx_list = []
#             for tx_hash in reversed(get_transaction_hashes



# ############################################################

# def get_token_price(token_address: str, exchange: str) -> float:
#     """
#     Function to get token price from an exchange

#     :param token_address: The token address of the token to get the price for
#     :type token_address: str
#     :param exchange: The exchange to get the token price from. Valid values are 'uniswap', 'binance', and 'bybit'.
#     :type exchange: str
#     :return: The current token price
#     :rtype: float
#     """
#     if exchange == 'uniswap':
#         # Get the token price from Uniswap
#         uniswap_url = f"https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2?query={{bundle(id: 1){{ethPrice}}pair(id: \"{token_address}\"){{token0{{symbol}}token1{{symbol}}token0Price}}}}}"
#         response = requests.post(uniswap_url)
#         result = response.json()['data']['pair']['token1Price']
#     elif exchange == 'binance':
#         # Get the token price from Binance
#         binance_url = f"https://api.binance.com/api/v3/ticker/price?symbol={token_address.upper()}USDT"
#         response = requests.get(binance_url)
#         result = response.json()['price']
#     elif exchange == 'bybit':
#         # Get the token price from Bybit
#         bybit_url = f"https://api.bybit.com/v2/public/tickers?symbol={token_address.upper()}USDT"
#         response = requests.get(bybit_url)
#         result = response.json()['result'][0]['last_price']
#     else:
#         raise ValueError("Invalid exchange")

#     return float(result)


# def get_token_transactions(token_address: str) -> List[Dict[str, Any]]:
#     """
#     Function to get a list of recent transactions for a given token

#     :param token_address: The token address of the token to get the transactions for
#     :type token_address: str
#     :return: A list of recent transactions for the given token
#     :rtype: List[Dict[str, Any]]
#     """
#     # Get the contract instance for the token
#     contract_instance = w3.eth.contract(address=Web3.toChecksumAddress(token_address), abi=erc20_abi)

#     # Get the last block number
#     last_block_number = w3.eth.block_number - 1

#     # Get all the logs for the token contract
#     logs = w3.eth.get_logs({
#         'fromBlock': last_block_number - 1000,
#         'toBlock': last_block_number,
#         'address': Web3.toChecksumAddress(token_address),
#         'topics': [TRANSFER_TOPIC]
#     })

#     # Parse the logs to get the transaction data
#     transactions = []
#     for log in logs:
#         transaction = parse_log(log, contract_instance)
#         if transaction['from'] is not None and transaction['to'] is not None:
#             transactions.append(transaction)

#     return transactions


# def get_historic_transactions() -> List[Dict[str, Any]]:
#     """
#     Function to get all historic transactions for a list of tokens

#     :return: A list of historic transactions for the specified tokens
#     :rtype: List[Dict[str, Any]]
#     """
#     historic_transactions = []
#     for token_address in TOKEN_ADDRESSES:
#         token_transactions = get_token_transactions(token_address)
#         for transaction in token_transactions:
#             token_price = get_token_price(token_address, 'uniswap')