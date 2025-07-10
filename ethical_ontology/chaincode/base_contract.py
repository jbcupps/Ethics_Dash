"""
Base Smart Contract for Ethical Ontology

Provides the foundation for all ethical smart contracts in the blockchain.
Aligns with paper's modular approach to ethical rule encoding.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class BaseSmartContract(ABC):
    """
    Abstract base class for all ethical smart contracts.
    
    Provides common functionality and enforces the interface
    that all ethical contracts must implement.
    """
    
    def __init__(self, contract_name: str, version: str = "1.0.0"):
        self.contract_name = contract_name
        self.version = version
        self.deployed_at = time.time()
        self.call_count = 0
        self.state: Dict[str, Any] = {}
        
        logger.info(f"Initialized {contract_name} v{version}")
    
    def get_contract_info(self) -> Dict[str, Any]:
        """Return basic information about this contract."""
        return {
            "name": self.contract_name,
            "version": self.version,
            "deployed_at": self.deployed_at,
            "call_count": self.call_count,
            "type": self.__class__.__name__
        }
    
    def _log_call(self, method: str, parameters: Dict[str, Any], result: Any):
        """Log a contract method call for audit purposes."""
        self.call_count += 1
        logger.debug(f"{self.contract_name}.{method} called with {parameters} -> {result}")
    
    def _validate_input(self, parameters: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that required fields are present in the input parameters."""
        for field in required_fields:
            if field not in parameters:
                logger.error(f"Missing required field: {field}")
                return False
            if parameters[field] is None:
                logger.error(f"Field {field} cannot be None")
                return False
        return True
    
    def _sanitize_text_input(self, text: str, max_length: int = 1000) -> str:
        """Sanitize text input to prevent injection attacks."""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Input truncated to {max_length} characters")
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", '\x00']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text.strip()
    
    @abstractmethod
    def check_compliance(self, action_description: str, **kwargs) -> Dict[str, Any]:
        """
        Check if an action complies with the ethical rules encoded in this contract.
        
        Args:
            action_description: Natural language description of the action to evaluate
            **kwargs: Additional parameters specific to the contract type
            
        Returns:
            Dict containing:
            - compliant: bool indicating if action is ethical
            - confidence: float (0-1) indicating confidence in the assessment
            - reasoning: str explaining the decision
            - rule_applied: str indicating which specific rule was used
        """
        pass
    
    @abstractmethod
    def get_applicable_rules(self) -> List[Dict[str, Any]]:
        """
        Return a list of ethical rules that this contract can evaluate.
        
        Returns:
            List of dicts, each containing:
            - rule_id: str unique identifier for the rule
            - rule_name: str human-readable name
            - description: str explanation of the rule
            - parameters: List[str] required parameters for evaluation
        """
        pass
    
    def update_state(self, key: str, value: Any):
        """Update the contract's internal state."""
        self.state[key] = {
            "value": value,
            "updated_at": time.time()
        }
        logger.debug(f"Updated state: {key} = {value}")
    
    def get_state(self, key: str) -> Any:
        """Get a value from the contract's internal state."""
        if key in self.state:
            return self.state[key]["value"]
        return None
    
    def get_full_state(self) -> Dict[str, Any]:
        """Get the complete internal state of the contract."""
        return self.state.copy()
    
    def reset_state(self):
        """Reset the contract's internal state (for testing purposes)."""
        self.state = {}
        logger.info(f"Reset state for {self.contract_name}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return usage metrics for this contract."""
        return {
            "total_calls": self.call_count,
            "uptime_seconds": time.time() - self.deployed_at,
            "state_size": len(self.state),
            "average_calls_per_hour": self.call_count / max(1, (time.time() - self.deployed_at) / 3600)
        } 