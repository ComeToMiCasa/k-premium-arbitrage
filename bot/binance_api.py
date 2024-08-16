import time
import hashlib
import hmac
import requests
import urllib.parse
import os


from exchanges import binance_master_api_key, binance_master_api_secret


def call_binance_api(url, method, data):
    # Get the current timestamp
    timestamp = int(time.time() * 1000)

    # Add the timestamp to the data dictionary
    data["timestamp"] = timestamp

    # Create the query string from the data dictionary
    query_string = urllib.parse.urlencode(data)

    # Sign the query string with your secret key
    signature = hmac.new(
        binance_master_api_secret.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Append the signature to the query string
    query_string += f"&signature={signature}"

    # Set the headers
    headers = {"X-MBX-APIKEY": binance_master_api_key}

    # Construct the final URL
    full_url = f"{url}?{query_string}"

    # Make the API call based on the method provided
    if method.upper() == "GET":
        response = requests.get(full_url, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(full_url, headers=headers)
    elif method.upper() == "DELETE":
        response = requests.delete(full_url, headers=headers)
    elif method.upper() == "PUT":
        response = requests.put(full_url, headers=headers)
    else:
        raise ValueError("Unsupported HTTP method")

    # Return the JSON response or error
    if response.status_code == 200:
        return response.json()
    else:
        return response.json()


# Example usage
# url = "https://api.binance.com/sapi/v1/capital/withdraw/history"
# method = "GET"
# data = {"coin": "TRX", "status": 6, "limit": 5}

# response = call_binance_api(
#     url, method, data, binance_master_api_key, binance_master_api_secret
# )
# print(response)
