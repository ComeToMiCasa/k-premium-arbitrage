import requests
import uuid
import base64
import hashlib
import json
import hmac
import time

from exchanges import coinone_api_key, coinone_api_secret


def call_coinone_api(url, method, data, version=2):
    """
    Generic function to call a Coinone API endpoint.

    :param url: The API URL to call.
    :param method: The HTTP request method (e.g., 'GET', 'POST').
    :param data: The data to include in the payload.
    :return: The response data from the API call.
    :version: 1 or 2. If 1, nonce is a unix timestamp. If 2, nonce is a uuid.
    """
    # Generate a nonce using UUID
    nonce = str(uuid.uuid4()) if version == 2 else int(time.time())

    # Prepare the payload for the request
    payload = {
        "access_token": coinone_api_key,
        "nonce": nonce,
    }
    payload.update(data)

    # Encode the payload to base64
    encoded_payload = base64.b64encode(json.dumps(payload).encode("utf-8"))

    # Generate a signature using HMAC-SHA512
    signature = hmac.new(
        coinone_api_secret.encode("utf-8"), encoded_payload, hashlib.sha512
    ).hexdigest()

    # Set the headers for the request
    headers = {
        "Content-Type": "application/json",
        "X-COINONE-PAYLOAD": encoded_payload,
        "X-COINONE-SIGNATURE": signature,
    }

    # Make the HTTP request to the Coinone API
    if method.upper() == "POST":
        response = requests.post(url, headers=headers, data=encoded_payload)
    elif method.upper() == "GET":
        response = requests.get(url, headers=headers, data=encoded_payload)
    else:
        raise ValueError("Unsupported HTTP method. Use 'GET' or 'POST'.")

    # Parse the response data
    data = response.json()

    # Check for errors in the response
    if data.get("result") != "success":
        print(f"Error during API call: {data.get('errorMessage')}")
        print(data)
        return None

    # Return the response data
    return data
