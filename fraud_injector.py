import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random, config
class FraudInjector:

    def __init__(self, base_data):
        self.base_data = base_data.copy()
        self.fake = Faker('es_ES') 
    
    """ Alternative constructor: Instead of df (Memory), instantiates from .csv file"""
    @classmethod
    def from_csv(cls, file_path):
        df = pd.read_csv(file_path, sep=";")
        
        #Handling of datetime variables, to avoid any regarding them
        df['timestamp_order'] = pd.to_datetime(df['timestamp_order'], errors='coerce')
        df['timestamp_order'] = df['timestamp_order'].apply(
            lambda x: x.to_pydatetime() if pd.notnull(x) else None
        )
        
        for col in ['shipping_date', 'invoice_date']:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
            df[col] = df[col].apply(lambda x: None if pd.isna(x) else x)
            
        return cls(df)
    
    #HELPER FUNCTIONS================
    
    def _get_random_indices(self, clean_index_logs, num_items):
        """ Selects random indices and removes them from the list clean_index_logs so they don't get overwritten"""
        picked_indices = random.sample(clean_index_logs, num_items)
        for index in picked_indices:
            clean_index_logs.remove(index)
        return picked_indices
    
    def _calculate_dates(self, index, new_date):
            new_shipping = new_date + timedelta(days=random.randint(1, 5))
            self.base_data.at[index, 'shipping_date'] = new_shipping.date()
            self.base_data.at[index, 'invoice_date'] = (new_shipping + timedelta(days=random.randint(0, 1))).date()
        
    def _remove_indices_from_list(self, clean_index_logs, block):
        """ Removes indices from clean_index_logs list """
        for i in range(len(block)):
            clean_index_logs.remove(block[i])

    def _find_consecutive_block(self, clean_index_logs, num_needed):
        """ Tries to find empty slots for burst injections (splitting, ghost sales) """
        tries = 0
        #Max tries so system does not get stuck
        max_tries = 100
        found_block = None
        
        if len(clean_index_logs) < num_needed: 
            return None

        while tries < max_tries and found_block is None:

            start_pos = random.randint(0, len(clean_index_logs) - num_needed)

            candidate = clean_index_logs[start_pos : start_pos + num_needed]

            if candidate[num_needed - 1] - candidate[0] == num_needed - 1:
                found_block = candidate
            tries += 1
        return found_block
    
    #PRIVATE FUNCTIONS================

    def _ghost_sales(self, clean_index_logs, num_ghost):
        """
        Ghost Sales: Burst of consecutive purchases from a new company to inflate volume.
        This function modifies a random amount of transactions (from 8 to 14) and assigns them to a random costumer in a short span of time. 
        """
        injected_count = 0
        
        while injected_count < num_ghost:
            burst_size = random.randint(8, 14)
            
            if injected_count + burst_size > num_ghost:
                burst_size = num_ghost - injected_count
                
            ghost_customer = self.fake.company()
            consecutive_block = self._find_consecutive_block(clean_index_logs, burst_size)
            
            if consecutive_block is not None:
                self._remove_indices_from_list(clean_index_logs, consecutive_block)
                base_time = self.base_data.at[consecutive_block[0], 'timestamp_order']
                corrupt_user = self.base_data.at[consecutive_block[0], 'user_id']
                
                for i in range(len(consecutive_block)):
                    index = consecutive_block[i]
                    time_offset = i * random.randint(2000, 10000)
                    new_date = base_time + timedelta(milliseconds=time_offset)
                    
                    self.base_data.at[index, 'customer_id'] = ghost_customer
                    
                    self.base_data.at[index, 'user_id'] = corrupt_user 
                    
                    self.base_data.at[index, 'timestamp_order'] = new_date
                    self.base_data.at[index, 'is_fraud'] = 1
                    
                    self._calculate_dates(index, new_date)

                injected_count += burst_size
            else:
                break
                
        return clean_index_logs
    
    def _channel_stuffing(self, clean_index_logs, num_chstuff):
        """
        Channel stuffing: Defined as the practice as issuing fake sales orders before the ending of a quarter. 
        The function simulates not asked for orders at the end of Q4. So customers return it.
        """
        
        picked_indices = self._get_random_indices(clean_index_logs, num_chstuff)
            
        for index in picked_indices:

            old_date = self.base_data.at[index, 'timestamp_order']

            end_of_year = old_date.replace(month=12, day=31)
            # The injection starts 45 days before the end of the year
            new_date = end_of_year - timedelta(days=random.randint(0, config.CHANNEL_STUFFING_WINDOW_DAYS))
            self.base_data.at[index, 'timestamp_order'] = new_date
            
            # We multiply the prices slightly to show a moderate increase in sales
            current_price = self.base_data.at[index, 'total_amount']
            self.base_data.at[index, 'total_amount'] = round(current_price * random.uniform(1.5, 3.5), 2)
            
            # Sometimes the sales go through
            cs_order_status = ['Returned', 'Completed', 'Cancelled']
            cs_order_weights = config.CS_STATUS_WEIGHTS
            
            cs_state = random.choices(cs_order_status, weights=cs_order_weights)[0]
            self.base_data.at[index, 'order_status'] = cs_state
            
            self.base_data.at[index, 'is_fraud'] = 2

            self._calculate_dates(index, new_date)

        return clean_index_logs
    
    def _discount_manipulation(self, clean_index_logs, num_discounts):    
        """
        Discount manipulation: The practice of a worker applying a non-authorised discount (higher than normal).
        The function simulates a group of corrupt employees favoring a group of customers.
        """

        picked_indices = self._get_random_indices(clean_index_logs, num_discounts)
        
        # We select a random set of customers and employees
        all_users = self.base_data['user_id'].unique().tolist()
        all_customers = self.base_data['customer_id'].unique().tolist()

        corrupt_employees_number = config.CORRUPT_EMPLOYEES_NUMBER
        corrupt_customers_number = config.CORRUPT_CUSTOMERS_NUMBER

        corrupt_employees = random.sample(all_users, corrupt_employees_number)
        corrupt_customers = random.sample(all_customers, corrupt_customers_number)
        
        for index in picked_indices:

            self.base_data.at[index, 'user_id'] = random.choice(corrupt_employees)
            self.base_data.at[index, 'customer_id'] = random.choice(corrupt_customers)

            current_category = self.base_data.at[index, 'product_category']
            max_allowed = config.CATEGORIES[current_category].max_discount
            fraudulent_discount = round(max_allowed * random.uniform(1.1, 1.5), 2)
            
            self.base_data.at[index, 'discount_percent'] = fraudulent_discount
            self.base_data.at[index, 'is_fraud'] = 3
            
        return clean_index_logs
    
    def _unusual_hours(self, clean_index_logs, num_unusual):
        """
        Unusual Hours: Making changes in the system outside of business hours.
        """

        picked_indices = self._get_random_indices(clean_index_logs, num_unusual)
            
        for index in picked_indices:
            old_date = self.base_data.at[index, 'timestamp_order']
            
            # 19 to 31 translates to 19:00 to 7:00
            new_hour = random.randint(19, 31) % 24
            
            new_date = old_date.replace(hour=new_hour, minute=random.randint(0, 59))
            
            self.base_data.at[index, 'timestamp_order'] = new_date
            self.base_data.at[index, 'is_fraud'] = 4
            

            self._calculate_dates(index, new_date)
            
        return clean_index_logs
    
    def _splitting(self, clean_index_logs, num_split_events):
        """
        Splitting: Defined as splitting a big sales order into two or more to avoid static control.
        Selects an amount to split a sales order and works with consecutive logs to simulate time proximity and avoid approval limits.
        """
        all_customers = self.base_data['customer_id'].unique().tolist()
        all_users = self.base_data['user_id'].unique().tolist()
        all_categories = self.base_data['product_category'].unique().tolist()
        # --------------------------

        for tries in range(num_split_events):

            num_splits = random.randint(config.SPLIT_COUNT_RANGE[0], config.SPLIT_COUNT_RANGE[1])
            consecutive_block = self._find_consecutive_block(clean_index_logs, num_splits)
            
            if consecutive_block is not None:

                self._remove_indices_from_list(clean_index_logs, consecutive_block)
                
                target_customer = random.choice(all_customers)
                target_user = random.choice(all_users)
                target_category = random.choice(all_categories)
                
                # Once we have the space to inject the transactions, we make up an "approval limit" and we split the sales 
                avg_price = config.CATEGORIES[target_category].avg_price
                approval_limit = avg_price * random.uniform(3.0, 5.0)
                total_value = approval_limit * random.uniform(1.1, 1.5)
                split_amount = round(total_value / num_splits, 2)
                
                base_time = self.base_data.at[consecutive_block[0], 'timestamp_order']
                accumulated_seconds = 0
                
                for i in range(len(consecutive_block)):
                    index = consecutive_block[i]
                    
                    self.base_data.at[index, 'customer_id'] = target_customer
                    self.base_data.at[index, 'user_id'] = target_user
                    self.base_data.at[index, 'product_category'] = target_category
                    self.base_data.at[index, 'total_amount'] = split_amount
                    self.base_data.at[index, 'discount_percent'] = 0.0
                    
                    # The next sales orders will be made in a short period of time
                    if i > 0:
                        accumulated_seconds += random.randint(40, 150)
                    
                    new_date = base_time + timedelta(seconds=accumulated_seconds)
                    self.base_data.at[index, 'timestamp_order'] = new_date
                    self.base_data.at[index, 'is_fraud'] = 5
                    
                    self._calculate_dates(index, new_date)

        return clean_index_logs
    
    def _premature_invoicing(self, clean_index_logs, num_premature):
        """
            Premature invoicing: The act of invoicing a sale before the customer fisically receives the goods. IRL can be a legal practice, if a previous agreement exists.
            In this function a delay is simulated, as if no material existed in stock in the first place.
            
        """
        picked_indices = self._get_random_indices(clean_index_logs, num_premature)
            
        for index in picked_indices:
            order_date = self.base_data.at[index, 'timestamp_order']

            invoice_gap = random.randint(0, 1)
            fake_invoice_date = (order_date + timedelta(days=invoice_gap)).date()
            
            chance = random.random()
            if chance < 0.30:
                shipping_delay = random.randint(6, 10)
            else:
                shipping_delay = random.randint(11, 40)
                
            fake_shipping_date = fake_invoice_date + timedelta(days=shipping_delay)

            self.base_data.at[index, 'invoice_date'] = fake_invoice_date
            self.base_data.at[index, 'shipping_date'] = fake_shipping_date
            self.base_data.at[index, 'is_fraud'] = 6
            
        return clean_index_logs
    
    #PUBLIC FUNCTIONS================

    def inject_all_frauds(self, num_ghost=150, num_chstuff=400, num_discounts=500, num_unusualh=600, num_splitting=200, num_prematureinv=500):

        clean_logs = self.base_data[self.base_data['is_fraud'] == 0]
        clean_index_logs = clean_logs.index.tolist() 

        clean_index_logs = self._ghost_sales(clean_index_logs, num_ghost)
        clean_index_logs = self._channel_stuffing(clean_index_logs, num_chstuff)
        clean_index_logs = self._discount_manipulation(clean_index_logs, num_discounts)
        clean_index_logs = self._unusual_hours(clean_index_logs, num_unusualh)
        clean_index_logs = self._splitting(clean_index_logs, num_splitting)
        clean_index_logs = self._premature_invoicing(clean_index_logs, num_prematureinv)

        self.base_data = self.base_data.sort_values(by='timestamp_order').reset_index(drop=True)

        return self.base_data
    



        
