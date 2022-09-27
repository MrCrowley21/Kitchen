from time import sleep

from config import *


class CookingApparatus:
    def __init__(self, apparatus_type, quantity):
        self.apparatus_type = apparatus_type
        self.quantity = quantity
        self.state = cooking_apparatus_available
        self.food_to_prepare = []

