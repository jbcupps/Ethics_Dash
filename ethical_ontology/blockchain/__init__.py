"""
Blockchain Core Module

Contains the core blockchain simulation classes for the Ethical Ontology Blockchain.
"""

from .core import EthicalOntologyBlockchain, Block, Transaction
from .network import BlockchainNetwork

__all__ = ["EthicalOntologyBlockchain", "Block", "Transaction", "BlockchainNetwork"] 