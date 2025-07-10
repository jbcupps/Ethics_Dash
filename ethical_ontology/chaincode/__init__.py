"""
Smart Contracts (Chaincode) Module

Contains smart contract implementations for ethical principles:
- Deontological rules and duties
- Virtue-based reputation systems  
- Teleological outcome tracking
"""

from .base_contract import BaseSmartContract
from .deontic_rule import DeonticRuleContract
from .virtue_reputation import VirtueReputationContract
from .teleological_outcome import TeleologicalOutcomeContract

__all__ = [
    "BaseSmartContract",
    "DeonticRuleContract", 
    "VirtueReputationContract",
    "TeleologicalOutcomeContract"
] 