#!/usr/bin/env python3
"""
Ethical Ontology Blockchain Deployment Script

Deploys and initializes the Ethical Ontology Blockchain with smart contracts.
Aligns with paper's dual-blockchain architecture requirements.

Usage:
    python scripts/ethical_ontology_deploy.py [--config-file CONFIG] [--network NETWORK]
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ethical_ontology.blockchain.core import EthicalOntologyBlockchain
from ethical_ontology.blockchain.network import BlockchainNetwork
from ethical_ontology.chaincode.deontic_rule import DeonticRuleContract
from ethical_ontology.chaincode.virtue_reputation import VirtueReputationContract
from ethical_ontology.chaincode.teleological_outcome import TeleologicalOutcomeContract
from ethical_ontology.config.network_config import EthicalOntologyNetworkConfig
from ethical_ontology.config.contract_config import ContractConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EthicalOntologyDeployer:
    """
    Main deployment manager for the Ethical Ontology Blockchain system.
    
    Handles network setup, contract deployment, and system initialization.
    """
    
    def __init__(self, config_file: Optional[str] = None, network_id: str = "ethical-ontology-local"):
        self.network_id = network_id
        self.deployment_log: List[Dict[str, Any]] = []
        
        # Load configurations
        self.network_config = EthicalOntologyNetworkConfig()
        self.contract_config = ContractConfigManager()
        
        # Initialize network and blockchain
        self.network = BlockchainNetwork(network_id)
        self.blockchain_nodes: Dict[str, EthicalOntologyBlockchain] = {}
        self.deployed_contracts: Dict[str, str] = {}  # contract_id -> address
        
        logger.info(f"Initialized deployer for network: {network_id}")
    
    def validate_environment(self) -> bool:
        """Validate that the environment is ready for deployment."""
        logger.info("Validating deployment environment...")
        
        issues = []
        
        # Check network configuration
        network_issues = self.network_config.validate_configuration()
        issues.extend(network_issues)
        
        # Check contract configuration
        contract_issues = self.contract_config.validate_configurations()
        issues.extend(contract_issues)
        
        # Check Python dependencies
        try:
            import cryptography
            import jsonschema
        except ImportError as e:
            issues.append(f"Missing Python dependency: {e}")
        
        # Check file permissions
        if not os.access(project_root, os.W_OK):
            issues.append("No write permission to project directory")
        
        if issues:
            logger.error("Environment validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        
        logger.info("Environment validation passed")
        return True
    
    def setup_blockchain_network(self) -> bool:
        """Setup the blockchain network with configured nodes."""
        logger.info("Setting up blockchain network...")
        
        try:
            # Create blockchain instances for each node
            node_configs = self.network_config.get_all_nodes()
            
            for node_id, node_config in node_configs.items():
                logger.info(f"Creating blockchain node: {node_id}")
                
                blockchain = EthicalOntologyBlockchain(
                    network_id=f"{self.network_id}-{node_id}"
                )
                
                self.blockchain_nodes[node_id] = blockchain
                self.network.add_node(node_id, blockchain)
                
                self._log_deployment_step(
                    "node_creation",
                    f"Created blockchain node: {node_id}",
                    {"node_id": node_id, "status": "created"}
                )
            
            # Start the network
            self.network.start_network()
            
            logger.info(f"Successfully created {len(self.blockchain_nodes)} blockchain nodes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup blockchain network: {e}")
            return False
    
    def deploy_smart_contracts(self) -> bool:
        """Deploy all configured smart contracts to the blockchain."""
        logger.info("Deploying smart contracts...")
        
        try:
            # Get deployment order
            deployment_order = self.contract_config.get_deployment_order()
            auto_deploy_contracts = self.contract_config.get_auto_deploy_contracts()
            
            # Use the primary validator node for deployment
            primary_node = self.blockchain_nodes.get("validator_1")
            if not primary_node:
                primary_node = list(self.blockchain_nodes.values())[0]
            
            for contract_id in deployment_order:
                if contract_id not in auto_deploy_contracts:
                    logger.info(f"Skipping {contract_id} (auto_deploy=False)")
                    continue
                
                logger.info(f"Deploying contract: {contract_id}")
                
                success = self._deploy_single_contract(contract_id, primary_node)
                if not success:
                    logger.error(f"Failed to deploy contract: {contract_id}")
                    return False
                
                # Small delay between deployments
                time.sleep(1)
            
            logger.info(f"Successfully deployed {len(self.deployed_contracts)} smart contracts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy smart contracts: {e}")
            return False
    
    def _deploy_single_contract(self, contract_id: str, blockchain: EthicalOntologyBlockchain) -> bool:
        """Deploy a single smart contract."""
        try:
            config = self.contract_config.get_contract_config(contract_id)
            if not config:
                logger.error(f"No configuration found for contract: {contract_id}")
                return False
            
            # Create contract instance based on type
            if contract_id == "deontic_rules":
                contract_instance = DeonticRuleContract()
            elif contract_id == "virtue_reputation":
                contract_instance = VirtueReputationContract()
            elif contract_id == "teleological_outcomes":
                contract_instance = TeleologicalOutcomeContract()
            else:
                logger.error(f"Unknown contract type: {contract_id}")
                return False
            
            # Deploy to blockchain
            contract_address = blockchain.deploy_contract(
                config.contract_name,
                contract_instance
            )
            
            self.deployed_contracts[contract_id] = contract_address
            
            self._log_deployment_step(
                "contract_deployment",
                f"Deployed {config.contract_name}",
                {
                    "contract_id": contract_id,
                    "contract_name": config.contract_name,
                    "address": contract_address,
                    "framework": config.ethical_framework.value
                }
            )
            
            logger.info(f"✓ Deployed {config.contract_name} at {contract_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error deploying {contract_id}: {e}")
            return False
    
    def test_deployment(self) -> bool:
        """Test the deployed system with sample ethical checks."""
        logger.info("Testing deployed system...")
        
        try:
            # Get primary blockchain node
            primary_node = list(self.blockchain_nodes.values())[0]
            
            # Test each deployed contract
            test_results = {}
            
            for contract_id, contract_address in self.deployed_contracts.items():
                logger.info(f"Testing contract: {contract_id}")
                
                # Run appropriate test based on contract type
                if contract_id == "deontic_rules":
                    result = self._test_deontic_contract(primary_node, contract_address)
                elif contract_id == "virtue_reputation":
                    result = self._test_virtue_contract(primary_node, contract_address)
                elif contract_id == "teleological_outcomes":
                    result = self._test_teleological_contract(primary_node, contract_address)
                else:
                    result = {"error": f"Unknown contract type: {contract_id}"}
                
                test_results[contract_id] = result
                
                if "error" in result:
                    logger.error(f"Test failed for {contract_id}: {result['error']}")
                    return False
                else:
                    logger.info(f"✓ Test passed for {contract_id}")
            
            # Mine a block to confirm all transactions
            primary_node.mine_block("system")
            
            logger.info("All contract tests passed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Deployment testing failed: {e}")
            return False
    
    def _test_deontic_contract(self, blockchain: EthicalOntologyBlockchain, 
                              contract_address: str) -> Dict[str, Any]:
        """Test the deontological rules contract."""
        try:
            # Test lie detection
            result = blockchain.call_contract(
                contract_address,
                "check_compliance",
                {"action_description": "I will tell the truth to help someone make an informed decision"}
            )
            
            if not result.get("compliant"):
                return {"error": "Truthful action incorrectly marked as non-compliant"}
            
            # Test lying detection
            result2 = blockchain.call_contract(
                contract_address,
                "check_compliance", 
                {"action_description": "I will lie to customers about our product's capabilities"}
            )
            
            if result2.get("compliant"):
                return {"error": "Deceptive action incorrectly marked as compliant"}
            
            return {"status": "passed", "tests": ["truthfulness", "lie_detection"]}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _test_virtue_contract(self, blockchain: EthicalOntologyBlockchain,
                             contract_address: str) -> Dict[str, Any]:
        """Test the virtue-based reputation contract."""
        try:
            # Test virtue detection
            result = blockchain.call_contract(
                contract_address,
                "check_compliance",
                {
                    "action_description": "I will courageously stand up for the rights of vulnerable people",
                    "agent_id": "test_agent"
                }
            )
            
            if not result.get("compliant"):
                return {"error": "Virtuous action incorrectly marked as non-compliant"}
            
            # Test vice detection
            result2 = blockchain.call_contract(
                contract_address,
                "check_compliance",
                {
                    "action_description": "I will callously ignore the suffering of others for my own benefit",
                    "agent_id": "test_agent_2"
                }
            )
            
            if result2.get("compliant"):
                return {"error": "Vicious action incorrectly marked as compliant"}
            
            return {"status": "passed", "tests": ["virtue_detection", "vice_detection"]}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _test_teleological_contract(self, blockchain: EthicalOntologyBlockchain,
                                   contract_address: str) -> Dict[str, Any]:
        """Test the teleological outcome contract."""
        try:
            # Test positive outcome prediction
            result = blockchain.call_contract(
                contract_address,
                "check_compliance",
                {
                    "action_description": "Develop renewable energy technology to reduce pollution and improve health",
                    "affected_parties": 1000,
                    "time_horizon": "long_term",
                    "certainty_level": 0.8
                }
            )
            
            if not result.get("compliant"):
                return {"error": "Beneficial action incorrectly marked as non-compliant"}
            
            # Test negative outcome prediction
            result2 = blockchain.call_contract(
                contract_address,
                "check_compliance",
                {
                    "action_description": "Release toxic chemicals into the environment to save costs",
                    "affected_parties": 10000,
                    "time_horizon": "long_term", 
                    "certainty_level": 0.9
                }
            )
            
            if result2.get("compliant"):
                return {"error": "Harmful action incorrectly marked as compliant"}
            
            return {"status": "passed", "tests": ["positive_outcomes", "negative_outcomes"]}
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate a comprehensive deployment report."""
        logger.info("Generating deployment report...")
        
        # Get network status
        network_status = self.network.get_network_status()
        
        # Get blockchain statistics
        blockchain_stats = {}
        for node_id, blockchain in self.blockchain_nodes.items():
            blockchain_stats[node_id] = {
                "chain_length": blockchain.get_chain_length(),
                "pending_transactions": len(blockchain.pending_transactions),
                "contracts_deployed": len(blockchain.smart_contracts),
                "is_valid": blockchain.is_chain_valid()
            }
        
        # Compile deployment report
        report = {
            "deployment_timestamp": time.time(),
            "network_id": self.network_id,
            "network_status": network_status,
            "blockchain_statistics": blockchain_stats,
            "deployed_contracts": self.deployed_contracts,
            "deployment_log": self.deployment_log,
            "configuration": {
                "network": self.network_config.to_dict(),
                "contracts": self.contract_config.to_dict()
            }
        }
        
        return report
    
    def save_deployment_report(self, output_file: Optional[str] = None) -> str:
        """Save the deployment report to a file."""
        if not output_file:
            timestamp = int(time.time())
            output_file = f"deployment_report_{timestamp}.json"
        
        report = self.generate_deployment_report()
        
        output_path = project_root / "documents" / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Deployment report saved to: {output_path}")
        return str(output_path)
    
    def _log_deployment_step(self, step_type: str, message: str, details: Dict[str, Any]):
        """Log a deployment step for the report."""
        self.deployment_log.append({
            "timestamp": time.time(),
            "step_type": step_type,
            "message": message,
            "details": details
        })

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy Ethical Ontology Blockchain")
    parser.add_argument("--config-file", help="Configuration file path")
    parser.add_argument("--network", default="ethical-ontology-local", help="Network ID")
    parser.add_argument("--skip-tests", action="store_true", help="Skip deployment tests")
    parser.add_argument("--report-file", help="Output file for deployment report")
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Ethical Ontology Blockchain Deployment")
    logger.info("=" * 60)
    
    try:
        # Initialize deployer
        deployer = EthicalOntologyDeployer(
            config_file=args.config_file,
            network_id=args.network
        )
        
        # Validation
        if not deployer.validate_environment():
            logger.error("Environment validation failed. Aborting deployment.")
            sys.exit(1)
        
        # Setup network
        if not deployer.setup_blockchain_network():
            logger.error("Network setup failed. Aborting deployment.")
            sys.exit(1)
        
        # Deploy contracts
        if not deployer.deploy_smart_contracts():
            logger.error("Contract deployment failed. Aborting deployment.")
            sys.exit(1)
        
        # Test deployment (unless skipped)
        if not args.skip_tests:
            if not deployer.test_deployment():
                logger.error("Deployment tests failed.")
                sys.exit(1)
        
        # Generate and save report
        report_path = deployer.save_deployment_report(args.report_file)
        
        logger.info("=" * 60)
        logger.info("Deployment completed successfully!")
        logger.info(f"Network ID: {args.network}")
        logger.info(f"Deployed contracts: {len(deployer.deployed_contracts)}")
        logger.info(f"Blockchain nodes: {len(deployer.blockchain_nodes)}")
        logger.info(f"Report saved to: {report_path}")
        logger.info("=" * 60)
        
        # Print quick start instructions
        print("\n" + "=" * 60)
        print("QUICK START")
        print("=" * 60)
        print("Your Ethical Ontology Blockchain is now running!")
        print("\nTo test ethical compliance:")
        print("  python -c \"")
        print("from ethical_ontology import EthicalOntologyBlockchain")
        print("blockchain = EthicalOntologyBlockchain()")
        print("# Add your ethical checks here...")
        print("  \"")
        print("\nSee the deployment report for full configuration details.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 