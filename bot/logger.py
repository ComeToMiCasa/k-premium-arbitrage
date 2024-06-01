import csv
import time

# Define the CSV file path and headers
CSV_FILE_PATH = 'order_details.csv'
CSV_HEADERS = ['timestamp', 'target_buy_avg_price', 'target_buy_quantity', 'target_buy_total_cost', 'target_buy_fee',
               'target_sell_avg_price', 'target_sell_quantity', 'target_sell_total_cost', 'target_sell_fee',
               'medium_buy_avg_price', 'medium_buy_quantity', 'medium_buy_total_cost', 'medium_buy_fee',
               'medium_sell_avg_price', 'medium_sell_quantity', 'medium_sell_total_cost', 'medium_sell_fee']


def log_order_details_to_csv(order_details):
    """
    Writes the order details to a new row in the CSV file.

    :param order_details: A dictionary with the order details for target buy, target sell, medium buy, and medium sell.
    """
    with open(CSV_FILE_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write headers if the file is empty
        if file.tell() == 0:
            writer.writerow(CSV_HEADERS)

        # Extract details
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        target_buy = order_details.get('target_buy', {})
        target_sell = order_details.get('target_sell', {})
        medium_buy = order_details.get('medium_buy', {})
        medium_sell = order_details.get('medium_sell', {})

        row = [
            timestamp,
            target_buy.get('average_price', ''),
            target_buy.get('quantity', ''),
            target_buy.get('total_cost', ''),
            target_buy.get('fee', ''),
            target_sell.get('average_price', ''),
            target_sell.get('quantity', ''),
            target_sell.get('total_cost', ''),
            target_sell.get('fee', ''),
            medium_buy.get('average_price', ''),
            medium_buy.get('quantity', ''),
            medium_buy.get('total_cost', ''),
            medium_buy.get('fee', ''),
            medium_sell.get('average_price', ''),
            medium_sell.get('quantity', ''),
            medium_sell.get('total_cost', ''),
            medium_sell.get('fee', '')
        ]

        writer.writerow(row)
