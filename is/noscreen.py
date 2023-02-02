import sys
import requests
import json
import os
import hashlib

# Example : python noscreen.py setup.json

# Load JSON File
try:
    if os.path.isfile(sys.argv[1]):
        # Read JSON File content
        f = open(sys.argv[1])
        data = json.load(f)
        f.close()
except Exception as exc:
    raise exc

# Setup URL variable
URL = data["url"]

# Get cookie
try:
    # Retrieve the CSRF token first
    client = requests.session()
    client.get(URL)  # sets cookie
    if 'csrftoken' in client.cookies:
        # Django 1.6 and up
        csrftoken = client.cookies['csrftoken']
    else:
        print("Error: csrftoken cookie is missing")
        exit(1)
    # login_data = dict(csrfmiddlewaretoken=csrftoken, next='/abg.html')
    # r = client.post(URL, data=login_data, headers=dict(Referer=URL))
except Exception as exc:
    print("Make sure the Django host is on and accessible")
    raise exc

# Setup variables and POST Request - Loop into list of Intersight(s)
for intersight in data["intersight_list"]:
    if "host" not in intersight:
        HOST = "http://intersight.com"
    else:
        HOST = intersight["host"]
    PUBLIC = intersight["public_key"]
    PRIVATE_FILE = intersight["private_file"]
    try:
        f = open(PRIVATE_FILE)
        PRIVATE = f.read()
        f.close()
    except Exception as exc:
        raise exc
    # Building POST request
    cookies = {
        'csrftoken': csrftoken,
    }
    headers = {
        'Referer': f'{URL}/abg.html',
    }
    data = {
    # 'document_type': 'Excel',
        'csrfmiddlewaretoken': csrftoken,
        'host': f'{HOST}',
        'public_api_key': f'{PUBLIC}',
        'private_api_key': f'{PRIVATE}',
    }
    # POST Request
    try:
        print(f"Sending request on {URL} for {HOST}")
        response = requests.post(f'{URL}/abg.html', cookies=cookies, headers=headers, data=data)
        print(f"Output files saved : staticfiles/mediafiles/intersight_output_{hashlib.sha256((PUBLIC).encode('utf-8')).hexdigest()[:10]}")
    except Exception as exc:
        raise exc
