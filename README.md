# block-printer
This repo contains the list of guides, services, and scripts to analyze, index, and compose the distribution of validator clients proposing blocks in Ethereum networks.

## First steps
The Sigma-Prime team has done a fantastic job building and maintaining the [`sigp/block-print`](https://github.com/sigp/blockprint) beacon block proposer model. This repo contains a complete step-by-step guide to deploy a local instance of the model at the [`infrastructure-setup.md`](https://github.com/migalabs/block-printer/blob/main/infrastructure-setup.md) file.

## Tools and Analysis scripts
Our contribution to the sigp/block-print repo contains the tools and scripts we use to interact with the API, analyze the distributions, and index the results into a PostgreSQL.

However, most of this work remains in the #TODO list.

## Missing Tasks
This repo is in working-on progress, so this is the list of tasks that are missing:
- [ ] Setup the [`sigp/block-print`](https://github.com/sigp/blockprint) model locally and document the process into the [`infrastructure-setup.md`](https://github.com/migalabs/block-printer/blob/main/infrastructure-setup.md) file.
- [ ] Expose the [`API`](https://github.com/sigp/blockprint/blob/main/docs/api.md) into a given endpoint (document this also in the `infra-setup` file)
- [ ] Benchmark the accuracy of the model by comparing it with the set of control validators (Rocket Pool, Client Teams' validators, etc.)
- [ ] Create a python library that can interact with the API, requesting to classify the client of the validator that proposed the block (index the guess weights into a PostgreSQL database)
- [ ] Create a python tool that subscribes to the [`New Block Event`](https://ethereum.github.io/beacon-APIs/#/Events/eventstream) from a given Beacon Node and triggers an API call to classify the proposer of the block, indexing it into a PostgreSQL database.
