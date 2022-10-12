import threading
import logging
from copy import copy

import requests

from Components_logic.Order import *
from Components_logic.Cooks import *
from Components_logic.Cook import *
from Components_logic.Menu import *
from Components_logic.Food import *
from Components_logic.Cooking_apparatus import *
from config import *

logging.basicConfig(level=logging.DEBUG)


class Kitchen:
    def __init__(self):
        self.menu = Menu().get_foods()  # set the list of food from menu
        self.order_list = []  # define the list with the orders
        self.order_dict = {}
        self.prepared_order_list = []  # define the temporary list with prepared orders
        self.lock = threading.Lock()  # define the inner locker
        cooks_list = Cooks(nr_cooks).get_cooks()
        self.cooks = [Cook(i, cooks_list.index(i), self) for i in cooks_list]  # get the list of cooks in the kitchen
        # define used cooking apparatus
        self.cooking_apparatus = {'oven': CookingApparatus('oven', oven_nr, self),
                                  'stove': CookingApparatus('stove', stove_nr, self)}
        # self.cooking_apparatus = {'oven': [CookingApparatus('oven', i, self) for i in range(oven_nr)],
        #                           'stove': [CookingApparatus('stove', i, self) for i in range(stove_nr)]}
        self.order_list_lock = Lock()
        self.food_list = []

    # set the order after its receiving
    def receive_order(self, order):
        # notify about adding the order in the list of orders needed to be prepared
        logging.info(f'Adding order {order["order_id"]} in the order list...')
        items = [Food(self.menu[i], order['order_id'], order['priority']) for i in order['items_id']]
        items.sort(key=lambda x: x.complexity)
        order = Order(order['order_id'], order['table_id'], order['waiter_id'], order['items_id'],
                      items, order['priority'], order['max_wait'], order['pick_up_time'])
        # append new order to the order list and sort it by the order od order generation
        # self.lock.acquire()
        with self.lock:
            self.order_list.append(order)
            self.order_list.sort(key=lambda x: (x.order_id / x.priority, x.order_id))
            self.order_dict[order.order_id] = order
            self.food_list += items
            # self.food_list.sort(key=lambda x: (x.order_id / x.priority, x.order_id))
        # self.lock.release()

    # set up threads for cooks
    def put_cooks_to_work(self):
        for cook in self.cooks:
            threading.Thread(target=cook.prepare_food).start()

    # set up the threads for cooking apparatus
    # def start_cooking_apparatus(self):
    #     for apparatus in self.cooking_apparatus:
    #         current_apparatus = self.cooking_apparatus[apparatus]
    #         threading.Thread(target=current_apparatus.apparatus_cook_food, args=()).start()

    # prepare orders and sending them to the dining hall
    def prepare_order(self):
        # set up the cooks
        self.put_cooks_to_work()
        # self.start_cooking_apparatus()
        while True:
            for order in self.order_list:
                # check for prepared orders and send them to the dinning hall
                if order.get_state() == prepared_order:
                    order.cooking_time = (time.time() - order.cooking_time) / time_unit
                    order_to_send = copy(order.__dict__)
                    order_to_send.pop('items', None)
                    requests.post(f'{dinning_hall_container_url}receive_prepared_order',
                                  json=order_to_send)
                    logging.info(f'Order {order.order_id} with order details:\n'
                                 f'{order_to_send} \n'
                                 f'has been prepared and sent to the dinning hall')
                    self.prepared_order_list.append(order)  # append prepared order to the list
                    break

            # excluding prepared orders from the list of orders
            while len(self.prepared_order_list) > 0:
                self.order_list.remove(self.prepared_order_list[0])
                self.prepared_order_list.pop(0)
