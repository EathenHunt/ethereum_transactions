import requests
import pandas as pd

# Replace with the token address you want to monitor
TOKEN_ADDRESS = '0x3845badAde8e6dFF049820680d1F14bD3903a5d0'
# Replace with the number of top holders you want to display
NUM_HOLDERS = 20

# API endpoint for getting token holders
HOLDERS_API = f'https://api.ethplorer.io/getTopTokenHolders/{TOKEN_ADDRESS}?apiKey=freekey'

# Get the token holders
response = requests.get(HOLDERS_API)
holders_data = response.json()['holders']

# Create a DataFrame of the token holders
holders_df = pd.DataFrame(holders_data)
holders_df['balance'] = holders_df['balance'] / 10 ** 18
holders_df = holders_df[['address', 'balance']].head(NUM_HOLDERS)

# Print the top token holders
print(f'Top {NUM_HOLDERS} holders of {TOKEN_ADDRESS}:')
print(holders_df)
