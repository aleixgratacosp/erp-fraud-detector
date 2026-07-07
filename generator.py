import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import config

"""
LOG STRUCTURE
FIELD	TYPE
Transaction_ID	String
User_ID	String
Customer_ID	String
Product_Category	String
Total_Amount	Float
Discount_Percent	Float
Order_Timestamp	DateTime
Order_Status	Enum
Shipping_Date	Date
Invoice_Date	Date
"""

class LogGenerator:

    # ========= Private functions =========

    def __init__(self):
        self.fake = Faker('es_ES')  
        self.current_id = config.START_TRANSACTION_ID

        self.customers_list = []
        for _ in range(config.CUSTOMER_AMOUNT):
            company_name = self.fake.company()
            self.customers_list.append(company_name)
    """ Handles transaction numbers: xxxx2, xxxx4 and so on """
    def _generate_transaction_id(self):
        new_id = self.current_id 
        self.current_id += 2
        return str(new_id)
    
    def _get_random_customer(self):
        """ 
        This function chooses and returns a customer from the list. 
        Also generates new customers with a config.NEW_CUSTOMER_CHANCE_PERCENTAGE probability, and returns it.
        """

        if random.random() < config.NEW_CUSTOMER_CHANCE_PERCENTAGE / 100:
            new_customer = self.fake.company()
            self.customers_list.append(new_customer)
            return new_customer
        
        return random.choice(self.customers_list)
    
    def _get_random_category(self):
        name = random.choice(list(config.CATEGORIES.keys()))
        return name, config.CATEGORIES[name]
    
    """ OLD VERSION
    def _calculate_pricing(self, category_info):
        # Calculates a price between a variation of +30% or -30% from the average price
        price = round(random.uniform(category_info.avg_price * 0.7, category_info.avg_price * 1.3), 2)
        # Calculates a discount from 0 up to the max discount for that category
        discount = round(random.uniform(0, category_info.max_discount), 2)
        return price, discount
    """
    def _calculate_pricing(self, category_info):
        # Price determination folows a Gauss distribution: 68% can be +-10%, 95% +-20%, and 1% can be higher/lower than +-30%
        deviation = category_info.avg_price * 0.10
        price = round(random.gauss(category_info.avg_price, deviation), 2)
        price = max(1.0, price)

      # Discount determination, on the other hand, is triangular 50% of the time no discount
        discount = round(random.triangular(0.0, category_info.max_discount, 0.0), 2)
        if random.random() < 0.50:
            discount = 0.0

        return price, discount

    
    def _generate_all_timestamps(self, n_logs):
        """Generates N timestamps in bussiness hours and sorts them """

        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        days_between = (end_date - start_date).days

        valid_timestamps = []
        
        while len(valid_timestamps) < n_logs:
            random_days = random.randint(0, days_between)
            candidate_date = start_date + timedelta(days=random_days)

            if candidate_date.weekday() < 5:
                final_timestamp = candidate_date.replace(
                    hour=random.randint(8, 17), 
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59),
                    microsecond=random.randint(0, 999999)
                )
                valid_timestamps.append(final_timestamp)
        
        valid_timestamps.sort()
        return valid_timestamps
            
    def _generate_dates(self):
        """Generates three dates: Timestamp, shipping and invoice"""
        order_timestamp = self.timestamp_list[self.current_log_index]
        
        if random.random() < 0.03: 
            shipping_delay = random.randint(6, 9)
        else:
            shipping_delay = random.randint(1, 5)

        shipping_date = order_timestamp + timedelta(days=shipping_delay)
        invoice_date = shipping_date + timedelta(days=random.randint(0, 1))

        return order_timestamp, shipping_date.date(), invoice_date.date()
     
    def _get_random_status(self):
        status_list = random.choices(config.ORDER_STATUS, weights=config.STATUS_WEIGHTS, k=1)
        return status_list[0]

    def _generate_single_log(self):
        
        order_status = self._get_random_status()
        category_name, category_info = self._get_random_category()
        price, discount = self._calculate_pricing(category_info)

        order_timestamp, shipping_date, invoice_date = self._generate_dates()

        if order_status == 'Pending':
            shipping_date = None
            invoice_date = None

        elif order_status == 'Cancelled':
            invoice_date = None
        
        log = {
            'transaction_id': self._generate_transaction_id(),
            'user_id': random.choice(config.USERS),
            'customer_id': self._get_random_customer(),
            'product_category': category_name,
            'total_amount': price,
            'discount_percent': discount,
            'timestamp_order': order_timestamp,
            'shipping_date': shipping_date,
            'invoice_date': invoice_date,
            'order_status': order_status,
            'is_fraud': 0
        }
        return log
    
    # ========= Public functions =========

    def generate_clean_logs(self, n_logs):
        self.timestamp_list = self._generate_all_timestamps(n_logs)
        
        self.current_log_index = 0
        
        log_list = []
        for _ in range(n_logs):
            log_list.append(self._generate_single_log())
            self.current_log_index += 1 

        return pd.DataFrame(log_list)



        
