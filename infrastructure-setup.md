# Guide to setup and configure the Sigp Block-Print service

This file contains all the requirements, documentation and steps to setup a [`sipg-blockprint`](https://github.com/sigp/blockprint) 

## Requirements


## Documentation - Relevant Links


## Setup Guide

### Manual use of the model with the script

#### - Clone the repository

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
- `--add-to-model` : If this flag is set, the script will add the guess to the model data, only if the guess was made thanks to the graffity
- `--node-url` : The url of the node to use to fetch the data from the blockchain (default: `http://localhost:5052`)
- `model_folder` : The folder containing the model data. You can use the `blockprint/model` folder in the repository
- `slot` : The block slot to have a guess for

### Using the server

In the `server.py` file, you can find a simple server that will allow you to use the model to make guesses

You can either run it locally or deploy it on a server

Then you can use the `/getClientGuess` ([GET]) endpoint to make a guess for a given slot. Using the same parameters as described before

#### request example

```
http://localhost:5000/getClientGuess?slot=66666&model_folder=blockprint/model/&node_url=my_nodeUrl&add_to_model
```