import threading
from copy import deepcopy
from flask import Flask, request, jsonify

from Components_logic.Kitchen import *

# initialize the logger mode
logging.basicConfig(level=logging.DEBUG)

# initialize the server (app)
app = Flask(__name__)


# define server function to receive order requests from the dining hall
@app.route('/receive_order', methods=['POST'])
def receive_order():
    order = request.json
    Thread(target=kitchen.receive_order, args=(order,)).start()
    logging.info(f'New order has been received from the dinning hall')
    order_response = deepcopy(order)
    if 'client_id' in order_response:
        order_response['estimated_waiting_time'] = kitchen.compute_estimated_time(order)
    return jsonify(order_response)


@app.route('/check_preparation/<int:order_id>', methods=['GET'])
def get_preparation_time(order_id):
    order = kitchen.client_service_order[order_id]
    estimated_time = kitchen.compute_estimated_time(order)
    return {'estimated_time': estimated_time}


# start the program execution
if __name__ == "__main__":
    # initialize server as a thread
    threading.Thread(target=lambda: app.run(port=port, host="0.0.0.0", debug=True, use_reloader=False)).start()
    # initialize kitchen
    kitchen = Kitchen()
    kitchen.prepare_order()
