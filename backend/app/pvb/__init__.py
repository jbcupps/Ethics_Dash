"""
Physical Verification Blockchain (PVB) Module

This module implements a cryptographically secure chain of custody system for media and data.
It consists of three main components:

1. Device Security Modules (DSMs): Software/hardware on capturing devices that sign data at the source
2. Trusted Verifiers (TVs): Entities that vet and register DSMs
3. Physical Verification Blockchain (PVB): Stores immutable records of submitted data

The system is designed to maximize AI and human freedom of choice and promote voluntary consensus.
"""

from .api import pvb_api_bp, register_pvb_api
from .blockchain_interface import PVBBlockchainInterface, get_blockchain_interface
from .schemas import (
    DSMOutputSchema,
    VerifierRegistrationSchema,
    DeviceRegistrationSchema,
    DataSubmissionSchema,
    VerificationRequestSchema,
    SubmissionResponseSchema,
    VerificationResponseSchema,
    ErrorResponseSchema,
    HealthCheckSchema,
    hash_data,
    convert_device_id_to_bytes32,
    convert_data_hash_to_bytes32
)

__version__ = "1.0.0"
__author__ = "Ethics Dashboard Team"
__description__ = "Physical Verification Blockchain for cryptographically secure chain of custody"

# Module exports
__all__ = [
    # API components
    'pvb_api_bp',
    'register_pvb_api',
    
    # Blockchain interface
    'PVBBlockchainInterface',
    'get_blockchain_interface',
    
    # Schemas
    'DSMOutputSchema',
    'VerifierRegistrationSchema',
    'DeviceRegistrationSchema',
    'DataSubmissionSchema',
    'VerificationRequestSchema',
    'SubmissionResponseSchema',
    'VerificationResponseSchema',
    'ErrorResponseSchema',
    'HealthCheckSchema',
    
    # Utility functions
    'hash_data',
    'convert_device_id_to_bytes32',
    'convert_data_hash_to_bytes32',
] 