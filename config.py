# Global Data
from dataclasses import dataclass

def create_users(user_amount):
    user_list = []

    for i in range(1, USER_AMOUNT + 1):
        user_name = "User_" + str(i)
        user_list.append(user_name)
        
    return user_list

@dataclass
class CategoryDescription:
    max_discount: int
    avg_price: float

LOG_NUMBER = 1000
USER_AMOUNT = 10
USERS = create_users(USER_AMOUNT)
CATEGORIES = {
    'Electronics': CategoryDescription(15, 600),
    'Clothing': CategoryDescription(40, 40),
    'Food': CategoryDescription(5, 10),
    'Furniture': CategoryDescription(20, 400),
    'Games': CategoryDescription(50, 40)
}
# Defines the number in which the sales order starts counting
START_TRANSACTION_ID = 1000000
CUSTOMER_AMOUNT = 100
# From 0 to 100 
NEW_CUSTOMER_CHANCE_PERCENTAGE = 5

ORDER_STATUS = ['Completed', 'Shipped', 'Pending', 'Cancelled', 'Returned']
STATUS_WEIGHTS = [0.85, 0.08, 0.03, 0.02, 0.02]

# Discount Manipulation
CORRUPT_EMPLOYEES_NUMBER = 2
CORRUPT_CUSTOMERS_NUMBER = 3
# Splitting
SPLIT_COUNT_RANGE = (2, 4)
# Channel Stuffing
CHANNEL_STUFFING_WINDOW_DAYS = 45
CS_STATUS_WEIGHTS = [0.8, 0.1, 0.1]


FRAUD_TYPE_MAP = {
    0: "False Alarm",
    1: "Ghost Sales",
    2: "Channel Stuffing",
    3: "Discount Manipulation",
    4: "Unusual Hours",
    5: "Splitting",
    6: "Premature Invoicing"
}
#Best performing contaminations
IFOREST_DEFAULT_CONTAMINATION = 0.0093 
LOF_DEFAULT_CONTAMINATION = 0.0048 
ENSEMBLE_DEFAULT_THRESHOLD = 99.5