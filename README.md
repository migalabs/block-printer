# block-printer

This repository contains a list of guides, services, and scripts for analyzing, indexing, and composing the distribution of validator clients proposing blocks in Ethereum networks.

## First steps

The Sigma-Prime team has done a fantastic job building and maintaining the [`sigp/block-print`](https://github.com/sigp/blockprint) beacon block proposer model. This repository contains a complete step-by-step guide to deploy a local instance of the model at the [`infrastructure-setup.md`](https://github.com/migalabs/block-printer/blob/main/infrastructure-setup.md) file.

## Tools and Analysis scripts

Our contribution to the sigp/block-print repository contains the tools and scripts we use to interact with the API, analyze the distributions.

This repository contains:

- [`sigp/block-print`](https://github.com/sigp/blockprint) setup guide the to have the model locally running - check the [`infrastructure-setup.md`](https://github.com/migalabs/block-printer/blob/main/infrastructure-setup.md) file.
- A `server.py` exposing an API where to ask to classify a valid Slot in the network where the Ethereum CL node is synced. (only supported Lighthouse nodes)
- A set of python scripts to measure the accuracy of the model by comparing it with the set of control validators (Rocket Pool, Client Teams' validators, etc.)
