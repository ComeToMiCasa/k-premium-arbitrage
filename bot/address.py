import csv
import ccxt
from fetch_data import *
import pandas as pd


def get_address_from_csv(file_path, target):
    try:
        with open(file_path, mode="r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row["Currency"] == target:
                    address = row["Address"]
                    tag = row["Tag"]
                    network = row["Network"]
                    return address, tag, network
        print(f"No entry found for {target} in the CSV file.")
        return None, None, None
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return None, None, None


def update_csv_with_network_ids(file_path, output_path, exchange):
    """
    Updates the CSV file with Deposit Network IDs based on available networks from the exchange.

    :param file_path: The path to the input CSV file.
    :param output_path: The path to save the updated CSV file.
    :param exchange: The ccxt exchange instance.
    """
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Create a new column for Deposit Network ID
    df["Deposit Network ID"] = ""

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        currency = row["Currency"]
        deposit_network = row["Deposit Network"]

        # Fetch available networks for the given currency
        available_networks = fetch_available_networks(exchange, currency)

        # Find a matching network and set the Deposit Network ID
        for network_id, network_name in available_networks:
            if deposit_network == network_id:
                df.at[index, "Deposit Network ID"] = network_name
                break

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_path, index=False)

    print(f"Updated CSV file saved as '{output_path}'.")


if __name__ == "__main__":
    update_csv_with_network_ids("address.csv", "address_network.csv", binance_master)
