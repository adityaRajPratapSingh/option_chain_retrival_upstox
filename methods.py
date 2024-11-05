import pandas as pd
import requests
from datetime import datetime
import os

class option_chain:
    def get_option_chain_data(instrument_name: str, expiry_date: str, side: str) -> pd.DataFrame:

        if side == 'CE':
            variable = 'ask_price'
        elif side == 'PE':
            variable = 'bid_price'
        else:
            raise Exception("INVALID SIDE")
        try:
            datetime.strptime(expiry_date, "%Y-%m-%d")
        except Exception:
            raise Exception(f"Invalid date format: '{expiry_date}'. Expected format is YYYY-MM-DD.")
        
        url_chain = 'https://api.upstox.com/v2/option/chain'
        params_chain = {
            'instrument_key': instrument_name,
            'expiry_date': expiry_date
        }
        headers_chain = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.getenv("ACCESS_TOKEN")}'
        }
        response_chain = requests.get(url_chain, params=params_chain, headers=headers_chain)
        if response_chain.status_code == 200:
            data_chain = response_chain.json().get('data', [])
            print("CHAIN FETCH SUCCESSFUL")
        else:
            raise Exception(f"FAILED FETCHING THE OPTION CHAIN \n CODE = {response_chain.status_code} \n RESPONSE = {response_chain.json()}")
        
        url_contracts = f'https://api.upstox.com/v2/option/contract?instrument_key={instrument_name}&expiry_date={expiry_date}'
        headers_contracts = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.getenv("ACCESS_TOKEN")}'
        }
        response_contracts = requests.get(url_contracts, headers=headers_contracts)
        if response_contracts.status_code == 200:
            data_contracts = response_contracts.json().get('data', [])
            print("CONTRACTS FETCH SUCCESSFUL")
        else:
            raise Exception(f"FAILED FETCHING THE OPTION CONTRACTS \n CODE = {response_contracts.status_code} \n RESPONSE = {response_contracts.json()}")
        
        df = pd.DataFrame({"instrument_name":[], "strike_price":[], "side":[], "bid/ask":[], "lot_size":[], "instrument_key":[]})
        for option,contract in zip(data_chain, data_contracts):
            strike_price = option['strike_price']
            val = max(
                option['call_options']['market_data'][variable],
                option['put_options']['market_data'][variable]
            )
            lot = contract['lot_size']
            instrument_key = contract['instrument_key']
            df=df.append({"instrument_name": instrument_name, "strike_price": strike_price, "side": side, "bid/ask": val, "lot_size":lot, "instrument_key":instrument_key})
        
        return df
    def calculate_margin_and_premium(data: pd.DataFrame) -> pd.DataFrame:
        url = "https://api.upstox.com/v2/charges/margin"
        headers = {
            "accept": "application/json",
            "Authorization": f'Bearer {os.getenv("ACCESS_TOKEN")}',
            "Content-Type": "application/json"
        }
        df = pd.DataFrame({"margin_required":[], "premium_earned":[]})
        margins = []
        premiums = []
        keys = data['instrument_key']
        lots = data['lot_size']
        for key,lot in zip(keys, lots):
            data = {
                "instruments": [
                    {
                        "instrument_key": key,
                        "quantity": 1,
                        "transaction_type": "SELL",
                        "product": "D"
                    }
                ]
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code==200:
                margin = response.json().get('data', {})['final_margin']
                margins.append(margin)
                premiums.append(margin*lot)
            else:
                raise Exception(F"COULD NOT FETCH MARGIN FOR THE KEY = {key}")
        
        new_row = pd.DataFrame([{"margin_required": margins, "premium_earned": premiums}])
        df = pd.concat([df, new_row], ignore_index=True)
        data_w_margins = pd.concat([data, df], axis=1)
        return data_w_margins