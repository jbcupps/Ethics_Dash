"""
Smart Contract Configuration for Ethical Ontology Blockchain

Defines configuration settings for smart contracts and their deployment parameters.
Aligns with paper's modular approach to ethical rule encoding.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class EthicalFramework(Enum):
    """Enumeration of supported ethical frameworks."""
    DEONTOLOGICAL = "deontological"
    VIRTUE_BASED = "virtue_based"
    TELEOLOGICAL = "teleological"
    HYBRID = "hybrid"

@dataclass
class ContractConfig:
    """Configuration for a single smart contract."""
    contract_name: str
    contract_class: str
    ethical_framework: EthicalFramework
    description: str
    auto_deploy: bool = True
    gas_limit: int = 1000000
    deployment_priority: int = 1
    configuration_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.configuration_params is None:
            self.configuration_params = {}

class ContractConfigManager:
    """
    Configuration manager for all smart contracts in the Ethical Ontology system.
    
    Handles contract registration, deployment configuration, and framework integration.
    """
    
    def __init__(self, env_prefix: str = "ETHICAL_CONTRACTS"):
        self.env_prefix = env_prefix
        self.contracts: Dict[str, ContractConfig] = {}
        
        # Load default contract configurations
        self._setup_default_contracts()
        
        # Load any environment-specific overrides
        self._load_environment_overrides()
    
    def _setup_default_contracts(self):
        """Setup default smart contract configurations."""
        
        # Deontological Rules Contract
        self.contracts["deontic_rules"] = ContractConfig(
            contract_name="DeonticRuleContract",
            contract_class="ethical_ontology.chaincode.deontic_rule.DeonticRuleContract",
            ethical_framework=EthicalFramework.DEONTOLOGICAL,
            description="Evaluates actions against deontological duties and moral rules",
            auto_deploy=True,
            gas_limit=500000,
            deployment_priority=1,
            configuration_params={
                "enable_universalizability_test": True,
                "strict_mode": False,
                "rule_weight_adjustments": {
                    "do_not_lie": 1.0,
                    "respect_autonomy": 1.0,
                    "keep_promises": 0.9,
                    "do_not_steal": 0.8,
                    "do_not_harm": 0.9
                }
            }
        )
        
        # Virtue-Based Reputation Contract
        self.contracts["virtue_reputation"] = ContractConfig(
            contract_name="VirtueReputationContract",
            contract_class="ethical_ontology.chaincode.virtue_reputation.VirtueReputationContract",
            ethical_framework=EthicalFramework.VIRTUE_BASED,
            description="Tracks virtue-based reputation and character assessments",
            auto_deploy=True,
            gas_limit=750000,
            deployment_priority=2,
            configuration_params={
                "enable_reputation_tracking": True,
                "reputation_decay_rate": 0.05,  # 5% decay per period
                "golden_mean_tolerance": 0.1,
                "virtue_weight_adjustments": {
                    "honesty": 1.0,
                    "justice": 1.0,
                    "courage": 0.9,
                    "compassion": 0.9,
                    "wisdom": 0.9,
                    "temperance": 0.8
                }
            }
        )
        
        # Teleological Outcome Contract  
        self.contracts["teleological_outcomes"] = ContractConfig(
            contract_name="TeleologicalOutcomeContract",
            contract_class="ethical_ontology.chaincode.teleological_outcome.TeleologicalOutcomeContract",
            ethical_framework=EthicalFramework.TELEOLOGICAL,
            description="Evaluates actions based on predicted consequences and outcomes",
            auto_deploy=True,
            gas_limit=1000000,
            deployment_priority=3,
            configuration_params={
                "enable_outcome_tracking": True,
                "default_time_horizon": "medium_term",
                "default_certainty_level": 0.7,
                "utility_threshold": 0.1,
                "outcome_weight_adjustments": {
                    "wellbeing": 1.0,
                    "justice": 0.9,
                    "autonomy": 0.9,
                    "environment": 0.8,
                    "knowledge": 0.7,
                    "social_cohesion": 0.6
                }
            }
        )
        
        logger.info(f"Loaded {len(self.contracts)} default contract configurations")
    
    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables."""
        
        # Check for contract-specific overrides
        for contract_id, config in self.contracts.items():
            env_key = f"{self.env_prefix}_{contract_id.upper()}_AUTO_DEPLOY"
            if os.getenv(env_key):
                config.auto_deploy = os.getenv(env_key).lower() == "true"
                logger.info(f"Override: {contract_id} auto_deploy = {config.auto_deploy}")
            
            # Gas limit override
            gas_env_key = f"{self.env_prefix}_{contract_id.upper()}_GAS_LIMIT"
            if os.getenv(gas_env_key):
                try:
                    config.gas_limit = int(os.getenv(gas_env_key))
                    logger.info(f"Override: {contract_id} gas_limit = {config.gas_limit}")
                except ValueError:
                    logger.warning(f"Invalid gas limit for {contract_id}: {os.getenv(gas_env_key)}")
    
    def get_contract_config(self, contract_id: str) -> Optional[ContractConfig]:
        """Get configuration for a specific contract."""
        return self.contracts.get(contract_id)
    
    def get_all_contracts(self) -> Dict[str, ContractConfig]:
        """Get all contract configurations."""
        return self.contracts.copy()
    
    def get_contracts_by_framework(self, framework: EthicalFramework) -> Dict[str, ContractConfig]:
        """Get all contracts for a specific ethical framework."""
        return {
            contract_id: config 
            for contract_id, config in self.contracts.items()
            if config.ethical_framework == framework
        }
    
    def get_auto_deploy_contracts(self) -> Dict[str, ContractConfig]:
        """Get contracts that should be automatically deployed."""
        return {
            contract_id: config 
            for contract_id, config in self.contracts.items()
            if config.auto_deploy
        }
    
    def get_deployment_order(self) -> List[str]:
        """Get contract IDs in deployment priority order."""
        return sorted(
            self.contracts.keys(),
            key=lambda x: self.contracts[x].deployment_priority
        )
    
    def add_contract(self, contract_id: str, config: ContractConfig):
        """Add a new contract configuration."""
        self.contracts[contract_id] = config
        logger.info(f"Added contract configuration: {contract_id}")
    
    def remove_contract(self, contract_id: str):
        """Remove a contract configuration."""
        if contract_id in self.contracts:
            del self.contracts[contract_id]
            logger.info(f"Removed contract configuration: {contract_id}")
    
    def update_contract_param(self, contract_id: str, param_name: str, param_value: Any):
        """Update a specific parameter for a contract."""
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        self.contracts[contract_id].configuration_params[param_name] = param_value
        logger.info(f"Updated {contract_id}.{param_name} = {param_value}")
    
    def validate_configurations(self) -> List[str]:
        """Validate all contract configurations and return any issues."""
        issues = []
        
        for contract_id, config in self.contracts.items():
            # Check contract class path
            try:
                # Basic import path validation
                parts = config.contract_class.split('.')
                if len(parts) < 2:
                    issues.append(f"{contract_id}: Invalid contract class path")
            except Exception:
                issues.append(f"{contract_id}: Invalid contract class path")
            
            # Check gas limit
            if config.gas_limit < 100000:
                issues.append(f"{contract_id}: Gas limit too low (minimum 100,000)")
            
            # Check deployment priority
            if config.deployment_priority < 1:
                issues.append(f"{contract_id}: Deployment priority must be >= 1")
        
        # Check for duplicate deployment priorities
        priorities = [config.deployment_priority for config in self.contracts.values()]
        if len(priorities) != len(set(priorities)):
            issues.append("Duplicate deployment priorities found")
        
        return issues
    
    def get_contract_deployment_script(self, contract_id: str) -> str:
        """Generate a deployment script for a specific contract."""
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        config = self.contracts[contract_id]
        
        script = f"""
# Deployment script for {config.contract_name}
# Framework: {config.ethical_framework.value}
# Description: {config.description}

from {config.contract_class} import {config.contract_name}
from ethical_ontology.blockchain.core import EthicalOntologyBlockchain

def deploy_{contract_id}(blockchain: EthicalOntologyBlockchain):
    \"\"\"Deploy the {config.contract_name} to the blockchain.\"\"\"
    
    # Initialize contract with configuration
    contract_instance = {config.contract_name}()
    
    # Apply configuration parameters
    config_params = {config.configuration_params}
    for param_name, param_value in config_params.items():
        if hasattr(contract_instance, f'set_{{param_name}}'):
            getattr(contract_instance, f'set_{{param_name}}')(param_value)
    
    # Deploy to blockchain
    contract_address = blockchain.deploy_contract(
        "{config.contract_name}",
        contract_instance
    )
    
    print(f"Deployed {config.contract_name} at address: {{contract_address}}")
    return contract_address

if __name__ == "__main__":
    # Example usage
    blockchain = EthicalOntologyBlockchain()
    address = deploy_{contract_id}(blockchain)
"""
        return script
    
    def get_multi_framework_config(self) -> Dict[str, Any]:
        """
        Get configuration for multi-framework ethical evaluation.
        
        This enables the system to use multiple ethical frameworks together
        for comprehensive moral reasoning.
        """
        frameworks = {}
        
        for framework in EthicalFramework:
            contracts = self.get_contracts_by_framework(framework)
            if contracts:
                frameworks[framework.value] = {
                    "contracts": list(contracts.keys()),
                    "weight": self._get_framework_weight(framework),
                    "enabled": len(contracts) > 0 and any(c.auto_deploy for c in contracts.values())
                }
        
        return {
            "frameworks": frameworks,
            "aggregation_method": "weighted_consensus",
            "minimum_agreement_threshold": 0.6,
            "enable_framework_mixing": True
        }
    
    def _get_framework_weight(self, framework: EthicalFramework) -> float:
        """Get the weight for a specific ethical framework in multi-framework evaluation."""
        # These weights can be configured based on the specific use case
        weights = {
            EthicalFramework.DEONTOLOGICAL: 0.4,  # Strong emphasis on duties and rules
            EthicalFramework.VIRTUE_BASED: 0.3,   # Character and reputation important
            EthicalFramework.TELEOLOGICAL: 0.3,   # Consequences matter
            EthicalFramework.HYBRID: 0.5          # If hybrid frameworks are developed
        }
        return weights.get(framework, 0.25)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire configuration to dictionary."""
        return {
            "contracts": {
                contract_id: {
                    **asdict(config),
                    "ethical_framework": config.ethical_framework.value
                }
                for contract_id, config in self.contracts.items()
            },
            "multi_framework": self.get_multi_framework_config()
        } 