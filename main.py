import requests
import random
import string
import json
import hashlib
from faker import Faker
import asyncio

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def create_1secmail_account(domain):
    fake = Faker()
    username = "Wiegine"+generate_random_string(10).lower()
    email = f"{username}@{domain}".lower()  
    password = fake.password()
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
    first_name = fake.first_name()
    last_name = fake.last_name()
    print(f'[√] Email Created: {email}')
    return email, password, first_name, last_name, birthday

async def fetch_email_messages(email):
    login, domain = email.split('@')
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                messages = response.json()
                if messages:
                    return messages
            else:
                print(f'[×] Fetch Email Error : {response.text}')
        except Exception as e:
            print(f'[×] Error : {e}')
        await asyncio.sleep(5)  

def register_facebook_account(email, password, first_name, last_name, birthday):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice(['M', 'F'])
    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'EN',
        'fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod',
        'fb_api_req_friendly_name': 'registerAccount',
        'firstname': first_name,
        'format': 'json',
        'gender': gender,
        'lastname': last_name,
        'email': email,
        'locale': 'en_US',
        'method': 'user.register',
        'password': password,
        'reg_instance': generate_random_string(32),
        'return_multiple_errors': True
    }
    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    print(sorted_req)
    print(sig)
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    print(ensig)
    req['sig'] = ensig
    api_url = 'https://b-api.facebook.com/method/user.register'
    reg = _call(api_url, req)
    id = reg['new_user_id']
    token = reg['session_info']['access_token']
    print(f'''[+] Email : {email}
[+] ID : {id}
[+] Token : {token}
[+] PassWord : {password}
[+] Name : {first_name} {last_name}
[+] BirthDay : {birthday}
[+] Gender : {gender}
===================================''')
    return id, token

def login_facebook_account(email, password):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    req = {
        'api_key': api_key,
        'email': email,
        'format': 'json',
        'locale': 'en_US',
        'method': 'auth.login',
        'password': password,
        'return_ssl_resources': 0,
        'v': '1.0'
    }
    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    req['sig'] = ensig
    api_url = 'https://api.facebook.com/restserver.php'
    response = _call(api_url, req)
    print(f'[+] Logged in with Email : {email}')
    return response

def _call(url, params, post=True):
    headers = {'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'}
    if post:
        response = requests.post(url, data=params, headers=headers)
    else:
        response = requests.get(url, params=params, headers=headers)
    return response.json()

specific_domains = ["1secmail.com", "1secmail.net"]

async def main():
    for i in range(int(input('[+] How Many Accounts : '))):
        domain = random.choice(specific_domains)
        email, password, first_name, last_name, birthday = create_1secmail_account(domain)
        if email and password and first_name and last_name and birthday:
            id, token = register_facebook_account(email, password, first_name, last_name, birthday)
            login_response = login_facebook_account(email, password)
            print(f"Fetching email messages for {email}...")
            messages = await fetch_email_messages(email)
            if messages:
                print(f"Email messages for {email}:")
                for message in messages:
                    print(f'From: {message["from"]}\nSubject: {message["subject"]}\nDate: {message["date"]}\n')

asyncio.run(main())
