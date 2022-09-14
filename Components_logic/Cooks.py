import json


# initiating the cooks in the kitchen
class Cooks:
    def __init__(self, nr_cooks):
        self.nr_cooks = nr_cooks
        self.cooks = []

    # get the list with the required amount of cooks
    def get_cooks(self):
        with open('kitchen_data/cooks.json') as json_file:
            all_cooks = json.load(json_file)
        self.cooks = all_cooks[0:self.nr_cooks]
        return self.cooks
