# block-printer
This repo contains the list of guides, services and scripts to analyze, index and compose the distribution of validator clients proposing blocks in Ethereum networks.

## First steps
The Sigma-Prime team has done an amazing job building and maintaining the [`sigp/block-print`](https://github.com/sigp/blockprint) beacon block proposer model. This repo contains a complete step-by-step guide to deploy a local instance of the model at the [`infrastructure-setup.md`](https://github.com/migalabs/block-printer/blob/main/infrastructure-setup.md) file.

## Tools and Analysis scripts
Our contribution to the `sigp/block-print` repo, this repo contains the list of tools and scripts that we use to interact with the API, analyze the distributions, as well as index the results into a PostgreSQL.

However most of this work is still remains in the #TODO list.

## Missing Tasks
This repo is still in a working-on progress, so this are the list of tasks that are missing:
- [ ] Setup the [`sigp/block-print`](https://github.com/sigp/blockprint) model locally and document the process into the [`infrastructure-setup.md`](https://github.com/migalabs/block-printer/blob/main/infrastructure-setup.md) file.
- [ ] Expose the [`API`](https://github.com/sigp/blockprint/blob/main/docs/api.md) into a given endpoint (document this also in the `infra-setup` file)
- [ ] Benchmark the accuracy of the model comparing it with the set of control validators (Rocket Pool, Client Teams' validators, etc)
- [ ] Create a python library that can interact with the API, requesting to clasify the client of the validator that proposed the block (index the guess weigts into a PostgreSQL database)
- [ ] Create a python tool that subscribea to the [`New Block Event`](https://ethereum.github.io/beacon-APIs/#/Events/eventstream) from a given Beacon Node, an triggers an API call to classfy the porposer of the block indexing it into a PostgreSQL database.
