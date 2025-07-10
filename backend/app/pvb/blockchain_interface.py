"""
Blockchain interface module for Physical Verification Blockchain (PVB) system.
Handles Web3 interactions with TrustedVerifierRegistry and DataSubmission smart contracts.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from .schemas import (
    convert_device_id_to_bytes32, 
    convert_data_hash_to_bytes32,
    hash_data
)

# Configure logging
logger = logging.getLogger(__name__)

class PVBBlockchainInterface:
    """
    Interface for interacting with Physical Verification Blockchain smart contracts.
    Manages connections to TrustedVerifierRegistry and DataSubmission contracts.
    """
    
    def __init__(self, 
                 web3_provider_url: Optional[str] = None,
                 registry_contract_address: Optional[str] = None,
                 submission_contract_address: Optional[str] = None,
                 private_key: Optional[str] = None):
        """
        Initialize the blockchain interface.
        
        Args:
            web3_provider_url: URL of the Web3 provider (e.g., local Ganache, Infura)
            registry_contract_address: Address of deployed TrustedVerifierRegistry contract
            submission_contract_address: Address of deployed DataSubmission contract
            private_key: Private key for transaction signing (hex string)
        """
        self.web3_provider_url = web3_provider_url or os.getenv('WEB3_PROVIDER_URL', 'http://localhost:7545')
        self.registry_contract_address = registry_contract_address or os.getenv('REGISTRY_CONTRACT_ADDRESS')
        self.submission_contract_address = submission_contract_address or os.getenv('SUBMISSION_CONTRACT_ADDRESS')
        self.private_key = private_key or os.getenv('BLOCKCHAIN_PRIVATE_KEY')
        
        # Initialize Web3 connection
        self.w3 = None
        self.account = None
        self.registry_contract = None
        self.submission_contract = None
        
        # Contract ABIs (simplified - in production, load from compiled contracts)
        self.registry_abi = self._get_registry_abi()
        self.submission_abi = self._get_submission_abi()
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Web3 connection and contract instances."""
        try:
            # Connect to Web3 provider
            self.w3 = Web3(Web3.HTTPProvider(self.web3_provider_url))
            
            # Add middleware for PoA networks (like some testnets)
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Check connection
            if not self.w3.is_connected():
                raise ConnectionError(f"Failed to connect to Web3 provider at {self.web3_provider_url}")
            
            logger.info(f"Connected to blockchain at {self.web3_provider_url}")
            
            # Initialize account if private key is provided
            if self.private_key:
                self.account = Account.from_key(self.private_key)
                logger.info(f"Account initialized: {self.account.address}")
            
            # Initialize contract instances
            if self.registry_contract_address:
                self.registry_contract = self.w3.eth.contract(
                    address=self.registry_contract_address,
                    abi=self.registry_abi
                )
                logger.info(f"Registry contract initialized at {self.registry_contract_address}")
            
            if self.submission_contract_address:
                self.submission_contract = self.w3.eth.contract(
                    address=self.submission_contract_address,
                    abi=self.submission_abi
                )
                logger.info(f"Submission contract initialized at {self.submission_contract_address}")
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain connection: {str(e)}")
            raise
    
    def is_connected(self) -> bool:
        """Check if Web3 connection is healthy."""
        try:
            return self.w3 is not None and self.w3.is_connected()
        except Exception:
            return False
    
    def get_block_number(self) -> int:
        """Get current block number."""
        return self.w3.eth.block_number
    
    def get_account_balance(self, address: Optional[str] = None) -> float:
        """Get ETH balance of an account."""
        address = address or (self.account.address if self.account else None)
        if not address:
            raise ValueError("No address provided and no account initialized")
        
        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')
    
    # Trusted Verifier Registry Functions
    
    def register_verifier(self, name: str, metadata: str = "") -> Dict[str, Any]:
        """
        Register a new Trusted Verifier.
        
        Args:
            name: Name of the verifier organization
            metadata: Additional metadata about the verifier
            
        Returns:
            Transaction receipt and details
        """
        if not self.registry_contract or not self.account:
            raise ValueError("Registry contract or account not initialized")
        
        try:
            # Build transaction
            function = self.registry_contract.functions.registerVerifier(name, metadata)
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Verifier registered: {name}, tx: {tx_hash.hex()}")
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'verifier_address': self.account.address
            }
            
        except Exception as e:
            logger.error(f"Failed to register verifier: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_device(self, device_id: str, device_public_key: str, metadata: str = "") -> Dict[str, Any]:
        """
        Add a device under the current verifier's vouching.
        
        Args:
            device_id: Unique identifier for the device
            device_public_key: Public key of the device
            metadata: Additional device metadata
            
        Returns:
            Transaction receipt and details
        """
        if not self.registry_contract or not self.account:
            raise ValueError("Registry contract or account not initialized")
        
        try:
            device_id_bytes32 = convert_device_id_to_bytes32(device_id)
            
            function = self.registry_contract.functions.addDevice(
                device_id_bytes32, device_public_key, metadata
            )
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Device added: {device_id}, tx: {tx_hash.hex()}")
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'device_id': device_id
            }
            
        except Exception as e:
            logger.error(f"Failed to add device: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_device_active(self, device_id: str) -> bool:
        """Check if a device is active and registered."""
        if not self.registry_contract:
            raise ValueError("Registry contract not initialized")
        
        try:
            device_id_bytes32 = convert_device_id_to_bytes32(device_id)
            return self.registry_contract.functions.isDeviceActive(device_id_bytes32).call()
        except Exception as e:
            logger.error(f"Failed to check device status: {str(e)}")
            return False
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device information from the registry."""
        if not self.registry_contract:
            raise ValueError("Registry contract not initialized")
        
        try:
            device_id_bytes32 = convert_device_id_to_bytes32(device_id)
            device_data = self.registry_contract.functions.getDevice(device_id_bytes32).call()
            
            return {
                'verifier_address': device_data[0],
                'device_id': device_id,
                'device_public_key': device_data[2],
                'metadata': device_data[3],
                'is_active': device_data[4],
                'registration_timestamp': device_data[5]
            }
        except Exception as e:
            logger.error(f"Failed to get device info: {str(e)}")
            return None
    
    # Data Submission Functions
    
    def submit_data(self, device_id: str, data_hash: str, signature: str, 
                   data_uri: str, metadata: str = "") -> Dict[str, Any]:
        """
        Submit data to the Physical Verification Blockchain.
        
        Args:
            device_id: ID of the submitting device
            data_hash: Cryptographic hash of the data
            signature: Digital signature of the data hash
            data_uri: URI to off-chain data storage
            metadata: Additional submission metadata
            
        Returns:
            Submission result with transaction details
        """
        if not self.submission_contract or not self.account:
            raise ValueError("Submission contract or account not initialized")
        
        try:
            device_id_bytes32 = convert_device_id_to_bytes32(device_id)
            data_hash_bytes32 = convert_data_hash_to_bytes32(data_hash)
            
            function = self.submission_contract.functions.submitData(
                device_id_bytes32, data_hash_bytes32, signature, data_uri, metadata
            )
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': 300000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Data submitted: {data_hash}, tx: {tx_hash.hex()}")
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'data_hash': data_hash
            }
            
        except Exception as e:
            logger.error(f"Failed to submit data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_submission(self, data_hash: str) -> Optional[Dict[str, Any]]:
        """
        Verify a data submission on the blockchain.
        
        Args:
            data_hash: Hash of the data to verify
            
        Returns:
            Submission details if found, None otherwise
        """
        if not self.submission_contract:
            raise ValueError("Submission contract not initialized")
        
        try:
            data_hash_bytes32 = convert_data_hash_to_bytes32(data_hash)
            submission_data = self.submission_contract.functions.verifySubmission(data_hash_bytes32).call()
            
            return {
                'device_id': submission_data[0].hex(),  # Convert bytes32 back to hex
                'verifier_address': submission_data[1],
                'data_hash': data_hash,
                'signature': submission_data[3],
                'timestamp': submission_data[4],
                'data_uri': submission_data[5],
                'metadata': submission_data[6],
                'is_verified': submission_data[7],
                'block_number': submission_data[8]
            }
            
        except Exception as e:
            logger.error(f"Failed to verify submission: {str(e)}")
            return None
    
    def get_submission_details(self, data_hash: str) -> Optional[Dict[str, Any]]:
        """Get complete submission details including chain of custody."""
        if not self.submission_contract:
            raise ValueError("Submission contract not initialized")
        
        try:
            data_hash_bytes32 = convert_data_hash_to_bytes32(data_hash)
            result = self.submission_contract.functions.getSubmissionDetails(data_hash_bytes32).call()
            
            submission, device, verifier = result
            
            return {
                'submission': {
                    'device_id': submission[0].hex(),
                    'verifier_address': submission[1],
                    'data_hash': data_hash,
                    'signature': submission[3],
                    'timestamp': submission[4],
                    'data_uri': submission[5],
                    'metadata': submission[6],
                    'is_verified': submission[7],
                    'block_number': submission[8]
                },
                'device': {
                    'verifier_address': device[0],
                    'device_id': device[1].hex(),
                    'device_public_key': device[2],
                    'metadata': device[3],
                    'is_active': device[4],
                    'registration_timestamp': device[5]
                },
                'verifier': {
                    'name': verifier[0],
                    'owner': verifier[1],
                    'is_active': verifier[2],
                    'registration_timestamp': verifier[3],
                    'metadata': verifier[4]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get submission details: {str(e)}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on blockchain connectivity and contracts."""
        health_status = {
            'blockchain_connected': False,
            'registry_contract_accessible': False,
            'submission_contract_accessible': False,
            'current_block': None,
            'account_balance': None,
            'timestamp': datetime.utcnow()
        }
        
        try:
            # Check blockchain connection
            health_status['blockchain_connected'] = self.is_connected()
            if health_status['blockchain_connected']:
                health_status['current_block'] = self.get_block_number()
                
                if self.account:
                    health_status['account_balance'] = self.get_account_balance()
            
            # Check registry contract
            if self.registry_contract:
                try:
                    # Try a simple read operation
                    self.registry_contract.functions.openRegistration().call()
                    health_status['registry_contract_accessible'] = True
                except Exception:
                    pass
            
            # Check submission contract
            if self.submission_contract:
                try:
                    # Try a simple read operation
                    self.submission_contract.functions.totalSubmissions().call()
                    health_status['submission_contract_accessible'] = True
                except Exception:
                    pass
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
        
        return health_status
    
    def _get_registry_abi(self) -> List[Dict]:
        """Get the ABI for TrustedVerifierRegistry contract."""
        # Simplified ABI - in production, load from compiled contract artifacts
        return [
            {
                "inputs": [{"name": "_name", "type": "string"}, {"name": "_metadata", "type": "string"}],
                "name": "registerVerifier",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "_deviceId", "type": "bytes32"},
                    {"name": "_devicePublicKey", "type": "string"},
                    {"name": "_metadata", "type": "string"}
                ],
                "name": "addDevice",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "_deviceId", "type": "bytes32"}],
                "name": "isDeviceActive",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "_deviceId", "type": "bytes32"}],
                "name": "getDevice",
                "outputs": [
                    {"name": "verifierAddress", "type": "address"},
                    {"name": "deviceId", "type": "bytes32"},
                    {"name": "devicePublicKey", "type": "string"},
                    {"name": "metadata", "type": "string"},
                    {"name": "isActive", "type": "bool"},
                    {"name": "registrationTimestamp", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "openRegistration",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def _get_submission_abi(self) -> List[Dict]:
        """Get the ABI for DataSubmission contract."""
        # Simplified ABI - in production, load from compiled contract artifacts
        return [
            {
                "inputs": [
                    {"name": "_deviceId", "type": "bytes32"},
                    {"name": "_dataHash", "type": "bytes32"},
                    {"name": "_signature", "type": "string"},
                    {"name": "_dataUri", "type": "string"},
                    {"name": "_metadata", "type": "string"}
                ],
                "name": "submitData",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "_dataHash", "type": "bytes32"}],
                "name": "verifySubmission",
                "outputs": [
                    {"name": "deviceId", "type": "bytes32"},
                    {"name": "verifierAddress", "type": "address"},
                    {"name": "dataHash", "type": "bytes32"},
                    {"name": "signature", "type": "string"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "dataUri", "type": "string"},
                    {"name": "metadata", "type": "string"},
                    {"name": "isVerified", "type": "bool"},
                    {"name": "blockNumber", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "_dataHash", "type": "bytes32"}],
                "name": "getSubmissionDetails",
                "outputs": [
                    {"name": "submission", "type": "tuple"},
                    {"name": "device", "type": "tuple"},
                    {"name": "verifier", "type": "tuple"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "totalSubmissions",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]


# Global instance for the application
pvb_blockchain = None

def get_blockchain_interface() -> PVBBlockchainInterface:
    """Get or create the global blockchain interface instance."""
    global pvb_blockchain
    if pvb_blockchain is None:
        pvb_blockchain = PVBBlockchainInterface()
    return pvb_blockchain

def initialize_blockchain_interface(**kwargs) -> PVBBlockchainInterface:
    """Initialize the global blockchain interface with custom parameters."""
    global pvb_blockchain
    pvb_blockchain = PVBBlockchainInterface(**kwargs)
    return pvb_blockchain 