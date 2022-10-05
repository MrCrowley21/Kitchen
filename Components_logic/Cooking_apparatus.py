from time import sleep
from threading import Thread, Lock
import logging

from config import *

logging.basicConfig(level=logging.DEBUG)


class CookingApparatus:
    def __init__(self, apparatus_type, quantity, kitchen):
        self.kitchen = kitchen  # initiate kitchen
        self.apparatus_type = apparatus_type  # initiate the type of the used apparatus
        self.quantity = quantity  # quantity of the current of apparatus
        # self.apparatus_id = apparatus_id
        self.state = cooking_apparatus_available  # the availability of the apparatus
        self.cooked_part = 0  # counter for the divisions that are already cooked
        self.lock = Lock()  # the inner lock of the cooking apparatus object
        self.food = None  # the list of food items to be prepared
        self.busy_apparatus = 0

    # get the food to be prepared from the list of food items and initiate its preparation
    def apparatus_cook_food(self, food):
        self.food = food
        if self.food.state != prepared:
            logging.info(f'Cooking apparatus ({self.apparatus_type}) started working on food  {self.food.food_id}')
            self.state = cooking_apparatus_busy
            for i in range(self.quantity):
                Thread(target=self.cook_with_apparatus).start()

    # define cooking logic behind each thread
    def cook_with_apparatus(self):
        sleep(min(time_partition, self.food.preparation_time - self.food.cooked_time) * time_unit)
        print('sleeping')
        self.food.cooked_time += time_partition
        with self.lock:
            self.cooked_part += 1
            # self.busy_apparatus -= 1
            # self.state = food_ready
            if self.cooked_part == self.quantity:
                self.cooked_part = 0
                self.state = food_ready
                # self.notify_cook()
        logging.info(f'{self.food.food_id}, {self.food.cook_id}, {self.cooked_part}')
        logging.info(f'Cooking apparatus ({self.apparatus_type}) notified cook {self.food.cook_id}')
