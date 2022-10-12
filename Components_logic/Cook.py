from time import sleep
import time
from threading import Thread, Lock
import logging
from collections import deque

from config import *
from Components_logic.Cooking_apparatus import *

# initialize the logger mode
logging.basicConfig(level=logging.DEBUG)


class Cook:
    def __init__(self, cooks, cook_id, kitchen):
        self.cook = cooks  # define the cook
        self.cook_id = cook_id + 1  # give id to the cook
        self.rank = cooks['rank']  # define the rank of the cook
        self.proficiency = cooks['proficiency']  # define the proficiency of the cook
        self.name = cooks['name']  # define the name of the cook
        self.catch_phrase = cooks['catch-phrase']  # define the cath phrase of the cook
        self.kitchen = kitchen  # initiate the kitchen configuration
        self.lock = Lock()  # define inner mutex
        self.divided_cook_time = None  # define the time after dividing food_preparation
        self.prepared_food = []  # temporary list of food that was prepared
        self.is_available = available  # define the availability of the cook
        self.cooked_part = 0  # counter for the divisions that are already cooked
        self.cooking_apparatus = []  # the list of food cooked by cooking apparatus
        self.busy_partition = 0

    # distribute food preparation
    def cook_food(self, food):
        food.state = in_preparation
        food.food_lock.release()
        Thread(target=self.cook_food_part, args=(food,)).start()

    # find and prepare the found food item
    def prepare_food(self):
        while True:
            with self.kitchen.order_list_lock:
                if len(self.kitchen.food_list) == 0:
                    continue
                elif self.is_available == available and self.rank >= self.kitchen.food_list[0].complexity:
                    food = self.kitchen.food_list.pop(0)
                    self.lock.acquire()
                    self.busy_partition += 1
                    if self.busy_partition == self.proficiency:
                        self.is_available = busy
                    self.lock.release()
                    order = self.kitchen.order_dict[food.order_id]
                    food.food_lock.acquire()
                    if food.state == waiting_to_be_prepared:
                        self.get_preparation_method(food, order)
                        food.cook_id = self.cook_id
                        if food.state == in_preparation:
                            order.cooking_details.append({'food_id': food.food_id, 'cook_id': self.cook_id})
                            logging.info(f'Cook {self.cook_id} is cooking food {food.food_id} from order '
                                         f'{order.order_id}...')
                    else:
                        self.kitchen.food_list.append(food)
                        food.food_lock.release()
                        self.lock.acquire()
                        self.busy_partition -= 1
                        if self.busy_partition < self.proficiency:
                            self.is_available = available
                        self.lock.release()
            # i += 1
            i = 0
            while i < len(self.cooking_apparatus):
                # with self.lock:
                if self.cooking_apparatus[i].state == food_ready:
                    current_apparatus = self.cooking_apparatus[i]
                    self.cooking_apparatus.pop(i)
                    if current_apparatus.food.cooked_time >= current_apparatus.food.preparation_time:
                        current_apparatus.food.state = prepared
                    else:
                        current_apparatus.food.state = waiting_to_be_prepared
                        with self.kitchen.order_list_lock:
                            self.kitchen.food_list.append(current_apparatus.food)
                    current_apparatus.state = cooking_apparatus_available
                    i -= 1
                i += 1

    # performing the check of the method of food preparation: using oven, stove or none of them
    def get_preparation_method(self, food, order):
        # in case of oven
        if food.cooking_apparatus == 'oven':
            current_apparatus = self.kitchen.cooking_apparatus['oven']
            self.use_cooking_apparatus(current_apparatus, food)
        elif food.cooking_apparatus == 'stove':
            current_apparatus = self.kitchen.cooking_apparatus['stove']
            self.use_cooking_apparatus(current_apparatus, food)
        else:
            self.cook_food(food)
            # logging.info(f'Food {food.food_id} from order {order.order_id} has been prepared')

    # def find_cooking_apparatus(self, apparatus_type):
    #     # self.kitchen.order_list_lock.acquire()
    #     for apparatus in self.kitchen.cooking_apparatus[apparatus_type]:
    #         if apparatus.state == cooking_apparatus_available:
    #             return apparatus
    #     return None

    def use_cooking_apparatus(self, current_apparatus, food):
        current_apparatus.lock.acquire()
        if current_apparatus.state == cooking_apparatus_available:
            # current_apparatus.state = cooking_apparatus_busy
            food.state = in_preparation
            # self.kitchen.order_list_lock.release()
            current_apparatus.apparatus_cook_food(food)
            self.cooking_apparatus.append(current_apparatus)
        else:
            self.kitchen.food_list.append(food)
        current_apparatus.lock.release()
        food.food_lock.release()
        self.lock.acquire()
        self.busy_partition -= 1
        if self.busy_partition < self.proficiency:
            self.is_available = available
        self.lock.release()

    def cook_food_part(self, food):
        sleep(min(time_partition, food.preparation_time - food.cooked_time) * time_unit)
        # check number of finished threads and set food as prepared if done
        food.food_lock.acquire()
        food.cooked_time += time_partition
        if food.preparation_time <= food.cooked_time:
            food.state = prepared
            logging.info(f'Food {food.food_id} from order {food.order_id} has been prepared')
        else:
            food.state = waiting_to_be_prepared
            self.kitchen.food_list.append(food)
            print('Coook ', self.cook_id, self.is_available)
        sleep(0.5 * time_unit)
        self.lock.acquire()
            # self.cooked_part += 1
        self.busy_partition -= 1
        if self.busy_partition < self.proficiency:
            self.is_available = available
        self.lock.release()
        food.food_lock.release()
