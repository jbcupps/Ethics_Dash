"""
Core Blockchain Implementation for Ethical Ontology

This module implements a simplified blockchain to store and verify ethical principles.
Aligns with paper's Command: Deontological Smart Contracts and virtue-based reputation.
"""

import hashlib
import json
import time
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    """
    Represents a blockchain transaction containing ethical evaluation data.
    
    Aligns with paper's requirement for immutable ethical record keeping.
    """
    transaction_id: str
    timestamp: float
    sender: str
    contract_address: str
    method: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    gas_used: int = 0
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for JSON serialization."""
        return asdict(self)
    
    def get_hash(self) -> str:
        """Generate a hash of the transaction data."""
        # Exclude signature from hash calculation
        data = self.to_dict()
        if 'signature' in data:
            del data['signature']
        
        transaction_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

@dataclass 
class Block:
    """
    Represents a block in the Ethical Ontology Blockchain.
    
    Contains ethical transactions and maintains chain integrity.
    """
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: Optional[str] = None
    merkle_root: Optional[str] = None
    
    def __post_init__(self):
        """Calculate merkle root and block hash after initialization."""
        if self.merkle_root is None:
            self.merkle_root = self.calculate_merkle_root()
        if self.hash is None:
            self.hash = self.calculate_hash()
    
    def calculate_merkle_root(self) -> str:
        """Calculate the Merkle root of all transactions in the block."""
        if not self.transactions:
            return hashlib.sha256(b"").hexdigest()
        
        # Get transaction hashes
        tx_hashes = [tx.get_hash() for tx in self.transactions]
        
        # Build Merkle tree
        while len(tx_hashes) > 1:
            next_level = []
            for i in range(0, len(tx_hashes), 2):
                if i + 1 < len(tx_hashes):
                    combined = tx_hashes[i] + tx_hashes[i + 1]
                else:
                    combined = tx_hashes[i] + tx_hashes[i]  # Duplicate if odd number
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            tx_hashes = next_level
        
        return tx_hashes[0]
    
    def calculate_hash(self) -> str:
        """Calculate the hash of the entire block."""
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary for JSON serialization."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "merkle_root": self.merkle_root
        }

class EthicalOntologyBlockchain:
    """
    Main blockchain class for the Ethical Ontology system.
    
    Implements a simplified permissioned ledger for ethical smart contracts.
    Aligns with paper's dual-blockchain architecture requirements.
    """
    
    def __init__(self, network_id: str = "ethical-ontology-local"):
        self.network_id = network_id
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.smart_contracts: Dict[str, Any] = {}
        self.validators: List[str] = []  # Permissioned validator addresses
        self.difficulty = 2  # Simple proof-of-work difficulty for simulation
        
        # Create genesis block
        self._create_genesis_block()
        
        logger.info(f"Initialized Ethical Ontology Blockchain (Network: {network_id})")
    
    def _create_genesis_block(self):
        """Create the first block in the blockchain."""
        genesis_transaction = Transaction(
            transaction_id="genesis",
            timestamp=time.time(),
            sender="system",
            contract_address="genesis",
            method="init",
            parameters={"message": "Ethical Ontology Blockchain Genesis"},
            result="initialized"
        )
        
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[genesis_transaction],
            previous_hash="0" * 64,
            nonce=0
        )
        
        self.chain.append(genesis_block)
        logger.info("Genesis block created")
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a transaction to the pending transaction pool."""
        try:
            # Validate transaction
            if not self._validate_transaction(transaction):
                logger.error(f"Invalid transaction: {transaction.transaction_id}")
                return False
            
            self.pending_transactions.append(transaction)
            logger.debug(f"Added transaction to pool: {transaction.transaction_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            return False
    
    def _validate_transaction(self, transaction: Transaction) -> bool:
        """Validate a transaction before adding to the pool."""
        # Basic validation
        if not transaction.transaction_id or not transaction.sender:
            return False
        
        # Check if contract exists for contract calls
        if (transaction.contract_address != "genesis" and 
            transaction.contract_address not in self.smart_contracts):
            logger.warning(f"Contract not found: {transaction.contract_address}")
            # Allow for now, contracts might be deployed later
        
        return True
    
    def mine_block(self, miner_address: str) -> Optional[Block]:
        """
        Mine a new block with pending transactions.
        
        In a real implementation, this would involve consensus mechanisms.
        For MVP, we use simple proof-of-work simulation.
        """
        if not self.pending_transactions:
            logger.info("No pending transactions to mine")
            return None
        
        try:
            # Get previous block
            previous_block = self.chain[-1]
            
            # Create new block
            new_block = Block(
                index=len(self.chain),
                timestamp=time.time(),
                transactions=self.pending_transactions.copy(),
                previous_hash=previous_block.hash
            )
            
            # Simple proof-of-work (for simulation only)
            target = "0" * self.difficulty
            while not new_block.hash.startswith(target):
                new_block.nonce += 1
                new_block.hash = new_block.calculate_hash()
            
            # Add block to chain
            self.chain.append(new_block)
            
            # Clear pending transactions
            self.pending_transactions = []
            
            logger.info(f"Mined block {new_block.index} with {len(new_block.transactions)} transactions")
            return new_block
            
        except Exception as e:
            logger.error(f"Error mining block: {e}")
            return None
    
    def deploy_contract(self, contract_name: str, contract_instance: Any) -> str:
        """Deploy a smart contract to the blockchain."""
        contract_address = f"0x{hashlib.sha256(contract_name.encode()).hexdigest()[:40]}"
        self.smart_contracts[contract_address] = contract_instance
        
        # Create deployment transaction
        deploy_tx = Transaction(
            transaction_id=f"deploy_{contract_name}_{int(time.time())}",
            timestamp=time.time(),
            sender="system",
            contract_address=contract_address,
            method="deploy",
            parameters={"contract_name": contract_name},
            result="deployed"
        )
        
        self.add_transaction(deploy_tx)
        
        logger.info(f"Deployed contract '{contract_name}' at address {contract_address}")
        return contract_address
    
    def call_contract(self, contract_address: str, method: str, parameters: Dict[str, Any], 
                     sender: str = "system") -> Any:
        """
        Call a method on a deployed smart contract.
        
        This is the main interface for ethical rule verification.
        """
        if contract_address not in self.smart_contracts:
            raise ValueError(f"Contract not found at address: {contract_address}")
        
        contract = self.smart_contracts[contract_address]
        
        try:
            # Call the method on the contract
            if hasattr(contract, method):
                result = getattr(contract, method)(**parameters)
            else:
                raise AttributeError(f"Method '{method}' not found in contract")
            
            # Create transaction record
            tx = Transaction(
                transaction_id=f"call_{int(time.time() * 1000)}_{sender}",
                timestamp=time.time(),
                sender=sender,
                contract_address=contract_address,
                method=method,
                parameters=parameters,
                result=result
            )
            
            # Add to pending transactions
            self.add_transaction(tx)
            
            logger.debug(f"Contract call: {method} -> {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error calling contract method {method}: {e}")
            raise
    
    def get_block(self, index: int) -> Optional[Block]:
        """Get a block by its index."""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1]
    
    def get_chain_length(self) -> int:
        """Get the number of blocks in the chain."""
        return len(self.chain)
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block hash is valid
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"Invalid hash for block {i}")
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Invalid previous hash for block {i}")
                return False
        
        return True
    
    def get_contract_history(self, contract_address: str) -> List[Transaction]:
        """Get all transactions for a specific contract."""
        history = []
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.contract_address == contract_address:
                    history.append(transaction)
        return history
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert blockchain to dictionary for JSON serialization."""
        return {
            "network_id": self.network_id,
            "chain_length": len(self.chain),
            "blocks": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
            "contracts": list(self.smart_contracts.keys())
        } 