from config import *
<<<<<<< HEAD
=======
import time
>>>>>>> 502325417bffb3264f30b88cee2d5b8d59090f33

from Components_logic.Menu import *
from Components_logic.Food import *


# describe objects of type Order
class Order:
<<<<<<< HEAD
    def __init__(self, order_id, items_nr, items_id, items, priority, max_wait, table_id):
        self.order_id = order_id
        self.items_nr = items_nr
=======
    def __init__(self, order_id, table_id, waiter_id, items_id, items, priority, max_wait, pick_up_time):
        self.order_id = order_id
        self.table_id = table_id
        self.waiter_id = waiter_id
>>>>>>> 502325417bffb3264f30b88cee2d5b8d59090f33
        self.items_id = items_id
        self.items = items
        self.priority = priority
        self.max_wait = max_wait
<<<<<<< HEAD
        self.table_id = table_id
=======
        self.pick_up_time = pick_up_time
        self.cooking_time = time.time()
        self.cooking_details = []
>>>>>>> 502325417bffb3264f30b88cee2d5b8d59090f33

    # check if the order is already prepared or not
    def get_state(self):
        for food in self.items:
            if food.state != prepared:
                return unprepared_order
        return prepared_order
