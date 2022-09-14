from config import *

from Components_logic.Menu import *
from Components_logic.Food import *


# describe objects of type Order
class Order:
    def __init__(self, order_id, items_nr, items_id, items, priority, max_wait, table_id):
        self.order_id = order_id
        self.items_nr = items_nr
        self.items_id = items_id
        self.items = items
        self.priority = priority
        self.max_wait = max_wait
        self.table_id = table_id

    # check if the order is already prepared or not
    def get_state(self):
        for food in self.items:
            if food.state != prepared:
                return unprepared_order
        return prepared_order
