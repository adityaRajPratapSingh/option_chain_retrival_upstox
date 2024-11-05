import os
from dotenv import load_dotenv
import webbrowser
import requests

class login:
    def update_env_var(key:str, value, file_path:str=".env")->None:
        load_dotenv(file_path)
        env_vars = {}
        
        if os.path.exists(file_path):
            with open(file_path, "r") as env_file:
                lines = env_file.readlines()
                for line in lines:
                    if line.strip() and "=" in line:
                        var, val = line.strip().split("=", 1)
                        env_vars[var] = val
        else:
            raise Exception("ENVIRONMENT VARIABLE PATH DOES NOT EXIST")
        
        env_vars[key] = value
        with open(file_path, "w") as env_file:
            for var, val in env_vars.items():
                env_file.write(f"{var}={val}\n")
    def perform_authentication(key:str, redirect:str)->None:
        authorization_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={key}&redirect_uri={redirect}"
        firefox = webbrowser.get('firefox')
        print('OPENING BROWSER FOR AUTHORIZATION!!!')
        firefox.open(authorization_url)
    def generate_access_token(code:str, key:str, secret:str, redirect:str)->None:
        access_token_url = 'https://api.upstox.com/v2/login/authorization/token'
        data ={
            'code': code,
            'client_id': key,
            'client_secret': secret,
            'redirect_uri': redirect,
            'grant_type': 'authorization_code'
        }
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(access_token_url, data=data, headers=headers)

        if response.status_code==200:
            print("SUCCESSFULLY RETRIVED THE ACCESS TOKEN")
            try:
                login.update_env_var("ACCESS_TOKEN", response.json().get("access_token"))
            except Exception as e:
                print(f"Error : {e}")
        else:
            raise Exception(f"FAILED TO RETRIVE ACCESS TOKEN \n CODE = {response.status_code} \n RESPONSE = {response.json()}")

