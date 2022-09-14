from config import *
from threading import Lock


# describe objects of type Food
class Food:
    def __init__(self, menu_description):
        self.food_id = menu_description['id']
        self.preparation_time = menu_description['preparation-time']
        self.complexity = menu_description['complexity']
        self.cooking_apparatus = menu_description['cooking-apparatus']
        self.state = waiting_to_be_prepared
        self.food_lock = Lock()
