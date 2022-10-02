import threading
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
    kitchen.receive_order(order)
    logging.info(f'Order {order["order_id"]} has been received from the dinning hall')
    return jsonify(order)


# start the program execution
if __name__ == "__main__":
    # initialize server as a thread
    threading.Thread(target=lambda: app.run(port=8080, host="0.0.0.0", debug=True, use_reloader=False)).start()
    # initialize kitchen
    kitchen = Kitchen()
    kitchen.prepare_order()
