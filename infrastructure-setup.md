# Guide to setup and configure the Sigp Block-Print service

This file contains all the requirements, documentation and steps to setup a [`sipg-blockprint`](https://github.com/sigp/blockprint) 

## Requirements

### Prepare the model

To do so:
- Clone this repository using the following command (so the submodules are also cloned)
```bash
git clone --recurse-submodules git@github.com:migalabs/block-printer.git
```

- Have a `lighthouse` node running and synced
- Use `prepare_training_data.py` to prepare the data for the model
```bash
./prepare_training_data.py [--node-url NODE_URL] start_slot end_slot training_data_folder model_folder
```
You can run `./prepare_training_data.py -h` for more information and options

`training_data_folder` being the folder where the blocks rewards, downloaded thanks to Lighthouse, will be stored

`model_folder` is the folder where the model data will be stored

___


## Documentation - Relevant Links


## Setup Guide

### Manual use of the model with the script

#### - Install the dependencies
    
```bash
pip install -r requirements.txt
```

#### - Have an access to a Lighthouse node
It will be used to fetch the data from the blockchain
By default, the script will try to connect to a local node running on `http://localhost:5052` but you can change it by using the `--node-url` flag followed by the url of the node when running the script

#### - Run the script

```bash
python3 guessRequester.py [-h] [--add-to-model] [--node-url NODE_URL] model_folder slot
```
- `--add-to-model` : If this flag is set, if the guess was made thanks to the graffity, the script will add the guess to the model data
- `--node-url` : The url of the node to use to fetch the data from the blockchain (default: `http://localhost:5052`)
- `model_folder` : The folder containing the model data
- `slot` : The block slot to have a guess for

### Using the server

In the `server.py` file, you can find a simple server that will allow you to use the model to make guesses

Here is the usage to run it:
```bash
usage: server.py [-h] [--add-to-model] [--node-url NODE_URL] model_folder
```

The model will be loaded only once at the start of the server

If the `--add-to-model` flag is set, the guesses made thanks to the graffity will be added to the model data

Then you can use the `/getClientGuess` ([GET]) endpoint to make a guess for a given slot passed as parameter

#### request example

Running it locally
```
http://127.0.0.1:5000/getClientGuess?slot=69420
```

___

Additionaly you can use the `build_db.py` script to build a sqlite database containing the guesses made by the model

```bash
usage: build_db.py [-h] --db-path DB_PATH --data-dir DATA_DIR --classify-dir CLASSIFY_DIR [--multi-classifier] [--force-rebuild]
```

`DATA_DIR` is the folder containing the model data

`CLASSIFY_DIR` is the folder containing the blocks rewards, downloaded thanks to Lighthouse (the _training_data_folder_)
