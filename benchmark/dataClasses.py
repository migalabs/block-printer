#!/usr/bin/env python3

from dataclasses import dataclass, field

@dataclass
class BlockGuess:
    slot: int
    proposer_index: int
    best_guess_single: str
    best_guess_multi: str
    probability_map: dict

    @classmethod
    def from_json(cls, json):
        return cls(**json)

@dataclass
class ProbabilityMapArray:
    Lighthouse: list = field(default_factory=list)
    Lodestar: list = field(default_factory=list)
    Nimbus: list = field(default_factory=list)
    Prysm: list = field(default_factory=list)
    Teku: list = field(default_factory=list)

    def add_elem(self, Lighthouse, Lodestar, Nimbus, Prysm, Teku):
        self.Lighthouse.append(Lighthouse)
        self.Lodestar.append(Lodestar)
        self.Nimbus.append(Nimbus)
        self.Prysm.append(Prysm)
        self.Teku.append(Teku)
    
    def getLists(self):
        return [self.Lighthouse, self.Lodestar, self.Nimbus, self.Prysm, self.Teku]
