"""
Pydantic schemas for Physical Verification Blockchain (PVB) data models.
These schemas define the structure and validation for DSM output, verifier registration,
and data submission in the PVB system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import hashlib
import re


class DSMOutputSchema(BaseModel):
    """
    Schema for Device Security Module (DSM) output data structure.
    This defines the expected format for data packages from DSMs.
    """
    device_id: str = Field(..., description="Unique identifier for the DSM")
    data_hash: str = Field(..., description="Cryptographic hash (SHA-256) of the media/data")
    signature: str = Field(..., description="Digital signature of dataHash using DSM's private key")
    timestamp: datetime = Field(..., description="Timestamp of data capture/signing")
    data_uri: str = Field(..., description="URI pointing to off-chain storage (IPFS, Arweave, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    @validator('device_id')
    def validate_device_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Device ID cannot be empty')
        if len(v) > 64:
            raise ValueError('Device ID too long (max 64 characters)')
        return v.strip()

    @validator('data_hash')
    def validate_data_hash(cls, v):
        # Validate SHA-256 hash format (64 hex characters)
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError('Data hash must be a valid SHA-256 hash (64 hex characters)')
        return v.lower()

    @validator('signature')
    def validate_signature(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Signature cannot be empty')
        return v.strip()

    @validator('data_uri')
    def validate_data_uri(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Data URI cannot be empty')
        # Basic URI validation
        if not (v.startswith('http://') or v.startswith('https://') or 
                v.startswith('ipfs://') or v.startswith('ar://')):
            raise ValueError('Data URI must use supported protocol (http, https, ipfs, ar)')
        return v.strip()


class VerifierRegistrationSchema(BaseModel):
    """Schema for Trusted Verifier registration requests."""
    name: str = Field(..., description="Name of the verifier organization/entity")
    metadata: Optional[str] = Field(default="", description="Additional metadata about the verifier")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Verifier name cannot be empty')
        if len(v) > 100:
            raise ValueError('Verifier name too long (max 100 characters)')
        return v.strip()


class DeviceRegistrationSchema(BaseModel):
    """Schema for Device Security Module registration by Trusted Verifiers."""
    device_id: str = Field(..., description="Unique identifier for the device")
    device_public_key: str = Field(..., description="Public key of the device for signature verification")
    metadata: Optional[str] = Field(default="", description="Additional metadata about the device")
    
    @validator('device_id')
    def validate_device_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Device ID cannot be empty')
        if len(v) > 64:
            raise ValueError('Device ID too long (max 64 characters)')
        return v.strip()
    
    @validator('device_public_key')
    def validate_public_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Device public key cannot be empty')
        return v.strip()


class DataSubmissionSchema(BaseModel):
    """Schema for data submission to the PVB."""
    device_id: str = Field(..., description="Device ID of the submitting DSM")
    data_hash: str = Field(..., description="Cryptographic hash of the data")
    signature: str = Field(..., description="Digital signature of the data hash")
    data_uri: str = Field(..., description="URI to the off-chain data storage")
    metadata: Optional[str] = Field(default="", description="Additional submission metadata")
    
    @validator('device_id')
    def validate_device_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Device ID cannot be empty')
        return v.strip()
    
    @validator('data_hash')
    def validate_data_hash(cls, v):
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError('Data hash must be a valid SHA-256 hash (64 hex characters)')
        return v.lower()
    
    @validator('signature')
    def validate_signature(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Signature cannot be empty')
        return v.strip()
    
    @validator('data_uri')
    def validate_data_uri(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Data URI cannot be empty')
        return v.strip()


class VerificationRequestSchema(BaseModel):
    """Schema for data verification requests."""
    data_hash: str = Field(..., description="Hash of the data to verify")
    provided_data: Optional[bytes] = Field(default=None, description="Optional: actual data for integrity check")
    
    @validator('data_hash')
    def validate_data_hash(cls, v):
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError('Data hash must be a valid SHA-256 hash (64 hex characters)')
        return v.lower()


class SubmissionResponseSchema(BaseModel):
    """Response schema for data submissions."""
    success: bool = Field(..., description="Whether the submission was successful")
    transaction_hash: Optional[str] = Field(default=None, description="Blockchain transaction hash")
    data_hash: str = Field(..., description="Hash of the submitted data")
    timestamp: datetime = Field(..., description="Timestamp of the submission")
    block_number: Optional[int] = Field(default=None, description="Block number where the transaction was mined")
    message: Optional[str] = Field(default=None, description="Additional message or error details")


class VerificationResponseSchema(BaseModel):
    """Response schema for verification requests."""
    data_hash: str = Field(..., description="Hash of the verified data")
    is_verified: bool = Field(..., description="Whether the submission is verified")
    device_id: Optional[str] = Field(default=None, description="Device ID that submitted the data")
    verifier_address: Optional[str] = Field(default=None, description="Address of the trusted verifier")
    timestamp: Optional[datetime] = Field(default=None, description="Timestamp of original submission")
    data_uri: Optional[str] = Field(default=None, description="URI to the off-chain data")
    metadata: Optional[str] = Field(default=None, description="Submission metadata")
    block_number: Optional[int] = Field(default=None, description="Block number of the submission")
    integrity_check: Optional[bool] = Field(default=None, description="Result of data integrity check if performed")


class DeviceInfoSchema(BaseModel):
    """Schema for device information responses."""
    device_id: str = Field(..., description="Device identifier")
    verifier_address: str = Field(..., description="Address of the verifier that registered this device")
    device_public_key: str = Field(..., description="Public key of the device")
    metadata: str = Field(..., description="Device metadata")
    is_active: bool = Field(..., description="Whether the device is currently active")
    registration_timestamp: int = Field(..., description="Unix timestamp of device registration")


class VerifierInfoSchema(BaseModel):
    """Schema for verifier information responses."""
    verifier_address: str = Field(..., description="Ethereum address of the verifier")
    name: str = Field(..., description="Name of the verifier")
    is_active: bool = Field(..., description="Whether the verifier is currently active")
    registration_timestamp: int = Field(..., description="Unix timestamp of verifier registration")
    metadata: str = Field(..., description="Verifier metadata")
    registered_devices: List[str] = Field(..., description="List of device IDs registered by this verifier")


class AuditTrailSchema(BaseModel):
    """Schema for audit trail responses."""
    submission_count: int = Field(..., description="Total number of submissions")
    submissions: List[Dict[str, Any]] = Field(..., description="List of submission details")
    start_index: int = Field(..., description="Starting index of the returned results")
    returned_count: int = Field(..., description="Number of results returned")


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    timestamp: datetime = Field(..., description="Timestamp of the error")
    request_id: Optional[str] = Field(default=None, description="Request identifier for tracking")


class HealthCheckSchema(BaseModel):
    """Schema for health check responses."""
    status: str = Field(..., description="Service status")
    blockchain_connected: bool = Field(..., description="Whether blockchain connection is healthy")
    registry_contract_accessible: bool = Field(..., description="Whether registry contract is accessible")
    submission_contract_accessible: bool = Field(..., description="Whether submission contract is accessible")
    timestamp: datetime = Field(..., description="Health check timestamp")


def hash_data(data: bytes) -> str:
    """
    Utility function to generate SHA-256 hash of data.
    
    Args:
        data (bytes): Data to hash
        
    Returns:
        str: Hexadecimal representation of the SHA-256 hash
    """
    return hashlib.sha256(data).hexdigest()


def convert_device_id_to_bytes32(device_id: str) -> bytes:
    """
    Convert device ID string to bytes32 format for smart contract interaction.
    
    Args:
        device_id (str): Device identifier string
        
    Returns:
        bytes: 32-byte representation of the device ID
    """
    # Hash the device ID to create a consistent 32-byte value
    return hashlib.sha256(device_id.encode('utf-8')).digest()


def convert_data_hash_to_bytes32(data_hash: str) -> bytes:
    """
    Convert hex string hash to bytes32 format for smart contract interaction.
    
    Args:
        data_hash (str): Hexadecimal hash string
        
    Returns:
        bytes: 32-byte representation of the hash
    """
    return bytes.fromhex(data_hash) 