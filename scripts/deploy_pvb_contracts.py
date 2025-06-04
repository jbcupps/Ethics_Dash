#!/usr/bin/env python3
"""
Smart Contract Deployment Script for Physical Verification Blockchain (PVB)

This script deploys the TrustedVerifierRegistry and DataSubmission contracts
to the specified blockchain network.
"""

import os
import sys
import json
import logging
from pathlib import Path
from web3 import Web3
from eth_account import Account
from solcx import compile_source, install_solc, set_solc_version

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.pvb.blockchain_interface import PVBBlockchainInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PVBContractDeployer:
    """Handles deployment of PVB smart contracts."""
    
    def __init__(self, web3_provider_url: str, private_key: str):
        """
        Initialize the contract deployer.
        
        Args:
            web3_provider_url: URL of the Web3 provider
            private_key: Private key for deployment transactions
        """
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))
        self.account = Account.from_key(private_key)
        self.contracts_dir = Path(__file__).parent.parent / "backend" / "app" / "pvb" / "contracts"
        
        # Check connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Web3 provider at {web3_provider_url}")
        
        logger.info(f"Connected to blockchain at {web3_provider_url}")
        logger.info(f"Deployer account: {self.account.address}")
        logger.info(f"Account balance: {self.w3.from_wei(self.w3.eth.get_balance(self.account.address), 'ether')} ETH")
    
    def compile_contracts(self) -> dict:
        """
        Compile the Solidity contracts.
        
        Returns:
            Dictionary containing compiled contract data
        """
        logger.info("Compiling smart contracts...")
        
        # Install and set Solidity compiler version
        try:
            install_solc('0.8.19')
            set_solc_version('0.8.19')
        except Exception as e:
            logger.warning(f"Could not install/set Solidity compiler: {e}")
        
        # Read contract source files
        registry_path = self.contracts_dir / "TrustedVerifierRegistry.sol"
        submission_path = self.contracts_dir / "DataSubmission.sol"
        
        if not registry_path.exists():
            raise FileNotFoundError(f"Registry contract not found at {registry_path}")
        if not submission_path.exists():
            raise FileNotFoundError(f"Submission contract not found at {submission_path}")
        
        registry_source = registry_path.read_text()
        submission_source = submission_path.read_text()
        
        # Combine sources for compilation
        combined_source = f"""
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.19;
        
        {registry_source}
        
        {submission_source}
        """
        
        try:
            compiled_contracts = compile_source(combined_source)
            logger.info("Contracts compiled successfully")
            return compiled_contracts
        except Exception as e:
            logger.error(f"Contract compilation failed: {e}")
            raise
    
    def deploy_contract(self, contract_interface: dict, constructor_args: list = None) -> dict:
        """
        Deploy a single contract.
        
        Args:
            contract_interface: Compiled contract interface
            constructor_args: Arguments for contract constructor
            
        Returns:
            Dictionary with deployment information
        """
        constructor_args = constructor_args or []
        
        # Create contract instance
        contract = self.w3.eth.contract(
            abi=contract_interface['abi'],
            bytecode=contract_interface['bin']
        )
        
        # Build constructor transaction
        constructor = contract.constructor(*constructor_args)
        transaction = constructor.build_transaction({
            'from': self.account.address,
            'gas': 3000000,  # Increased gas limit for deployment
            'gasPrice': self.w3.to_wei('20', 'gwei'),
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for transaction receipt
        logger.info(f"Waiting for contract deployment transaction: {tx_hash.hex()}")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            logger.info(f"Contract deployed successfully at address: {receipt.contractAddress}")
            return {
                'address': receipt.contractAddress,
                'transaction_hash': tx_hash.hex(),
                'gas_used': receipt.gasUsed,
                'abi': contract_interface['abi']
            }
        else:
            raise Exception(f"Contract deployment failed. Transaction hash: {tx_hash.hex()}")
    
    def deploy_all_contracts(self) -> dict:
        """
        Deploy all PVB contracts in the correct order.
        
        Returns:
            Dictionary containing deployment information for all contracts
        """
        logger.info("Starting PVB contract deployment...")
        
        # Compile contracts
        compiled_contracts = self.compile_contracts()
        
        # Extract contract interfaces
        registry_interface = compiled_contracts['<stdin>:TrustedVerifierRegistry']
        submission_interface = compiled_contracts['<stdin>:DataSubmission']
        
        deployment_info = {}
        
        # Deploy TrustedVerifierRegistry first
        logger.info("Deploying TrustedVerifierRegistry contract...")
        registry_deployment = self.deploy_contract(registry_interface)
        deployment_info['TrustedVerifierRegistry'] = registry_deployment
        
        # Deploy DataSubmission contract with registry address
        logger.info("Deploying DataSubmission contract...")
        submission_deployment = self.deploy_contract(
            submission_interface,
            constructor_args=[registry_deployment['address']]
        )
        deployment_info['DataSubmission'] = submission_deployment
        
        logger.info("All contracts deployed successfully!")
        return deployment_info
    
    def save_deployment_info(self, deployment_info: dict, output_file: str = None):
        """
        Save deployment information to a JSON file.
        
        Args:
            deployment_info: Deployment information dictionary
            output_file: Output file path (optional)
        """
        if output_file is None:
            output_file = f"pvb_deployment_{self.w3.eth.chain_id}.json"
        
        output_path = Path(output_file)
        
        # Add network information
        deployment_data = {
            'network': {
                'chain_id': self.w3.eth.chain_id,
                'provider_url': str(self.w3.provider.endpoint_uri),
                'deployer_address': self.account.address,
                'deployment_block': self.w3.eth.block_number
            },
            'contracts': deployment_info
        }
        
        with open(output_path, 'w') as f:
            json.dump(deployment_data, f, indent=2)
        
        logger.info(f"Deployment information saved to {output_path}")
    
    def verify_deployment(self, deployment_info: dict) -> bool:
        """
        Verify that deployed contracts are working correctly.
        
        Args:
            deployment_info: Deployment information dictionary
            
        Returns:
            True if verification successful, False otherwise
        """
        logger.info("Verifying contract deployment...")
        
        try:
            # Test TrustedVerifierRegistry
            registry_address = deployment_info['TrustedVerifierRegistry']['address']
            registry_abi = deployment_info['TrustedVerifierRegistry']['abi']
            
            registry_contract = self.w3.eth.contract(
                address=registry_address,
                abi=registry_abi
            )
            
            # Test reading openRegistration
            open_registration = registry_contract.functions.openRegistration().call()
            logger.info(f"Registry openRegistration: {open_registration}")
            
            # Test DataSubmission
            submission_address = deployment_info['DataSubmission']['address']
            submission_abi = deployment_info['DataSubmission']['abi']
            
            submission_contract = self.w3.eth.contract(
                address=submission_address,
                abi=submission_abi
            )
            
            # Test reading totalSubmissions
            total_submissions = submission_contract.functions.totalSubmissions().call()
            logger.info(f"Submission totalSubmissions: {total_submissions}")
            
            # Test that DataSubmission knows about the registry
            registry_in_submission = submission_contract.functions.trustedVerifierRegistry().call()
            if registry_in_submission.lower() != registry_address.lower():
                raise Exception("DataSubmission contract does not reference correct registry address")
            
            logger.info("Contract verification successful!")
            return True
            
        except Exception as e:
            logger.error(f"Contract verification failed: {e}")
            return False


def main():
    """Main deployment function."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration from environment
    web3_provider_url = os.getenv('WEB3_PROVIDER_URL', 'http://localhost:7545')
    private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
    
    if not private_key:
        logger.error("BLOCKCHAIN_PRIVATE_KEY environment variable is required")
        sys.exit(1)
    
    # Ensure private key has 0x prefix
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    
    try:
        # Create deployer instance
        deployer = PVBContractDeployer(web3_provider_url, private_key)
        
        # Deploy contracts
        deployment_info = deployer.deploy_all_contracts()
        
        # Save deployment information
        deployer.save_deployment_info(deployment_info)
        
        # Verify deployment
        if deployer.verify_deployment(deployment_info):
            logger.info("Deployment completed successfully!")
            
            # Print environment variables to set
            print("\n" + "="*60)
            print("DEPLOYMENT SUCCESSFUL!")
            print("="*60)
            print("\nAdd these environment variables to your .env file:")
            print(f"REGISTRY_CONTRACT_ADDRESS={deployment_info['TrustedVerifierRegistry']['address']}")
            print(f"SUBMISSION_CONTRACT_ADDRESS={deployment_info['DataSubmission']['address']}")
            print("\nContract addresses:")
            print(f"TrustedVerifierRegistry: {deployment_info['TrustedVerifierRegistry']['address']}")
            print(f"DataSubmission: {deployment_info['DataSubmission']['address']}")
            print("="*60)
        else:
            logger.error("Deployment verification failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 