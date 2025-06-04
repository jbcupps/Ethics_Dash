# Physical Verification Blockchain (PVB) Implementation Guide

## Overview

The Physical Verification Blockchain (PVB) is a cryptographically secure chain of custody system for media and data, integrated into the Ethics Dashboard. This system provides immutable verification records for data submitted by Device Security Modules (DSMs) through Trusted Verifiers (TVs).

## Architecture

The PVB system consists of three main components:

### 1. Device Security Modules (DSMs)
- Software/hardware on capturing devices that sign data at the source
- Generate cryptographic hashes and digital signatures
- Submit data packages to the PVB system

### 2. Trusted Verifiers (TVs)
- Entities that vet and register DSMs
- Vouch for the authenticity and reliability of DSMs
- Manage device registration and revocation

### 3. Physical Verification Blockchain (PVB)
- Stores immutable records (hashes, signatures, metadata) of submitted data
- Provides verification and audit capabilities
- Maintains chain of custody information

## System Components

### Smart Contracts

#### TrustedVerifierRegistry.sol
- **Purpose**: Manages registration of Trusted Verifiers and DSMs
- **Key Functions**:
  - `registerVerifier()`: Register a new Trusted Verifier
  - `addDevice()`: Add a DSM under a verifier's vouching
  - `revokeDevice()`: Revoke a DSM
  - `isDeviceActive()`: Check device status
  - `getDevicePublicKey()`: Retrieve device public key

#### DataSubmission.sol
- **Purpose**: Records signed data hashes from verified DSMs
- **Key Functions**:
  - `submitData()`: Submit data with cryptographic proof
  - `verifySubmission()`: Verify a data submission
  - `getSubmissionDetails()`: Get complete submission information

### Python Components

#### Schemas (`backend/app/pvb/schemas.py`)
- **DSMOutputSchema**: Validates DSM data packages
- **VerifierRegistrationSchema**: Validates verifier registration
- **DataSubmissionSchema**: Validates data submissions
- **VerificationResponseSchema**: Structures verification responses

#### Blockchain Interface (`backend/app/pvb/blockchain_interface.py`)
- **PVBBlockchainInterface**: Main class for Web3 interactions
- Handles contract deployment and interaction
- Manages transaction signing and verification

#### API Endpoints (`backend/app/pvb/api.py`)
- RESTful API for PVB operations
- Handles verifier registration, device management, and data submission
- Provides verification endpoints

## API Endpoints

### Health Check
- **GET** `/api/pvb/health` - Check system health

### Verifier Management
- **POST** `/api/pvb/verifiers` - Register a new Trusted Verifier
- **POST** `/api/pvb/verifiers/{address}/devices` - Add a device under a verifier

### Device Management
- **GET** `/api/pvb/devices/{device_id}` - Get device information

### Data Operations
- **POST** `/api/pvb/data` - Submit data to the PVB
- **GET** `/api/pvb/data/{hash}/verify` - Verify a data submission

## Setup and Configuration

### 1. Environment Variables

Add the following to your `.env` file:

```bash
# Blockchain Configuration
WEB3_PROVIDER_URL=http://localhost:7545
REGISTRY_CONTRACT_ADDRESS=0x...
SUBMISSION_CONTRACT_ADDRESS=0x...
BLOCKCHAIN_PRIVATE_KEY=0x...

# Network Configuration
PVB_NETWORK_ID=1337
PVB_GAS_LIMIT=300000
PVB_GAS_PRICE=20000000000
```

### 2. Docker Setup

The system includes a Ganache blockchain service for development:

```bash
# Start all services including Ganache
docker compose up -d

# Check Ganache is running
curl http://localhost:7545
```

### 3. Smart Contract Deployment

Deploy the smart contracts to your blockchain network:

```bash
# Example deployment script (you'll need to create this)
python scripts/deploy_contracts.py
```

## Usage Examples

### 1. Register a Trusted Verifier

```bash
curl -X POST http://localhost:5000/api/pvb/verifiers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Verification Authority",
    "metadata": "Trusted verifier for media authentication"
  }'
```

### 2. Add a Device

```bash
curl -X POST http://localhost:5000/api/pvb/verifiers/0x.../devices \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "camera_001",
    "device_public_key": "0x...",
    "metadata": "Professional camera device"
  }'
```

### 3. Submit Data

```bash
curl -X POST http://localhost:5000/api/pvb/data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "camera_001",
    "data_hash": "a1b2c3d4e5f6...",
    "signature": "0x...",
    "data_uri": "ipfs://QmExample...",
    "metadata": "Photo taken at location X"
  }'
```

### 4. Verify Data

```bash
curl http://localhost:5000/api/pvb/data/a1b2c3d4e5f6.../verify
```

## DSM Integration

### DSM Output Format

DSMs should produce data packages in the following format:

```json
{
  "device_id": "unique_device_identifier",
  "data_hash": "sha256_hash_of_media_data",
  "signature": "digital_signature_of_hash",
  "timestamp": "2024-01-01T12:00:00Z",
  "data_uri": "ipfs://QmExampleHash...",
  "metadata": {
    "location": "GPS coordinates",
    "sensor_data": "Additional sensor readings",
    "device_info": "Camera model and settings"
  }
}
```

### Signature Generation

DSMs must:
1. Generate SHA-256 hash of the media data
2. Sign the hash using their private key (ECDSA)
3. Include the signature in the data package

### Data Storage

- Store full media data off-chain (IPFS, Arweave, etc.)
- Only submit hashes and metadata to the blockchain
- Ensure data URI is accessible for verification

## Security Considerations

### Key Management
- DSMs manage their own private keys
- Trusted Verifiers manage their signing keys
- Never expose private keys in API calls or logs

### Signature Verification
- All signatures are verified on-chain
- Invalid signatures are rejected
- Public keys are stored in the registry contract

### Access Control
- Only registered devices can submit data
- Only active verifiers can register devices
- Revoked devices cannot submit new data

## Development Workflow

### 1. Local Development

```bash
# Start development environment
docker compose up -d

# Check services are running
docker compose ps

# View logs
docker compose logs -f ai-backend
docker compose logs -f ganache
```

### 2. Testing

```bash
# Run API tests
python -m pytest backend/tests/pvb/

# Test blockchain connectivity
curl http://localhost:5000/api/pvb/health
```

### 3. Contract Development

1. Modify contracts in `backend/app/pvb/contracts/`
2. Deploy to local Ganache
3. Update contract addresses in environment
4. Test API endpoints

## Production Deployment

### 1. Blockchain Network

Choose appropriate blockchain network:
- **Ethereum Mainnet**: High security, high cost
- **Polygon**: Lower cost, good performance
- **Private Network**: Full control, custom requirements

### 2. Contract Deployment

1. Deploy contracts to chosen network
2. Verify contracts on block explorer
3. Update environment variables
4. Test all functionality

### 3. Security Hardening

- Use hardware security modules for key storage
- Implement proper access controls
- Set up monitoring and alerting
- Regular security audits

## Monitoring and Maintenance

### Health Checks

The system provides health check endpoints:
- Blockchain connectivity
- Contract accessibility
- Account balance monitoring

### Logging

Monitor logs for:
- Failed transactions
- Invalid signatures
- Connection issues
- Unusual activity patterns

### Backup and Recovery

- Backup private keys securely
- Monitor contract state
- Plan for network upgrades
- Document recovery procedures

## Troubleshooting

### Common Issues

1. **Blockchain Connection Failed**
   - Check Web3 provider URL
   - Verify network connectivity
   - Check Ganache is running

2. **Transaction Failed**
   - Check account balance
   - Verify gas settings
   - Check contract addresses

3. **Signature Verification Failed**
   - Verify device is registered
   - Check signature format
   - Ensure correct private key used

### Debug Commands

```bash
# Check blockchain connection
curl http://localhost:5000/api/pvb/health

# View Ganache accounts
curl -X POST http://localhost:7545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}'

# Check contract deployment
curl -X POST http://localhost:7545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getCode","params":["CONTRACT_ADDRESS","latest"],"id":1}'
```

## Future Enhancements

### Planned Features

1. **DAO Governance**: Transition to decentralized governance
2. **Multi-chain Support**: Support multiple blockchain networks
3. **Advanced Cryptography**: Implement zero-knowledge proofs
4. **Mobile SDK**: SDK for mobile device integration
5. **Audit Dashboard**: Web interface for audit trails

### Integration Opportunities

- **IPFS Integration**: Seamless decentralized storage
- **Oracle Networks**: External data verification
- **Identity Systems**: Integration with DID systems
- **Compliance Tools**: Regulatory compliance features

## Support and Resources

### Documentation
- [Smart Contract Reference](./PVB_Smart_Contracts.md)
- [API Reference](./PVB_API_Reference.md)
- [DSM Integration Guide](./PVB_DSM_Integration.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Discussions: Community support and ideas
- Wiki: Additional documentation and examples

### Contact
For technical support or questions about the PVB implementation, please refer to the project documentation or create an issue in the GitHub repository. 