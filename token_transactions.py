import requests
import json
import time
from web3 import Web3

# Define endpoint for Etherscan API
ETHERSCAN_API_ENDPOINT = 'https://api.etherscan.io/api'

# Load API keys from json file
with open('api_keys.json') as f:
    api_keys = json.load(f)

# Get Etherscan API key
etherscan_api_key = api_keys['etherscan']

# Create web3 instance using Infura endpoint
web3 = Web3(Web3.HTTPProvider(api_keys['infura']))

# Load ERC20 ABI
with open('erc20_abi.json') as f:
    erc20_abi = json.load(f)


def get_token_transactions(token_address):
    """
    Get all transactions for a given ERC20 token

    :param token_address: str, the address of the ERC20 token
    :return: list of dictionaries containing transaction data
    """
    # Get token contract instance
    token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)

    # Get the number of token transfer events
    transfer_filter = token_contract.events.Transfer.createFilter(fromBlock=0)
    transfer_events = transfer_filter.get_all_entries()

    # Get transactions for each transfer event
    transactions = []
    for event in transfer_events:
        tx_hash = event['transactionHash'].hex()
        tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
        if tx_receipt is not None:
            tx_data = tx_receipt['transactionHash'].hex()
            tx_from = tx_receipt['from']
            tx_to = tx_receipt['to']
            tx_value = token_contract.events.Transfer().processReceipt(tx_receipt)[
                0]['args']['value']
            timestamp = web3.eth.getBlock(
                tx_receipt['blockNumber'])['timestamp']
            transactions.append({
                'tx_hash': tx_hash,
                'tx_data': tx_data,
                'tx_from': tx_from,
                'tx_to': tx_to,
                'tx_value': tx_value,
                'timestamp': timestamp,
                'token_address': token_address
            })
        time.sleep(0.1)

    return transactions


if __name__ == '__main__':
    # Example usage
    token_address = '0x3845badAde8e6dFF049820680d1F14bD3903a5d0'
    transactions = get_token_transactions(token_address)
    print(transactions)
