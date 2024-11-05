from get_access_token import login
import pandas as pd
from methods import option_chain
import os

print("PRESS 1 FOR LOGIN\nPRESS 2 FOR OPTION CHAIN RETRIVAL")
x = input()

if x =='1':
    login.perform_authentication(os.getenv('API_KEY'), os.getenv('REDIRECT_URL'))
    print("TAKING THE AUTH CODE FROM THE REDIRECT AND ADDING MANUALLY")
    input()
    try:
        login.generate_access_token(os.getenv('AUTH_CODE'), os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('REDIRECT_URL'))
    except Exception as e:
        print(f"Error : {e}")
elif x =='2':
    data = option_chain.get_option_chain_data('NSE_INDEX|Nifty 50', '2024-11-05', 'CE')
    print(data)
    data_w_margin = option_chain.calculate_margin_and_premium(data)
    print(data_w_margin)
else:
    print("TRY AGAIN WITH THE CORRECT OPTION")