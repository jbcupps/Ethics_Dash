"""
Flask API endpoints for Physical Verification Blockchain (PVB) system.
Provides REST API for verifier registration, device management, and data submission/verification.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
import traceback

from .schemas import (
    VerifierRegistrationSchema,
    DeviceRegistrationSchema,
    DataSubmissionSchema,
    VerificationRequestSchema,
    SubmissionResponseSchema,
    VerificationResponseSchema,
    ErrorResponseSchema,
    HealthCheckSchema,
    DSMOutputSchema
)
from .blockchain_interface import get_blockchain_interface, PVBBlockchainInterface

# Configure logging
logger = logging.getLogger(__name__)

# Create Flask Blueprint for PVB API
pvb_api_bp = Blueprint('pvb_api', __name__, url_prefix='/api/pvb')

def handle_error(error_type: str, message: str, status_code: int = 400) -> tuple:
    """
    Standardized error handling for PVB API endpoints.
    
    Args:
        error_type: Type of error (e.g., 'ValidationError', 'BlockchainError')
        message: Detailed error message
        status_code: HTTP status code
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    error_response = ErrorResponseSchema(
        error=error_type,
        message=message,
        timestamp=datetime.utcnow()
    )
    
    logger.error(f"{error_type}: {message}")
    return error_response.dict(), status_code

def get_blockchain() -> PVBBlockchainInterface:
    """Get blockchain interface instance with error handling."""
    try:
        blockchain = get_blockchain_interface()
        if not blockchain.is_connected():
            raise ConnectionError("Blockchain connection is not available")
        return blockchain
    except Exception as e:
        raise ConnectionError(f"Failed to connect to blockchain: {str(e)}")

# Health Check Endpoint
@pvb_api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for PVB system.
    Returns the status of blockchain connectivity and contract accessibility.
    """
    try:
        blockchain = get_blockchain_interface()
        health_data = blockchain.health_check()
        
        # Determine overall status
        overall_status = "healthy" if (
            health_data['blockchain_connected'] and
            health_data['registry_contract_accessible'] and
            health_data['submission_contract_accessible']
        ) else "degraded"
        
        response = HealthCheckSchema(
            status=overall_status,
            blockchain_connected=health_data['blockchain_connected'],
            registry_contract_accessible=health_data['registry_contract_accessible'],
            submission_contract_accessible=health_data['submission_contract_accessible'],
            timestamp=datetime.utcnow()
        )
        
        status_code = 200 if overall_status == "healthy" else 503
        return response.dict(), status_code
        
    except Exception as e:
        return handle_error("HealthCheckError", str(e), 503)

# Trusted Verifier Management Endpoints

@pvb_api_bp.route('/verifiers', methods=['POST'])
def register_verifier():
    """
    Register a new Trusted Verifier.
    
    Expected JSON payload:
    {
        "name": "Verifier Organization Name",
        "metadata": "Optional metadata about the verifier"
    }
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return handle_error("ValidationError", "Request body is required", 400)
        
        verifier_data = VerifierRegistrationSchema(**data)
        
        # Get blockchain interface
        blockchain = get_blockchain()
        
        # Register verifier on blockchain
        result = blockchain.register_verifier(
            name=verifier_data.name,
            metadata=verifier_data.metadata or ""
        )
        
        if result['success']:
            response = {
                'success': True,
                'message': 'Verifier registered successfully',
                'transaction_hash': result['transaction_hash'],
                'block_number': result['block_number'],
                'verifier_address': result['verifier_address'],
                'timestamp': datetime.utcnow()
            }
            return response, 201
        else:
            return handle_error("BlockchainError", result['error'], 500)
            
    except ValidationError as e:
        return handle_error("ValidationError", str(e), 400)
    except ConnectionError as e:
        return handle_error("ConnectionError", str(e), 503)
    except Exception as e:
        logger.error(f"Unexpected error in register_verifier: {traceback.format_exc()}")
        return handle_error("InternalError", "An unexpected error occurred", 500)

@pvb_api_bp.route('/verifiers/<verifier_address>/devices', methods=['POST'])
def add_device(verifier_address: str):
    """
    Add a Device Security Module under a verifier's vouching.
    
    Expected JSON payload:
    {
        "device_id": "unique_device_identifier",
        "device_public_key": "device_public_key_string",
        "metadata": "Optional device metadata"
    }
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return handle_error("ValidationError", "Request body is required", 400)
        
        device_data = DeviceRegistrationSchema(**data)
        
        # Get blockchain interface
        blockchain = get_blockchain()
        
        # Add device on blockchain
        result = blockchain.add_device(
            device_id=device_data.device_id,
            device_public_key=device_data.device_public_key,
            metadata=device_data.metadata or ""
        )
        
        if result['success']:
            response = {
                'success': True,
                'message': 'Device registered successfully',
                'transaction_hash': result['transaction_hash'],
                'block_number': result['block_number'],
                'device_id': result['device_id'],
                'verifier_address': verifier_address,
                'timestamp': datetime.utcnow()
            }
            return response, 201
        else:
            return handle_error("BlockchainError", result['error'], 500)
            
    except ValidationError as e:
        return handle_error("ValidationError", str(e), 400)
    except ConnectionError as e:
        return handle_error("ConnectionError", str(e), 503)
    except Exception as e:
        logger.error(f"Unexpected error in add_device: {traceback.format_exc()}")
        return handle_error("InternalError", "An unexpected error occurred", 500)

@pvb_api_bp.route('/devices/<device_id>', methods=['GET'])
def get_device_info(device_id: str):
    """
    Get information about a registered device.
    """
    try:
        blockchain = get_blockchain()
        
        # Get device information from blockchain
        device_info = blockchain.get_device_info(device_id)
        
        if device_info:
            return device_info, 200
        else:
            return handle_error("NotFoundError", f"Device {device_id} not found", 404)
            
    except ConnectionError as e:
        return handle_error("ConnectionError", str(e), 503)
    except Exception as e:
        logger.error(f"Unexpected error in get_device_info: {traceback.format_exc()}")
        return handle_error("InternalError", "An unexpected error occurred", 500)

# Data Submission and Verification Endpoints

@pvb_api_bp.route('/data', methods=['POST'])
def submit_data():
    """
    Submit data to the Physical Verification Blockchain.
    
    Expected JSON payload (DSM Output format):
    {
        "device_id": "device_identifier",
        "data_hash": "sha256_hash_of_data",
        "signature": "digital_signature",
        "data_uri": "uri_to_offchain_storage",
        "metadata": "optional_metadata"
    }
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return handle_error("ValidationError", "Request body is required", 400)
        
        submission_data = DataSubmissionSchema(**data)
        
        # Get blockchain interface
        blockchain = get_blockchain()
        
        # Submit data to blockchain
        result = blockchain.submit_data(
            device_id=submission_data.device_id,
            data_hash=submission_data.data_hash,
            signature=submission_data.signature,
            data_uri=submission_data.data_uri,
            metadata=submission_data.metadata or ""
        )
        
        if result['success']:
            response = SubmissionResponseSchema(
                success=True,
                transaction_hash=result['transaction_hash'],
                data_hash=result['data_hash'],
                timestamp=datetime.utcnow(),
                block_number=result['block_number'],
                message="Data submitted successfully to PVB"
            )
            return response.dict(), 201
        else:
            return handle_error("BlockchainError", result['error'], 500)
            
    except ValidationError as e:
        return handle_error("ValidationError", str(e), 400)
    except ConnectionError as e:
        return handle_error("ConnectionError", str(e), 503)
    except Exception as e:
        logger.error(f"Unexpected error in submit_data: {traceback.format_exc()}")
        return handle_error("InternalError", "An unexpected error occurred", 500)

@pvb_api_bp.route('/data/<data_hash>/verify', methods=['GET'])
def verify_data(data_hash: str):
    """
    Verify a data submission on the blockchain.
    """
    try:
        # Validate data hash format
        verification_request = VerificationRequestSchema(data_hash=data_hash)
        
        blockchain = get_blockchain()
        
        # Verify submission on blockchain
        submission_data = blockchain.verify_submission(verification_request.data_hash)
        
        if submission_data:
            response = VerificationResponseSchema(
                data_hash=verification_request.data_hash,
                is_verified=submission_data['is_verified'],
                device_id=submission_data['device_id'],
                verifier_address=submission_data['verifier_address'],
                timestamp=datetime.fromtimestamp(submission_data['timestamp']),
                data_uri=submission_data['data_uri'],
                metadata=submission_data['metadata'],
                block_number=submission_data['block_number']
            )
            return response.dict(), 200
        else:
            response = VerificationResponseSchema(
                data_hash=verification_request.data_hash,
                is_verified=False
            )
            return response.dict(), 404
            
    except ValidationError as e:
        return handle_error("ValidationError", str(e), 400)
    except ConnectionError as e:
        return handle_error("ConnectionError", str(e), 503)
    except Exception as e:
        logger.error(f"Unexpected error in verify_data: {traceback.format_exc()}")
        return handle_error("InternalError", "An unexpected error occurred", 500)

# Register the blueprint with the main Flask app
def register_pvb_api(app):
    """
    Register the PVB API blueprint with the Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(pvb_api_bp)
    logger.info("PVB API blueprint registered successfully")
