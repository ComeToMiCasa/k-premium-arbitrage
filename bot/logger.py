import csv
import time

# Define the CSV file path and headers
CSV_FILE_PATH = 'order_details.csv'
CSV_HEADERS = ['timestamp', 'target_buy_avg_price', 'target_buy_quantity', 'target_buy_total_cost', 'target_buy_fee',
               'target_sell_avg_price', 'target_sell_quantity', 'target_sell_total_cost', 'target_sell_fee',
               'medium_buy_avg_price', 'medium_buy_quantity', 'medium_buy_total_cost', 'medium_buy_fee',
               'medium_sell_avg_price', 'medium_sell_quantity', 'medium_sell_total_cost', 'medium_sell_fee']


def log_order_details_to_csv(timestamp, buy_details, short_details, sell_details, close_short_details, filename='order_log.csv'):
    """
    Logs the order details to a CSV file.

    :param timestamp: The timestamp of the order.
    :param buy_details: The details of the buy order.
    :param short_details: The details of the short order.
    :param sell_details: The details of the sell order.
    :param close_short_details: The details of the close short order.
    :param filename: The name of the CSV file to log to.
    """
    fieldnames = ['timestamp', 'buy_order', 'buy_average_price', 'buy_quantity', 'buy_total_cost', 'buy_fee',
                  'short_order', 'short_average_price', 'short_quantity', 'short_total_cost', 'short_fee',
                  'sell_order', 'sell_average_price', 'sell_quantity', 'sell_total_cost', 'sell_fee',
                  'close_short_order', 'close_short_average_price', 'close_short_quantity', 'close_short_total_cost', 'close_short_fee']

    row = {
        'timestamp': timestamp,
        'buy_order': buy_details['order']['id'] if buy_details else None,
        'buy_average_price': buy_details['average_price'] if buy_details else None,
        'buy_quantity': buy_details['quantity'] if buy_details else None,
        'buy_total_cost': buy_details['total_cost'] if buy_details else None,
        'buy_fee': buy_details['fee'] if buy_details else None,
        'short_order': short_details['order']['id'] if short_details else None,
        'short_average_price': short_details['average_price'] if short_details else None,
        'short_quantity': short_details['quantity'] if short_details else None,
        'short_total_cost': short_details['total_cost'] if short_details else None,
        'short_fee': short_details['fee'] if short_details else None,
        'sell_order': sell_details['order']['id'] if sell_details else None,
        'sell_average_price': sell_details['average_price'] if sell_details else None,
        'sell_quantity': sell_details['quantity'] if sell_details else None,
        'sell_total_cost': sell_details['total_cost'] if sell_details else None,
        'sell_fee': sell_details['fee'] if sell_details else None,
        'close_short_order': close_short_details['order']['id'] if close_short_details else None,
        'close_short_average_price': close_short_details['average_price'] if close_short_details else None,
        'close_short_quantity': close_short_details['quantity'] if close_short_details else None,
        'close_short_total_cost': close_short_details['total_cost'] if close_short_details else None,
        'close_short_fee': close_short_details['fee'] if close_short_details else None
    }

    # Write to CSV file
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(row)
