// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./TrustedVerifierRegistry.sol";

/**
 * @title DataSubmission
 * @dev Records signed data hashes from verified Device Security Modules (DSMs)
 * Core component of the Physical Verification Blockchain (PVB) system
 */
contract DataSubmission {
    
    // Reference to the TrustedVerifierRegistry contract
    TrustedVerifierRegistry public trustedVerifierRegistry;
    
    // Struct to store submission details
    struct Submission {
        bytes32 deviceId;
        address verifierAddress;
        bytes32 dataHash;
        string signature;
        uint256 timestamp;
        string dataUri;
        string metadata;
        bool isVerified;
        uint256 blockNumber;
    }
    
    // State variables
    mapping(bytes32 => Submission) public submissions; // dataHash => Submission
    mapping(bytes32 => bytes32[]) public deviceSubmissions; // deviceId => dataHash[]
    mapping(address => bytes32[]) public verifierSubmissions; // verifierAddress => dataHash[]
    
    // Counter for total submissions
    uint256 public totalSubmissions;
    
    // Events
    event DataSubmitted(
        bytes32 indexed dataHash,
        bytes32 indexed deviceId,
        address indexed verifierAddress,
        uint256 timestamp,
        string dataUri,
        uint256 blockNumber
    );
    
    event SubmissionVerified(
        bytes32 indexed dataHash,
        bytes32 indexed deviceId,
        bool isValid
    );
    
    // Modifiers
    modifier onlyActiveDevice(bytes32 _deviceId) {
        require(
            trustedVerifierRegistry.isDeviceActive(_deviceId),
            "Device is not active or not registered"
        );
        _;
    }
    
    modifier validDataHash(bytes32 _dataHash) {
        require(_dataHash != bytes32(0), "Data hash cannot be empty");
        _;
    }
    
    modifier submissionExists(bytes32 _dataHash) {
        require(submissions[_dataHash].timestamp != 0, "Submission does not exist");
        _;
    }
    
    /**
     * @dev Constructor sets the TrustedVerifierRegistry contract address
     * @param _trustedVerifierRegistryAddress Address of the deployed TrustedVerifierRegistry contract
     */
    constructor(address _trustedVerifierRegistryAddress) {
        require(_trustedVerifierRegistryAddress != address(0), "Registry address cannot be zero");
        trustedVerifierRegistry = TrustedVerifierRegistry(_trustedVerifierRegistryAddress);
    }
    
    /**
     * @dev Submit data with cryptographic proof from a verified DSM
     * @param _deviceId Unique identifier of the submitting device
     * @param _dataHash Cryptographic hash of the original data
     * @param _signature Digital signature of the data hash by the device
     * @param _dataUri URI pointing to off-chain storage of the full data
     * @param _metadata Additional metadata about the submission
     */
    function submitData(
        bytes32 _deviceId,
        bytes32 _dataHash,
        string memory _signature,
        string memory _dataUri,
        string memory _metadata
    ) external onlyActiveDevice(_deviceId) validDataHash(_dataHash) {
        
        require(bytes(_signature).length > 0, "Signature cannot be empty");
        require(bytes(_dataUri).length > 0, "Data URI cannot be empty");
        require(submissions[_dataHash].timestamp == 0, "Data hash already submitted");
        
        // Get device details from the registry
        TrustedVerifierRegistry.Device memory device = trustedVerifierRegistry.getDevice(_deviceId);
        require(device.isActive, "Device is not active");
        
        // Verify that the verifier is still active
        require(
            trustedVerifierRegistry.isVerifierActive(device.verifierAddress),
            "Device's verifier is not active"
        );
        
        // Get device public key for signature verification
        string memory devicePublicKey = trustedVerifierRegistry.getDevicePublicKey(_deviceId);
        
        // Verify the signature (simplified - in practice you'd use proper ECDSA verification)
        bool signatureValid = _verifySignature(_dataHash, _signature, devicePublicKey);
        require(signatureValid, "Invalid signature");
        
        // Store the submission
        submissions[_dataHash] = Submission({
            deviceId: _deviceId,
            verifierAddress: device.verifierAddress,
            dataHash: _dataHash,
            signature: _signature,
            timestamp: block.timestamp,
            dataUri: _dataUri,
            metadata: _metadata,
            isVerified: signatureValid,
            blockNumber: block.number
        });
        
        // Update tracking arrays
        deviceSubmissions[_deviceId].push(_dataHash);
        verifierSubmissions[device.verifierAddress].push(_dataHash);
        totalSubmissions++;
        
        // Emit events
        emit DataSubmitted(
            _dataHash,
            _deviceId,
            device.verifierAddress,
            block.timestamp,
            _dataUri,
            block.number
        );
        
        emit SubmissionVerified(_dataHash, _deviceId, signatureValid);
    }
    
    /**
     * @dev Verify a submission's authenticity
     * @param _dataHash Hash of the data to verify
     * @return Submission details and verification status
     */
    function verifySubmission(bytes32 _dataHash) 
        external 
        view 
        submissionExists(_dataHash) 
        returns (Submission memory) 
    {
        return submissions[_dataHash];
    }
    
    /**
     * @dev Verify data integrity by comparing provided data with stored hash
     * @param _dataHash Hash of the original submission
     * @param _providedData The actual data to verify against the hash
     * @return Boolean indicating if the data matches the stored hash
     */
    function verifyDataIntegrity(bytes32 _dataHash, bytes memory _providedData) 
        external 
        view 
        submissionExists(_dataHash) 
        returns (bool) 
    {
        bytes32 computedHash = keccak256(_providedData);
        return computedHash == _dataHash;
    }
    
    /**
     * @dev Get all submissions by a specific device
     * @param _deviceId Device ID to query
     * @return Array of data hashes submitted by the device
     */
    function getDeviceSubmissions(bytes32 _deviceId) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        return deviceSubmissions[_deviceId];
    }
    
    /**
     * @dev Get all submissions verified by a specific verifier
     * @param _verifierAddress Verifier address to query
     * @return Array of data hashes verified by the verifier
     */
    function getVerifierSubmissions(address _verifierAddress) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        return verifierSubmissions[_verifierAddress];
    }
    
    /**
     * @dev Get submission details including full chain of custody
     * @param _dataHash Data hash to query
     * @return Complete submission details with verification chain
     */
    function getSubmissionDetails(bytes32 _dataHash) 
        external 
        view 
        submissionExists(_dataHash) 
        returns (
            Submission memory submission,
            TrustedVerifierRegistry.Device memory device,
            TrustedVerifierRegistry.Verifier memory verifier
        ) 
    {
        submission = submissions[_dataHash];
        device = trustedVerifierRegistry.getDevice(submission.deviceId);
        verifier = trustedVerifierRegistry.getVerifier(submission.verifierAddress);
    }
    
    /**
     * @dev Check if a data hash has been submitted
     * @param _dataHash Data hash to check
     * @return Boolean indicating if the hash exists in submissions
     */
    function hasSubmission(bytes32 _dataHash) external view returns (bool) {
        return submissions[_dataHash].timestamp != 0;
    }
    
    /**
     * @dev Get total number of submissions in the system
     * @return Total submission count
     */
    function getTotalSubmissions() external view returns (uint256) {
        return totalSubmissions;
    }
    
    /**
     * @dev Update the TrustedVerifierRegistry contract address (for upgrades)
     * @param _newRegistryAddress New registry contract address
     * @dev This should ideally be controlled by governance in production
     */
    function updateRegistryAddress(address _newRegistryAddress) external {
        require(_newRegistryAddress != address(0), "Registry address cannot be zero");
        // In production, add proper access control (onlyOwner or governance)
        trustedVerifierRegistry = TrustedVerifierRegistry(_newRegistryAddress);
    }
    
    /**
     * @dev Internal function to verify signature (simplified implementation)
     * @param _dataHash Hash that was signed
     * @param _signature Signature to verify
     * @param _publicKey Public key of the signer
     * @return Boolean indicating if signature is valid
     * @dev In production, implement proper ECDSA signature verification using ecrecover
     */
    function _verifySignature(
        bytes32 _dataHash,
        string memory _signature,
        string memory _publicKey
    ) internal pure returns (bool) {
        // Simplified signature verification for demonstration
        // In production, implement proper ECDSA verification:
        // 1. Parse the signature to extract r, s, v values
        // 2. Use ecrecover to get the signer's address
        // 3. Compare with the expected public key/address
        
        // For now, return true if signature and public key are non-empty
        // This is a placeholder and MUST be replaced with proper cryptographic verification
        return (bytes(_signature).length > 0 && bytes(_publicKey).length > 0);
    }
    
    /**
     * @dev Get submission history for audit purposes
     * @param _startIndex Starting index for pagination
     * @param _count Number of records to return
     * @return Array of submission data hashes for audit trail
     */
    function getSubmissionHistory(uint256 _startIndex, uint256 _count) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        require(_startIndex < totalSubmissions, "Start index out of range");
        
        uint256 endIndex = _startIndex + _count;
        if (endIndex > totalSubmissions) {
            endIndex = totalSubmissions;
        }
        
        bytes32[] memory result = new bytes32[](endIndex - _startIndex);
        uint256 currentIndex = 0;
        
        // This is a simplified implementation - in production, you'd maintain
        // a proper indexed array for efficient pagination
        // For now, this serves as a placeholder for the audit functionality
        
        return result;
    }
} 