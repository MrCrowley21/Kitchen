# ports
ports = {
    'port_1': 8080,
    'port_2': 8081,
    'port_3': 8082,
    'port_4': 8083
}

# urls
urls_for_dinning_hall = {
    'dinning_hall_url_1': 'http://127.0.0.1:8000/',
    'dinning_hall_container_url_1': 'http://dinning_hall_container_1:8000/',
    'dinning_hall_url_2': 'http://127.0.0.1:8001/',
    'dinning_hall_container_url_2': 'http://dinning_hall_container_2:8001/',
    'dinning_hall_url_3': 'http://127.0.0.1:8002/',
    'dinning_hall_container_url_3': 'http://dinning_hall_container_3:8002/',
    'dinning_hall_url_4': 'http://127.0.0.1:8003/',
    'dinning_hall_container_url_4': 'http://dinning_hall_container_4:8003/'
}

# define the states of food item
waiting_to_be_prepared = 0
in_preparation = 1
prepared = 2

# define states of order
unprepared_order = 0
prepared_order = 1

# define states of cook
available = 0
busy = 1

# define states of cooking_apparatus
cooking_apparatus_available = 0
food_ready = 1
cooking_apparatus_busy = 2

# define the number of cooking apparatus
oven_nr = 2
stove_nr = 1
total_cooking_apparatus = oven_nr + stove_nr

# define constants
time_unit = 0.5
nr_cooks = 4

# define time partition
time_partition = 10

# define configs according to the restaurants
restaurant_id = '2'
port = ports['port_' + restaurant_id]
dinning_hall_url = urls_for_dinning_hall['dinning_hall_url_' + restaurant_id]
dinning_hall_container_url = urls_for_dinning_hall['dinning_hall_container_url_' + restaurant_id]
# dinning_hall = dinning_hall_url
dinning_hall = dinning_hall_container_url
menu = 'kitchen_data/menu_' + restaurant_id + '.json'
# menu = 'kitchen_data/menu.json'
