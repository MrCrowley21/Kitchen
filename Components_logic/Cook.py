from time import sleep
import time
from threading import Thread, Lock
import logging

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
        self.cooked_part = 0   # counter for the divisions that are already cooked
        self.cooking_apparatus = []  # the list of food cooked by cooking apparatus

    # distribute food preparation
    def cook_food(self, food):
        food.state = in_preparation
        food.food_lock.release()
        self.is_available = busy
        # dividing food preparation in tasks to cook one food in parallel
        self.divided_cook_time = food.preparation_time * time_unit / self.proficiency
        # initiate thread for each task
        for i in range(self.proficiency):
            Thread(target=self.cook_by_parts, args=(self.divided_cook_time, food)).start()

    # find and prepare the found food item
    def prepare_food(self):
        while True:
            if len(self.kitchen.order_list) == 0:
                continue
            # searching for food to prepare by checking them
            order = self.kitchen.order_list[0]
            while order.get_state() != prepared_order:
                with self.kitchen.order_list_lock:
                    for food in order.items:
                        food.food_lock.acquire()
                        if food.state == waiting_to_be_prepared and self.rank >= food.complexity \
                                and self.is_available == available:
                            self.get_preparation_method(food, order)
                            if food.state != waiting_to_be_prepared:
                                order.cooking_details.append({'food_id': food.food_id, 'cook_id': self.cook_id})
                                food.cook_id = self.cook_id
                                logging.info(f'Cook {self.cook_id} is cooking food {food.food_id} from order '
                                             f'{order.order_id}...')
                        else:
                            food.food_lock.release()
                        i = 0
                        while i < len(self.cooking_apparatus):
                            with self.kitchen.lock:
                                if self.cooking_apparatus[i].state == food_ready:
                                    current_apparatus = self.cooking_apparatus[i]
                                    self.cooking_apparatus.pop(i)
                                    current_apparatus.food.state = prepared
                                    current_apparatus.state = cooking_apparatus_available
                                    i -= 1
                            i += 1

    # performing the check of the method of food preparation: using oven, stove or none of them
    def get_preparation_method(self, food, order):
        # in case of oven
        if food.cooking_apparatus == 'oven':
            current_apparatus = self.kitchen.cooking_apparatus['oven']
            with current_apparatus.lock:
                if current_apparatus.state == cooking_apparatus_available:
                    current_apparatus.state = cooking_apparatus_busy
                    food.state = in_preparation
                    current_apparatus.apparatus_cook_food(food)
                    self.cooking_apparatus.append(current_apparatus)
            food.food_lock.release()
        # in case of stove
        elif food.cooking_apparatus == 'stove':
            current_apparatus = self.kitchen.cooking_apparatus['stove']
            with current_apparatus.lock:
                if current_apparatus.state == cooking_apparatus_available:
                    current_apparatus.state = cooking_apparatus_busy
                    food.state = in_preparation
                    current_apparatus.apparatus_cook_food(food)
                    self.cooking_apparatus.append(current_apparatus)
            food.food_lock.release()
        else:
            self.cook_food(food)
            logging.info(f'Food {food.food_id} from order {order.order_id} has been prepared')

    # performing a subtask of food cooking
    def cook_by_parts(self, cook_time, food):
        sleep(cook_time)
        # check number of finished threads and set food as prepared if done
        with self.lock:
            self.cooked_part += 1
            if self.cooked_part == self.proficiency:
                food.state = prepared
                self.is_available = available
                self.cooked_part = 0
