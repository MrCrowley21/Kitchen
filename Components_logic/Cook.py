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
        self.busy_partition = 0  # the number of cook's threads that are busy
        self.available_apparatus = {'oven': oven_nr,
                                    'stove': stove_nr}  # the state of the apparatus

    # find and prepare the found food item
    def prepare_food(self):
        while True:
            self.kitchen.order_list_lock.acquire()
            if len(self.kitchen.food_list) == 0:
                self.kitchen.order_list_lock.release()
                continue
            elif self.is_available == available:
                self.kitchen.order_list_lock.release()
                self.lock.acquire()
                self.busy_partition += 1
                if self.busy_partition == self.proficiency:
                    self.is_available = busy
                self.lock.release()
                t = Thread(target=self.cook_food)
                t.start()
                t.join()
            elif self.is_available != available:
                self.kitchen.order_list_lock.release()
            else:
                self.kitchen.order_list_lock.release()

    def cook_food(self):
        food = self.find_food()
        self.kitchen.order_list_lock.acquire()
        self.kitchen.food_list.sort(key=lambda x: x.priority, reverse=True)
        self.kitchen.order_list_lock.release()
        if food is not None:
            order = self.kitchen.order_dict[food.order_id]
            self.get_preparation_method(food)
            food.cook_id = self.cook_id
            order.cooking_details.append({'food_id': food.food_id, 'cook_id': self.cook_id})
        self.lock.acquire()
        self.busy_partition -= 1
        if self.busy_partition < self.proficiency:
            self.is_available = available
        self.lock.release()

        i = 0
        while i < len(self.cooking_apparatus):
            self.cooking_apparatus[i].lock.acquire()
            if self.cooking_apparatus[i].state == food_ready:
                current_apparatus = self.cooking_apparatus[i]
                current_apparatus.lock.release()
                self.lock.acquire()
                self.cooking_apparatus.pop(i)
                self.lock.release()
                current_apparatus.food.food_lock.acquire()
                if current_apparatus.food.cooked_time >= current_apparatus.food.preparation_time:
                    current_apparatus.food.state = prepared
                    current_apparatus.food.food_lock.release()
                else:
                    current_apparatus.food.state = waiting_to_be_prepared
                    current_apparatus.food.food_lock.release()
                current_apparatus.lock.acquire()
                current_apparatus.state = cooking_apparatus_available
                current_apparatus.lock.release()
                self.lock.acquire()
                self.available_apparatus[current_apparatus.food.cooking_apparatus] += 1
                self.lock.release()
                logging.info(f'{self.cook_id} {self.is_available}')
                i -= 1
            else:
                self.cooking_apparatus[i].lock.release()
            i += 1

    def find_food(self):
        i = 0
        self.kitchen.order_list_lock.acquire()
        while i < len(self.kitchen.food_list):
            food = self.kitchen.food_list[i]
            food.food_lock.acquire()
            if food.cooked_time < food.preparation_time and food.complexity <= self.proficiency and \
                    food.state == waiting_to_be_prepared and \
                    (food.cooking_apparatus is None or self.available_apparatus[food.cooking_apparatus] > 0):
                food.state = in_preparation
                food.food_lock.release()
                self.kitchen.order_list_lock.release()
                return food
            elif food.state == prepared:
                food.food_lock.release()
                try:
                    self.kitchen.food_list.remove(food)
                except:
                    pass
            else:
                food.food_lock.release()
                i += 1
        self.kitchen.order_list_lock.release()
        return None

    # performing the check of the method of food preparation: using oven, stove or none of them
    def get_preparation_method(self, food):
        # in case of oven
        if food.cooking_apparatus == 'oven':
            current_apparatus = self.find_cooking_apparatus('oven')
            if current_apparatus is not None:
                self.use_cooking_apparatus(current_apparatus, food)
                self.lock.acquire()
                self.available_apparatus['oven'] -= 1
                self.lock.release()
            else:
                food.food_lock.acquire()
                food.state = waiting_to_be_prepared
                food.food_lock.release()
                self.lock.acquire()
                self.busy_partition -= 1
                if self.busy_partition < self.proficiency:
                    self.is_available = available
                self.lock.release()
        # in case of stove
        elif food.cooking_apparatus == 'stove':
            current_apparatus = self.find_cooking_apparatus('stove')
            if current_apparatus is not None:
                self.use_cooking_apparatus(current_apparatus, food)
                self.lock.acquire()
                self.available_apparatus['stove'] -= 1
                self.lock.release()
            else:
                food.food_lock.acquire()
                food.state = waiting_to_be_prepared
                food.food_lock.release()
                self.lock.acquire()
                self.busy_partition -= 1
                if self.busy_partition < self.proficiency:
                    self.is_available = available
                self.lock.release()
        else:
            self.cook_food_part(food)

    def find_cooking_apparatus(self, apparatus_type):
        for apparatus in self.kitchen.cooking_apparatus[apparatus_type]:
            apparatus.lock.acquire()
            if apparatus.state == cooking_apparatus_available:
                apparatus.state = cooking_apparatus_busy
                apparatus.lock.release()
                return apparatus
            else:
                apparatus.lock.release()
        return None

    def use_cooking_apparatus(self, current_apparatus, food):
        Thread(target=current_apparatus.apparatus_cook_food, args=(food,)).start()
        self.lock.acquire()
        self.cooking_apparatus.append(current_apparatus)
        self.busy_partition -= 1
        if self.busy_partition < self.proficiency:
            self.is_available = available
        self.lock.release()

    def cook_food_part(self, food):
        food.food_lock.acquire()
        food.cooked_time += time_partition
        food.food_lock.release()
        sleep(min(time_partition, abs(food.preparation_time - food.cooked_time)) * time_unit)
        food.food_lock.acquire()
        if food.preparation_time <= food.cooked_time:
            food.state = prepared
            food.food_lock.release()
            logging.info(f'Food {food.food_id} from order {food.order_id} has been prepared')
        else:
            food.state = waiting_to_be_prepared
            food.food_lock.release()
            print('Coook ', self.cook_id, self.is_available)
        self.lock.acquire()
        self.busy_partition -= 1
        if self.busy_partition < self.proficiency:
            self.is_available = available
        self.lock.release()
        self.check_cooking_apparatus()

    def check_cooking_apparatus(self):
        i = 0
        while i < len(self.cooking_apparatus):
            self.cooking_apparatus[i].lock.acquire()
            if self.cooking_apparatus[i].state == food_ready:
                current_apparatus = self.cooking_apparatus[i]
                current_apparatus.lock.release()
                self.lock.acquire()
                self.cooking_apparatus.pop(i)
                self.lock.release()
                current_apparatus.food.food_lock.acquire()
                if current_apparatus.food.cooked_time >= current_apparatus.food.preparation_time:
                    current_apparatus.food.state = prepared
                    current_apparatus.food.food_lock.release()
                else:
                    current_apparatus.food.state = waiting_to_be_prepared
                    current_apparatus.food.food_lock.release()
                current_apparatus.lock.acquire()
                current_apparatus.state = cooking_apparatus_available
                current_apparatus.lock.release()
                self.lock.acquire()
                self.available_apparatus[current_apparatus.food.cooking_apparatus] += 1
                self.lock.release()
                logging.info(f'{self.cook_id} {self.is_available}')
                i -= 1
            else:
                self.cooking_apparatus[i].lock.release()
            i += 1