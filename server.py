#!/usr/bin/env python3

from flask import Flask, request, jsonify
from guessRequester import getSlotGuess

app = Flask(__name__)

@app.route('/getClientGuess', methods=['GET'])
def getClientGuess():
    args = (request.args).to_dict()

    slot = args.get('slot')
    model_folder = args.get('model_folder')
    add_to_model= args.get('add_to_model') is not None
    node_url = args.get('node_url') or 'http://localhost:5052'

    if slot is None:
        return jsonify({'error': 'Invalid request, please provide slot'}), 500

    try:
        slot = int(slot)
    except ValueError:
        return jsonify({'error': 'Invalid request, slot must be an integer'}), 500

    print('add_to_model', add_to_model)
    print('node_url', node_url)

    res = getSlotGuess(slot, model_folder, node_url, add_to_model=add_to_model)
    if res is None:
        return jsonify({'error': 'Slot is empty or could not be downloaded'}), 500

    return jsonify(res), 200

if __name__ == "__main__":
    app.run()
