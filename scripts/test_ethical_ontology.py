#!/usr/bin/env python3
"""
Test Script for Ethical Ontology Blockchain

Verifies that the Ethical Ontology Blockchain is working correctly with sample ethical checks.
Aligns with paper's dual-blockchain architecture requirements.

Usage:
    python scripts/test_ethical_ontology.py [--local] [--verbose]
"""

import sys
import json
import time
import logging
import argparse
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_direct_blockchain():
    """Test the blockchain directly (for local testing)."""
    logger.info("Testing Ethical Ontology Blockchain directly...")
    
    try:
        from ethical_ontology.blockchain.core import EthicalOntologyBlockchain
        from ethical_ontology.chaincode.deontic_rule import DeonticRuleContract
        from ethical_ontology.chaincode.virtue_reputation import VirtueReputationContract
        from ethical_ontology.chaincode.teleological_outcome import TeleologicalOutcomeContract
        
        # Initialize blockchain
        blockchain = EthicalOntologyBlockchain(network_id="test-network")
        logger.info(f"✓ Blockchain initialized with {blockchain.get_chain_length()} blocks")
        
        # Deploy contracts
        deontic_contract = DeonticRuleContract()
        virtue_contract = VirtueReputationContract()
        teleological_contract = TeleologicalOutcomeContract()
        
        deontic_addr = blockchain.deploy_contract("DeonticRuleContract", deontic_contract)
        virtue_addr = blockchain.deploy_contract("VirtueReputationContract", virtue_contract)
        teleological_addr = blockchain.deploy_contract("TeleologicalOutcomeContract", teleological_contract)
        
        logger.info(f"✓ Deployed 3 smart contracts")
        
        # Test deontological contract
        result1 = blockchain.call_contract(
            deontic_addr,
            "check_compliance",
            {"action_description": "I will tell the truth to help someone make an informed decision"}
        )
        assert result1.get("compliant") == True, "Truthful action should be compliant"
        logger.info(f"✓ Deontological test passed: {result1.get('reasoning', '')[:60]}...")
        
        # Test virtue contract
        result2 = blockchain.call_contract(
            virtue_addr,
            "check_compliance",
            {
                "action_description": "I will courageously defend the rights of vulnerable people",
                "agent_id": "test_agent"
            }
        )
        assert result2.get("compliant") == True, "Virtuous action should be compliant"
        logger.info(f"✓ Virtue ethics test passed: {result2.get('reasoning', '')[:60]}...")
        
        # Test teleological contract
        result3 = blockchain.call_contract(
            teleological_addr,
            "check_compliance",
            {
                "action_description": "Develop renewable energy technology to reduce pollution",
                "affected_parties": 1000,
                "time_horizon": "long_term",
                "certainty_level": 0.8
            }
        )
        assert result3.get("compliant") == True, "Beneficial action should be compliant"
        logger.info(f"✓ Teleological test passed: {result3.get('reasoning', '')[:60]}...")
        
        # Mine a block
        block = blockchain.mine_block("test_miner")
        assert block is not None, "Block mining should succeed"
        logger.info(f"✓ Block mined successfully: block {block.index} with {len(block.transactions)} transactions")
        
        # Validate blockchain
        assert blockchain.is_chain_valid(), "Blockchain should be valid"
        logger.info(f"✓ Blockchain validation passed")
        
        logger.info("🎉 All direct blockchain tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Direct blockchain test failed: {e}")
        return False

def test_api_endpoint(base_url="http://localhost:5000"):
    """Test the /ethical_check API endpoint."""
    logger.info(f"Testing /ethical_check API endpoint at {base_url}...")
    
    test_cases = [
        {
            "name": "Truthful communication",
            "data": {
                "action_description": "I will provide accurate information to help customers make informed decisions",
                "agent_id": "sales_agent",
                "affected_parties": 50,
                "time_horizon": "short_term",
                "certainty_level": 0.9
            },
            "expected_compliant": True
        },
        {
            "name": "Deceptive marketing",
            "data": {
                "action_description": "I will lie about our product's capabilities to increase sales",
                "agent_id": "bad_sales_agent",
                "affected_parties": 100,
                "time_horizon": "medium_term",
                "certainty_level": 0.8
            },
            "expected_compliant": False
        },
        {
            "name": "Environmental sustainability",
            "data": {
                "action_description": "Implement sustainable manufacturing practices to reduce environmental impact",
                "agent_id": "sustainability_manager",
                "affected_parties": 10000,
                "time_horizon": "long_term",
                "certainty_level": 0.7,
                "frameworks": ["teleological", "virtue_based"]
            },
            "expected_compliant": True
        },
        {
            "name": "Single framework test",
            "data": {
                "action_description": "Stand up for justice and defend the rights of marginalized communities",
                "agent_id": "activist",
                "frameworks": ["virtue_based"]
            },
            "expected_compliant": True
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"Running test {i}/{total_tests}: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/ethical_check",
                json=test_case["data"],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Test {i} failed: HTTP {response.status_code} - {response.text}")
                continue
            
            result = response.json()
            
            # Check if response has expected structure
            required_fields = ["overall_assessment", "evaluation_results", "blockchain_info"]
            if not all(field in result for field in required_fields):
                logger.error(f"❌ Test {i} failed: Missing required fields in response")
                continue
            
            # Check compliance result
            actual_compliant = result["overall_assessment"]["compliant"]
            expected_compliant = test_case["expected_compliant"]
            
            if actual_compliant == expected_compliant:
                logger.info(f"✓ Test {i} passed: compliant={actual_compliant}, confidence={result['overall_assessment']['confidence']}")
                passed_tests += 1
            else:
                logger.error(f"❌ Test {i} failed: expected compliant={expected_compliant}, got {actual_compliant}")
                logger.error(f"   Recommendation: {result['overall_assessment']['recommendation']}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Test {i} failed: Network error - {e}")
        except Exception as e:
            logger.error(f"❌ Test {i} failed: {e}")
    
    success_rate = passed_tests / total_tests
    logger.info(f"API test results: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")
    
    if success_rate >= 0.75:  # 75% pass rate threshold
        logger.info("🎉 API tests passed!")
        return True
    else:
        logger.error("❌ API tests failed - insufficient pass rate")
        return False

def test_health_endpoint(base_url="http://localhost:5000"):
    """Test that the API is healthy and running."""
    logger.info(f"Testing health endpoint at {base_url}...")
    
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"✓ API is healthy: {health_data.get('status', 'unknown')}")
            return True
        else:
            logger.error(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Health check failed: {e}")
        return False

def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test Ethical Ontology Blockchain")
    parser.add_argument("--local", action="store_true", help="Test blockchain directly (local mode)")
    parser.add_argument("--api-url", default="http://localhost:5000", help="API base URL")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("Ethical Ontology Blockchain Test Suite")
    logger.info("=" * 60)
    
    test_results = []
    
    if args.local:
        # Test blockchain directly
        logger.info("Running local blockchain tests...")
        test_results.append(("Direct Blockchain", test_direct_blockchain()))
    else:
        # Test via API
        logger.info(f"Running API tests against {args.api_url}...")
        
        # Check if API is running
        test_results.append(("Health Check", test_health_endpoint(args.api_url)))
        
        # Test ethical check endpoint
        test_results.append(("Ethical Check API", test_api_endpoint(args.api_url)))
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Ethical Ontology Blockchain is working correctly.")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 