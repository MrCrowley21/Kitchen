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
        self.cooks_proficiency = sum([i.proficiency for i in self.cooks])
        # define used cooking apparatus
        self.cooking_apparatus = {'oven': [CookingApparatus('oven', i, self) for i in range(oven_nr)],
                                  'stove': [CookingApparatus('stove', i, self) for i in range(stove_nr)]}
        self.apparatus_lock = Lock()
        self.order_list_lock = Lock()
        self.client_service_order = {}
        self.food_list = []

    # set the order after its receiving
    def receive_order(self, order):
        try:
            # notify about adding the order in the list of orders needed to be prepared
            logging.info(f'Adding order {order["order_id"]} in the order list...')
            items = [Food(self.menu[i], order['order_id'], order['priority']) for i in order['items_id']]
            items.sort(key=lambda x: x.complexity)
            order = Order(order['order_id'], order['table_id'], order['waiter_id'], order['items_id'],
                          items, order['priority'], order['max_wait'], order['pick_up_time'])
        except:
            logging.info(f'{order}')
            # notify about adding the order in the list of orders needed to be prepared
            logging.info(f'Adding order of client {order["client_id"]} in the order list...')
            items = [Food(self.menu[i], order['order_id'], order['priority']) for i in order['items']]
            items.sort(key=lambda x: x.complexity)
            order = Order(order['order_id'], None, None, order['items'],
                          items, order['priority'], order['max_wait'], order['created_time'])
            self.order_list_lock.acquire()
            self.client_service_order[order.order_id] = order
            self.order_list_lock.release()
        self.order_list_lock.acquire()
        self.order_list.append(order)
        self.order_dict[order.order_id] = order
        self.food_list += items
        self.order_list_lock.release()

    def compute_estimated_time(self, order):
        try:
            items = [self.menu[i] for i in order['items']]
        except:
            items = [self.menu[i] for i in order.items_id]
        cooking_with_app, cooking_without_app = self.__compute_food_count(items)
        estimated_waiting_time = (cooking_without_app / self.cooks_proficiency +
                                  cooking_with_app / total_cooking_apparatus) * \
                                 (len(self.food_list) + len(items)) / len(items)
        return estimated_waiting_time

    def __compute_food_count(self, items):
        with_cooking_apparatus = 0
        without_cooking_apparatus = 0
        for item in items:
            if item['cooking-apparatus'] is None:
                without_cooking_apparatus += item['preparation-time']
            else:
                with_cooking_apparatus += item['preparation-time']
        return with_cooking_apparatus, without_cooking_apparatus

    # set up threads for cooks
    def put_cooks_to_work(self):
        for cook in self.cooks:
            threading.Thread(target=cook.prepare_food).start()

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
                    requests.post(f'{dinning_hall_url}receive_prepared_order',
                                  json=order_to_send)
                    logging.info(f'Order {order.order_id} with order details:\n'
                                 f'{order_to_send} \n'
                                 f'has been prepared and sent to the dinning hall')
                    self.prepared_order_list.append(order)  # append prepared order to the list
                    break

            # excluding prepared orders from the list of orders
            while len(self.prepared_order_list) > 0:
                self.order_list_lock.acquire()
                self.order_list.remove(self.prepared_order_list[0])
                self.order_list_lock.release()
                self.prepared_order_list.pop(0)
