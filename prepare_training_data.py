#!/usr/bin/env python3

import argparse
import functools
import multiprocessing
import os
import concurrent.futures

import blockprint.load_blocks as lb
import blockprint.prepare_training_data as ptd

def parseArgs():
    parser = argparse.ArgumentParser(description="Load blocks and prepare training data")
    parser.add_argument("start_slot", type=int, help="Slot to start loading blocks from")
    parser.add_argument("end_slot", type=int, help="Slot to end loading blocks at")
    parser.add_argument("training_data_folder", type=str, help="Path to the folder to use for the training data")
    parser.add_argument("model_folder", type=str, help="Path to the folder to use for the model")
    parser.add_argument("--node-url", type=str, default="http://localhost:5052", help="URL of the beacon node to download blocks from (default: http://localhost:5052)")
    parser.add_argument(
        "--disable",
        default=[],
        nargs="+",
        help="clients to ignore when forming training data",
    )
    parser.add_argument(
        "--num-workers",
        default=multiprocessing.cpu_count(),
        type=int,
        help="number of parallel processes to utilize",
    )
    return parser.parse_args()

def load_blocks(args):
    lb.download_block_reward_batches(args.start_slot, args.end_slot, args.training_data_folder, args.node_url)

def prepare_training_data(args):
    raw_data_dir = args.training_data_folder
    proc_data_dir = args.model_folder
    parallel_workers = args.num_workers
    disabled_clients = args.disable

    input_files = os.listdir(raw_data_dir)

    with concurrent.futures.ProcessPoolExecutor(
        max_workers=parallel_workers
    ) as executor:
        partial = functools.partial(
            ptd.process_file, raw_data_dir, proc_data_dir, disabled_clients
        )
        executor.map(partial, input_files)

def main():
    args = parseArgs()

    try:
        load_blocks(args)
        prepare_training_data(args)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()