"""
Ethical Ontology Blockchain Package

This package implements a simplified blockchain simulation for encoding and verifying
ethical principles in smart contracts. It supports deontological duties, virtue-based
reputation systems, and teleological outcome tracking.

Aligns with paper's dual-blockchain architecture for decentralized ethical AI governance.
"""

__version__ = "1.0.0"
__author__ = "Ethics Dashboard Team"

# Package imports for external use
from .blockchain.core import EthicalOntologyBlockchain
from .chaincode.deontic_rule import DeonticRuleContract
from .chaincode.virtue_reputation import VirtueReputationContract
from .chaincode.teleological_outcome import TeleologicalOutcomeContract

__all__ = [
    "EthicalOntologyBlockchain",
    "DeonticRuleContract", 
    "VirtueReputationContract",
    "TeleologicalOutcomeContract"
] 