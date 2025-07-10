"""
Network Configuration for Ethical Ontology Blockchain

Defines network settings, node configurations, and connection parameters.
Aligns with paper's requirements for local blockchain simulation.
"""

import os
import logging
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class NodeConfig:
    """Configuration for a single blockchain node."""
    node_id: str
    host: str = "localhost"
    port: int = 8545
    is_validator: bool = False
    max_connections: int = 10
    mining_enabled: bool = True
    
@dataclass
class NetworkConfig:
    """Configuration for the entire blockchain network."""
    network_id: str = "ethical-ontology-local"
    network_name: str = "Ethical Ontology Blockchain"
    consensus_algorithm: str = "proof_of_work"  # For simulation
    block_time_seconds: int = 10
    max_block_size: int = 1000000  # 1MB
    max_transactions_per_block: int = 100
    difficulty_adjustment_interval: int = 10  # blocks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

class EthicalOntologyNetworkConfig:
    """
    Main configuration manager for the Ethical Ontology Blockchain network.
    
    Handles environment-based configuration and provides defaults for local development.
    """
    
    def __init__(self, env_prefix: str = "ETHICAL_ONTOLOGY"):
        self.env_prefix = env_prefix
        self._network_config = None
        self._nodes = {}
        
        # Load configuration from environment or defaults
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables or use defaults."""
        
        # Network configuration
        self._network_config = NetworkConfig(
            network_id=self._get_env("NETWORK_ID", "ethical-ontology-local"),
            network_name=self._get_env("NETWORK_NAME", "Ethical Ontology Blockchain"),
            consensus_algorithm=self._get_env("CONSENSUS_ALGORITHM", "proof_of_work"),
            block_time_seconds=int(self._get_env("BLOCK_TIME_SECONDS", "10")),
            max_block_size=int(self._get_env("MAX_BLOCK_SIZE", "1000000")),
            max_transactions_per_block=int(self._get_env("MAX_TRANSACTIONS_PER_BLOCK", "100")),
            difficulty_adjustment_interval=int(self._get_env("DIFFICULTY_ADJUSTMENT_INTERVAL", "10"))
        )
        
        # Default node configurations for local development
        self._setup_default_nodes()
        
        logger.info(f"Loaded network configuration: {self._network_config.network_name}")
    
    def _get_env(self, key: str, default: str) -> str:
        """Get environment variable with prefix."""
        full_key = f"{self.env_prefix}_{key}"
        return os.getenv(full_key, default)
    
    def _setup_default_nodes(self):
        """Setup default node configurations for local testing."""
        
        # Main validator node
        self._nodes["validator_1"] = NodeConfig(
            node_id="validator_1",
            host="localhost",
            port=8545,
            is_validator=True,
            max_connections=20,
            mining_enabled=True
        )
        
        # Peer nodes for testing consensus
        self._nodes["peer_1"] = NodeConfig(
            node_id="peer_1",
            host="localhost", 
            port=8546,
            is_validator=True,
            max_connections=10,
            mining_enabled=True
        )
        
        self._nodes["peer_2"] = NodeConfig(
            node_id="peer_2",
            host="localhost",
            port=8547,
            is_validator=True,
            max_connections=10,
            mining_enabled=True
        )
        
        # Observer node (doesn't mine)
        self._nodes["observer_1"] = NodeConfig(
            node_id="observer_1",
            host="localhost",
            port=8548,
            is_validator=False,
            max_connections=5,
            mining_enabled=False
        )
    
    def get_network_config(self) -> NetworkConfig:
        """Get the network configuration."""
        return self._network_config
    
    def get_node_config(self, node_id: str) -> NodeConfig:
        """Get configuration for a specific node."""
        if node_id not in self._nodes:
            raise ValueError(f"Node {node_id} not found in configuration")
        return self._nodes[node_id]
    
    def get_all_nodes(self) -> Dict[str, NodeConfig]:
        """Get configurations for all nodes."""
        return self._nodes.copy()
    
    def get_validator_nodes(self) -> Dict[str, NodeConfig]:
        """Get configurations for validator nodes only."""
        return {
            node_id: config 
            for node_id, config in self._nodes.items() 
            if config.is_validator
        }
    
    def add_node(self, node_config: NodeConfig):
        """Add a new node configuration."""
        self._nodes[node_config.node_id] = node_config
        logger.info(f"Added node configuration: {node_config.node_id}")
    
    def remove_node(self, node_id: str):
        """Remove a node configuration."""
        if node_id in self._nodes:
            del self._nodes[node_id]
            logger.info(f"Removed node configuration: {node_id}")
    
    def get_docker_compose_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate Docker Compose service definitions for all nodes.
        
        This enables easy deployment of the blockchain network with Docker.
        """
        services = {}
        
        for node_id, node_config in self._nodes.items():
            service_name = f"ethical-ontology-{node_id.replace('_', '-')}"
            
            services[service_name] = {
                "build": {
                    "context": ".",
                    "dockerfile": "ethical_ontology/Dockerfile"
                },
                "ports": [f"{node_config.port}:{node_config.port}"],
                "environment": [
                    f"NODE_ID={node_config.node_id}",
                    f"NODE_PORT={node_config.port}",
                    f"IS_VALIDATOR={str(node_config.is_validator).lower()}",
                    f"MINING_ENABLED={str(node_config.mining_enabled).lower()}",
                    f"NETWORK_ID={self._network_config.network_id}",
                    f"MAX_CONNECTIONS={node_config.max_connections}"
                ],
                "volumes": [
                    f"./ethical_ontology:/app/ethical_ontology",
                    f"{node_id}_data:/app/data"
                ],
                "networks": ["ethical-ontology-network"],
                "depends_on": ["ethical-ontology-init"] if node_id != "validator_1" else [],
                "healthcheck": {
                    "test": [f"curl -f http://localhost:{node_config.port}/health || exit 1"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            }
        
        # Add network definition
        services["_networks"] = {
            "ethical-ontology-network": {
                "driver": "bridge",
                "name": "ethical-ontology-network"
            }
        }
        
        # Add volume definitions
        services["_volumes"] = {
            f"{node_id}_data": {} for node_id in self._nodes.keys()
        }
        
        return services
    
    def get_connection_string(self, node_id: str) -> str:
        """Get connection string for a specific node."""
        node_config = self.get_node_config(node_id)
        return f"http://{node_config.host}:{node_config.port}"
    
    def validate_configuration(self) -> List[str]:
        """Validate the network configuration and return any issues."""
        issues = []
        
        # Check for port conflicts
        ports_used = set()
        for node_id, config in self._nodes.items():
            if config.port in ports_used:
                issues.append(f"Port conflict: {config.port} used by multiple nodes")
            ports_used.add(config.port)
        
        # Ensure at least one validator
        validators = [n for n in self._nodes.values() if n.is_validator]
        if not validators:
            issues.append("No validator nodes configured")
        
        # Check environment variables are properly formatted
        if not self._network_config.network_id.replace("-", "").replace("_", "").isalnum():
            issues.append("Network ID contains invalid characters")
        
        if self._network_config.block_time_seconds < 1:
            issues.append("Block time must be at least 1 second")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire configuration to dictionary."""
        return {
            "network": self._network_config.to_dict(),
            "nodes": {
                node_id: asdict(config) 
                for node_id, config in self._nodes.items()
            }
        } 