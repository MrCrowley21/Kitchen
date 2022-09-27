from time import sleep
import time
from threading import Thread, Lock
import logging

from config import *
from Components_logic.Cooking_aparatus import *

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
        self.is_available = available
        self.cooked_part = 0

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
            # for order in self.kitchen.order_list:
            while order.get_state() != prepared_order:
                with self.kitchen.order_list_lock:
                    for food in order.items:
                        food.food_lock.acquire()
                        # self.lock.acquire()
                        # check food state and its complexity
                        if food.state == waiting_to_be_prepared and self.rank >= food.complexity \
                                and self.is_available == available:
                            order.cooking_details.append({'food_id': food.food_id, 'cook_id': self.cook_id})
                            logging.info(f'Starting prepare food {food.food_id} from order {order.order_id}...')
                            self.cook_food(food)
                            logging.info(f'Food {food.food_id} from order {order.order_id} has been prepared')
                        else:
                            food.food_lock.release()

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
