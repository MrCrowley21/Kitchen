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
        self.state = cooking_apparatus_available  # the availability of the apparatus
        self.cooked_part = 0  # counter for the divisions that are already cooked
        self.lock = Lock()  # the inner lock of the cooking apparatus object
        self.food_to_prepare = []  # the list of food items to be prepared

    # get the food to be prepared from the list of food items and initiate its preparation
    def select_food(self):
        while True:
            for food in self.food_to_prepare:
                food.food_lock.acquire()
                if self.state == cooking_apparatus_available and food.state != prepared:
                    logging.info(f'Cooking apparatus ({self.apparatus_type}) started working on food  {food.food_id}')
                    self.state = cooking_apparatus_busy
                    preparation_time = (food.preparation_time * time_unit) / self.quantity
                    self.food_to_prepare.remove(food)
                    for i in range(self.quantity):
                        Thread(target=self.cook_with_apparatus, args=(preparation_time, food)).start()
                else:
                    food.food_lock.release()

    # define cooking logic behind each thread
    def cook_with_apparatus(self, preparation_time, food):
        sleep(preparation_time)
        with self.lock:
            self.cooked_part += 1
            logging.info(f'{food.food_id}, {food.cook_id}, {self.cooked_part}')
            if self.cooked_part == self.quantity:
                self.cooked_part = 0
                self.notify_cook(food)
                food.food_lock.release()
                self.state = cooking_apparatus_available

    # notify the responsible cook about food's preparation
    def notify_cook(self, food):
        with self.kitchen.lock:
            cook = self.kitchen.cooks[food.cook_id - 1]
            cook.apparatus_cooked.append(food)
            logging.info(f'Cooking apparatus ({self.apparatus_type}) notified cook {food.cook_id}')
