"""
Blockchain Network Simulation

Provides networking utilities for the Ethical Ontology Blockchain.
In a real deployment, this would handle peer-to-peer communication.
For MVP, this simulates network operations locally.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional
from .core import EthicalOntologyBlockchain, Block, Transaction

logger = logging.getLogger(__name__)

class BlockchainNetwork:
    """
    Simulates a blockchain network for local development.
    
    In production, this would handle distributed consensus,
    peer discovery, and message propagation.
    """
    
    def __init__(self, network_id: str = "ethical-ontology-local"):
        self.network_id = network_id
        self.nodes: Dict[str, EthicalOntologyBlockchain] = {}
        self.is_running = False
        
    def add_node(self, node_id: str, blockchain: EthicalOntologyBlockchain):
        """Add a blockchain node to the network."""
        self.nodes[node_id] = blockchain
        logger.info(f"Added node {node_id} to network {self.network_id}")
    
    def remove_node(self, node_id: str):
        """Remove a node from the network."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            logger.info(f"Removed node {node_id} from network")
    
    def get_node(self, node_id: str) -> Optional[EthicalOntologyBlockchain]:
        """Get a specific node by ID."""
        return self.nodes.get(node_id)
    
    def broadcast_transaction(self, transaction: Transaction):
        """Broadcast a transaction to all nodes in the network."""
        logger.debug(f"Broadcasting transaction {transaction.transaction_id}")
        for node_id, blockchain in self.nodes.items():
            try:
                blockchain.add_transaction(transaction)
                logger.debug(f"Transaction sent to node {node_id}")
            except Exception as e:
                logger.error(f"Failed to send transaction to node {node_id}: {e}")
    
    def sync_nodes(self):
        """
        Synchronize all nodes to have the same blockchain state.
        
        In reality, this would involve complex consensus mechanisms.
        For simulation, we use the longest valid chain rule.
        """
        if not self.nodes:
            return
        
        # Find the longest valid chain
        longest_chain = None
        longest_length = 0
        
        for node_id, blockchain in self.nodes.items():
            if blockchain.is_chain_valid() and blockchain.get_chain_length() > longest_length:
                longest_chain = blockchain.chain
                longest_length = blockchain.get_chain_length()
        
        if longest_chain:
            # Update all nodes with the longest chain
            for node_id, blockchain in self.nodes.items():
                if blockchain.get_chain_length() < longest_length:
                    blockchain.chain = longest_chain.copy()
                    logger.info(f"Synchronized node {node_id} with longest chain")
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get the current status of the network."""
        status = {
            "network_id": self.network_id,
            "total_nodes": len(self.nodes),
            "is_running": self.is_running,
            "nodes": {}
        }
        
        for node_id, blockchain in self.nodes.items():
            status["nodes"][node_id] = {
                "chain_length": blockchain.get_chain_length(),
                "pending_transactions": len(blockchain.pending_transactions),
                "contracts": len(blockchain.smart_contracts),
                "is_valid": blockchain.is_chain_valid()
            }
        
        return status
    
    def start_network(self):
        """Start the blockchain network simulation."""
        self.is_running = True
        logger.info(f"Started network {self.network_id}")
    
    def stop_network(self):
        """Stop the blockchain network simulation."""
        self.is_running = False
        logger.info(f"Stopped network {self.network_id}")
    
    def get_consensus_result(self, contract_address: str, method: str, 
                           parameters: Dict[str, Any]) -> Any:
        """
        Get consensus result from multiple nodes for a contract call.
        
        This simulates how the network would reach consensus on ethical decisions.
        """
        results = []
        
        for node_id, blockchain in self.nodes.items():
            try:
                result = blockchain.call_contract(contract_address, method, parameters)
                results.append(result)
                logger.debug(f"Node {node_id} returned: {result}")
            except Exception as e:
                logger.error(f"Node {node_id} failed: {e}")
        
        if not results:
            raise RuntimeError("No nodes could process the request")
        
        # Simple majority consensus for boolean results
        if all(isinstance(r, bool) for r in results):
            true_count = sum(results)
            return true_count > len(results) / 2
        
        # For other types, return the most common result
        from collections import Counter
        counter = Counter(results)
        most_common = counter.most_common(1)[0][0]
        
        logger.info(f"Consensus result: {most_common} (from {len(results)} nodes)")
        return most_common 