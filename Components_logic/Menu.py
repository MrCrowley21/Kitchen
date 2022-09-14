import json


# initialize food items from the menu
class Menu:
    def __init__(self):
        self.foods = dict()

    # get the list of food items from the menu
    def get_foods(self):
        with open('kitchen_data/menu.json') as json_file:
            menu_foods = json.load(json_file)
        for food in menu_foods:
            self.foods[food['id']] = food
        return self.foods
