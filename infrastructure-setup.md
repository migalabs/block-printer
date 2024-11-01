# Guide to setup and configure the Sigp Block-Print service

This file contains all the requirements, documentation and steps to setup [`sipg-blockprint`](https://github.com/sigp/blockprint)

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

---

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

#### - Run the guess requester script

```bash
python3 guessRequester.py [-h] [--add-to-model] [--node-url NODE_URL] model_folder start_slot [end_slot]
```

- `--add-to-model` : If this flag is set, if the guess was made thanks to the graffity, the script will add the guess to the model data
- `--node-url` : The url of the node to use to fetch the data from the blockchain (default: `http://localhost:5052`)
- `model_folder` : The folder containing the model data
- `start_slot` : The start block slot to have a guess for
- `end_slot` : The end block slot to have a guess for (default: `start_slot`)

### Using the server

In the `server.py` file, you can find a simple server that will allow you to use the model to make guesses

Here is the usage to run it:

```bash
usage: server.py [-h] [--add-to-model] [--node-url NODE_URL] model_folder
```

The model will be loaded only once at the start of the server

If the `--add-to-model` flag is set, the guesses made thanks to the graffity will be added to the model data

Then you can use the `/getClientGuess` ([GET]) endpoint to make guesses for given slots passed as parameter. The slots are passed in a range format using the parameters `start_slot` and `end_slot`.

#### request examples

Running it locally

If the `end_slot` parameter is not set, the guess will be made only for the `start_slot`.

```
http://127.0.0.1:5000/getClientGuess?start_slot=69420
```

```
http://localhost:5000/getClientGuess?start_slot=69420&end_slot=69430
```

The response will be a JSON object containing the following fields:

```
{
    "best_guess_multi": "Teku",
    "best_guess_single": "Teku",
    "probability_map": {
        "Lighthouse": 0.0,
        "Nimbus": 0.0,
        "Prysm": 0.0,
        "Teku": 1.0
    },
    "proposer_index": 11516,
    "slot": 2
}
```

### Build the database

#### Clickhouse database

The script `load_db.py` will allow you to load the model data into a clickhouse database. The `clickhouse_endpoint` introduced should be an http endpoint to the clickhouse database. Example: `http://USER:PASSWORD@localhost:8123/DB_NAME`.

```bash
usage: load_db.py [-h] [--model-folder MODEL_FOLDER] [--add-to-model] [--node-url NODE_URL] [--reindex] clickhouse_endpoint
```

- `--model-folder` MODEL_FOLDER Path to the folder with model files. It will be used to train the classifier if there isn't one persisted already. Default: model

- `--add-to-model` Add the block to the model if client could be identified with graffiti

- `--node-url` NODE_URL URL of the beacon node to download blocks from (default: http://localhost:5052)

- `--reindex` Reindex the database. WARNING: This will delete all data in the database and reindex all slots from the beacon node. Useful if the model was updated
- `--persist-classifier` PERSIST_CLASSIFIER Persist the classifier to disk after training. It will be stored in the persisted_classifier folder with the name given as parameter. This name will also be used to load the classifier if it exists. The name should end with .pkl. Example: `--persist-classifier my_classifier.pkl`. This will allow to load the classifier from disk instead of retraining it every time the script is run, saving a lot of time on the cost of storing just a few KBs of data.

The script starts a backfilling process that will load all the guesses up to the current slot. It will then start a process that will listen to new blocks and add them to the database.

#### Sqlite database, from blockprint original repository

Additionaly you can use the `build_db.py` script to build a sqlite database containing the guesses made by the model

```bash
usage: build_db.py [-h] --db-path DB_PATH --data-dir DATA_DIR --classify-dir CLASSIFY_DIR [--multi-classifier] [--force-rebuild]
```

`DATA_DIR` is the folder containing the model data

`CLASSIFY_DIR` is the folder containing the blocks rewards, downloaded thanks to Lighthouse (the _training_data_folder_)

### Docker Images

There are two docker-compose services defined in the `docker-compose.yml` file. You can build them using the following command:

```bash
docker-compose build
```

The parameters for the services are defined in the `.env` file. These parameters are:

- `CLICKHOUSE_ENDPOINT`: The endpoint of the clickhouse database. It will be used by the `block-printer-load-db` service to load the model data into the database. Example: `http://USER:PASSWORD@localhost:8123/DB_NAME`

- `MODEL_PATH`: The folder containing the model data. It will be used by both services to make the guesses. Example: `model`

- `NODE_URL`: The url of the node to use to fetch the data from the blockchain. It will be used by both services to fetch the data from the blockchain. Example: `http://localhost:5052`

#### block-printer-server

This service will run the `server.py` script in a docker container. It will be accessible on port `5000` of the host machine.

To run it, you can use the following command:

```bash
docker-compose up block-printer-server
```

#### block-printer-load-db

This service will run the `load_db.py` script in a docker container.

To run it, you can use the following command:

```bash
docker-compose up -d block-printer-load-db
```
