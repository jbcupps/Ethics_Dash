// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title TrustedVerifierRegistry
 * @dev Manages the registration of Trusted Verifiers and the DSMs they vouch for
 * Supports voluntary participation and freedom of choice in the PVB ecosystem
 */
contract TrustedVerifierRegistry {
    
    // Struct definitions
    struct Verifier {
        string name;
        address owner;
        bool isActive;
        uint256 registrationTimestamp;
        string metadata;
    }
    
    struct Device {
        address verifierAddress;
        bytes32 deviceId;
        string devicePublicKey;
        string metadata;
        bool isActive;
        uint256 registrationTimestamp;
    }
    
    // State variables
    mapping(address => Verifier) public verifiers;
    mapping(bytes32 => Device) public devices;
    mapping(address => mapping(bytes32 => bool)) public verifierDevices;
    mapping(address => bytes32[]) public verifierDeviceList;
    
    // Contract owner for initial governance (can be transferred to DAO later)
    address public owner;
    bool public openRegistration = true; // Allows anyone to become a TV initially
    
    // Events
    event VerifierRegistered(address indexed verifierAddress, string name, uint256 timestamp);
    event VerifierDeprecated(address indexed verifierAddress, uint256 timestamp);
    event DeviceAdded(address indexed verifierAddress, bytes32 indexed deviceId, string devicePublicKey, uint256 timestamp);
    event DeviceRevoked(address indexed verifierAddress, bytes32 indexed deviceId, uint256 timestamp);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event RegistrationPolicyChanged(bool openRegistration);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyActiveVerifier() {
        require(verifiers[msg.sender].isActive, "Caller is not an active verifier");
        _;
    }
    
    modifier validDeviceId(bytes32 _deviceId) {
        require(_deviceId != bytes32(0), "Device ID cannot be empty");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Register a new Trusted Verifier
     * @param _name Name of the verifier organization/entity
     * @param _metadata Additional metadata about the verifier
     */
    function registerVerifier(string memory _name, string memory _metadata) external {
        require(bytes(_name).length > 0, "Verifier name cannot be empty");
        require(!verifiers[msg.sender].isActive, "Verifier already registered and active");
        
        // Check if registration is open or if caller is approved by owner
        if (!openRegistration) {
            require(msg.sender == owner, "Registration is currently restricted");
        }
        
        verifiers[msg.sender] = Verifier({
            name: _name,
            owner: msg.sender,
            isActive: true,
            registrationTimestamp: block.timestamp,
            metadata: _metadata
        });
        
        emit VerifierRegistered(msg.sender, _name, block.timestamp);
    }
    
    /**
     * @dev Deprecate a verifier (self-deprecation)
     */
    function deprecateVerifier() external onlyActiveVerifier {
        verifiers[msg.sender].isActive = false;
        
        // Deactivate all devices registered by this verifier
        bytes32[] memory deviceIds = verifierDeviceList[msg.sender];
        for (uint256 i = 0; i < deviceIds.length; i++) {
            if (devices[deviceIds[i]].isActive) {
                devices[deviceIds[i]].isActive = false;
            }
        }
        
        emit VerifierDeprecated(msg.sender, block.timestamp);
    }
    
    /**
     * @dev Add a new device under a verifier's vouching
     * @param _deviceId Unique identifier for the device
     * @param _devicePublicKey Public key of the device for signature verification
     * @param _metadata Additional metadata about the device
     */
    function addDevice(
        bytes32 _deviceId, 
        string memory _devicePublicKey, 
        string memory _metadata
    ) external onlyActiveVerifier validDeviceId(_deviceId) {
        require(bytes(_devicePublicKey).length > 0, "Device public key cannot be empty");
        require(!devices[_deviceId].isActive, "Device already registered and active");
        
        devices[_deviceId] = Device({
            verifierAddress: msg.sender,
            deviceId: _deviceId,
            devicePublicKey: _devicePublicKey,
            metadata: _metadata,
            isActive: true,
            registrationTimestamp: block.timestamp
        });
        
        verifierDevices[msg.sender][_deviceId] = true;
        verifierDeviceList[msg.sender].push(_deviceId);
        
        emit DeviceAdded(msg.sender, _deviceId, _devicePublicKey, block.timestamp);
    }
    
    /**
     * @dev Revoke a device (only by the verifier who registered it)
     * @param _deviceId Device ID to revoke
     */
    function revokeDevice(bytes32 _deviceId) external validDeviceId(_deviceId) {
        require(devices[_deviceId].verifierAddress == msg.sender, "Only the registering verifier can revoke this device");
        require(devices[_deviceId].isActive, "Device is not active");
        
        devices[_deviceId].isActive = false;
        verifierDevices[msg.sender][_deviceId] = false;
        
        emit DeviceRevoked(msg.sender, _deviceId, block.timestamp);
    }
    
    /**
     * @dev Get device public key for signature verification
     * @param _deviceId Device ID to query
     * @return Device public key string
     */
    function getDevicePublicKey(bytes32 _deviceId) external view validDeviceId(_deviceId) returns (string memory) {
        require(devices[_deviceId].isActive, "Device is not active");
        return devices[_deviceId].devicePublicKey;
    }
    
    /**
     * @dev Check if a device is active
     * @param _deviceId Device ID to check
     * @return Boolean indicating if device is active
     */
    function isDeviceActive(bytes32 _deviceId) external view returns (bool) {
        return devices[_deviceId].isActive;
    }
    
    /**
     * @dev Check if a verifier is active
     * @param _verifierAddress Verifier address to check
     * @return Boolean indicating if verifier is active
     */
    function isVerifierActive(address _verifierAddress) external view returns (bool) {
        return verifiers[_verifierAddress].isActive;
    }
    
    /**
     * @dev Get device details
     * @param _deviceId Device ID to query
     * @return Device struct data
     */
    function getDevice(bytes32 _deviceId) external view validDeviceId(_deviceId) returns (Device memory) {
        return devices[_deviceId];
    }
    
    /**
     * @dev Get verifier details
     * @param _verifierAddress Verifier address to query
     * @return Verifier struct data
     */
    function getVerifier(address _verifierAddress) external view returns (Verifier memory) {
        return verifiers[_verifierAddress];
    }
    
    /**
     * @dev Get all devices registered by a verifier
     * @param _verifierAddress Verifier address to query
     * @return Array of device IDs
     */
    function getVerifierDevices(address _verifierAddress) external view returns (bytes32[] memory) {
        return verifierDeviceList[_verifierAddress];
    }
    
    /**
     * @dev Transfer ownership (for DAO governance transition)
     * @param _newOwner New owner address
     */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "New owner cannot be zero address");
        address previousOwner = owner;
        owner = _newOwner;
        emit OwnershipTransferred(previousOwner, _newOwner);
    }
    
    /**
     * @dev Set registration policy (open vs restricted)
     * @param _openRegistration Whether registration is open to all
     */
    function setRegistrationPolicy(bool _openRegistration) external onlyOwner {
        openRegistration = _openRegistration;
        emit RegistrationPolicyChanged(_openRegistration);
    }
} 