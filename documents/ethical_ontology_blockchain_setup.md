# Ethical Ontology Blockchain Setup and Usage

This document provides comprehensive instructions for setting up and using the Ethical Ontology Blockchain component of the Ethics Dashboard. This implementation aligns with the paper's dual-blockchain architecture for decentralized ethical AI governance.

## Overview

The Ethical Ontology Blockchain is a specialized blockchain layer that encodes and verifies ethical principles through smart contracts. It implements three main ethical frameworks:

1. **Deontological Ethics** - Duty-based moral rules (e.g., "Do not lie")
2. **Virtue Ethics** - Character-based moral evaluation with reputation tracking
3. **Teleological Ethics** - Consequence-based evaluation of outcomes and utility

## Architecture

The system consists of:
- **Core Blockchain** (`ethical_ontology/blockchain/`) - Simplified blockchain simulation
- **Smart Contracts** (`ethical_ontology/chaincode/`) - Ethical evaluation contracts
- **Network Layer** (`ethical_ontology/blockchain/network.py`) - Node communication simulation
- **Configuration** (`ethical_ontology/config/`) - Network and contract settings
- **API Integration** (`backend/app/api.py`) - `/ethical_check` endpoint
- **Deployment Scripts** (`scripts/ethical_ontology_deploy.py`) - Automated setup

## Quick Start

### 1. Deploy the Blockchain

Run the deployment script to set up the blockchain and deploy smart contracts:

```bash
python scripts/ethical_ontology_deploy.py --network ethical-ontology-local
```

This will:
- Initialize a local blockchain network
- Deploy deontological, virtue-based, and teleological smart contracts
- Run validation tests
- Generate a deployment report

### 2. Test the System

Run the test suite to verify everything is working:

```bash
# Test the blockchain directly
python scripts/test_ethical_ontology.py --local

# Test via API (requires backend running)
python scripts/test_ethical_ontology.py --api-url http://localhost:5000
```

### 3. Use the API Endpoint

Make ethical compliance checks via the `/api/ethical_check` endpoint:

```bash
curl -X POST http://localhost:5000/api/ethical_check \
  -H "Content-Type: application/json" \
  -d '{
    "action_description": "I will provide accurate information to help customers make informed decisions",
    "agent_id": "sales_agent",
    "affected_parties": 50,
    "time_horizon": "short_term",
    "certainty_level": 0.9,
    "frameworks": ["deontological", "virtue_based", "teleological"]
  }'
```

## Docker Deployment

The system is integrated with Docker Compose for easy deployment:

```bash
# Start all services including blockchain
docker-compose up -d

# View blockchain logs
docker-compose logs ethical-ontology-blockchain

# Test the deployment
docker-compose exec ai-backend python /app/scripts/test_ethical_ontology.py
```

## API Reference

### POST /api/ethical_check

Evaluates an action against ethical frameworks using the blockchain.

#### Request Body

```json
{
  "action_description": "string (required) - Natural language description of the action to evaluate",
  "agent_id": "string (optional) - Identifier for reputation tracking, default: 'anonymous'",
  "affected_parties": "integer (optional) - Number of people affected, default: 1",
  "time_horizon": "string (optional) - 'short_term', 'medium_term', or 'long_term', default: 'medium_term'",
  "certainty_level": "float (optional) - Confidence in outcome prediction (0.0-1.0), default: 0.7",
  "frameworks": "array (optional) - List of frameworks to evaluate ['deontological', 'virtue_based', 'teleological'], default: all"
}
```

#### Response

```json
{
  "action_description": "...",
  "agent_id": "...",
  "parameters": {
    "affected_parties": 50,
    "time_horizon": "short_term",
    "certainty_level": 0.9
  },
  "frameworks_evaluated": ["deontological", "virtue_based", "teleological"],
  "evaluation_results": {
    "deontological": {
      "compliant": true,
      "confidence": 0.8,
      "reasoning": "No deontological duty violations detected...",
      "rule_applied": "comprehensive_duty_check"
    },
    "virtue_based": {
      "compliant": true,
      "confidence": 0.7,
      "reasoning": "Action demonstrates virtuous character traits...",
      "rule_applied": "virtue_excellence"
    },
    "teleological": {
      "compliant": true,
      "confidence": 0.9,
      "reasoning": "Action is predicted to produce net positive outcomes...",
      "rule_applied": "utility_maximization"
    }
  },
  "overall_assessment": {
    "compliant": true,
    "confidence": 0.8,
    "recommendation": "Action approved"
  },
  "blockchain_info": {
    "network_id": "ethical-ontology-api",
    "chain_length": 2,
    "contracts_deployed": ["deontological", "virtue_based", "teleological"],
    "transaction_recorded": true
  },
  "timestamp": 1234567890.123
}
```

## Smart Contract Details

### Deontological Smart Contract

Evaluates actions against duty-based moral rules:

- **Do Not Lie** - Detects deceptive communication
- **Keep Promises** - Checks commitment fulfillment 
- **Respect Autonomy** - Validates consent and self-determination
- **Do Not Steal** - Protects property rights
- **Do Not Harm** - Prevents unnecessary suffering

**Methods:**
- `check_compliance(action_description)` - Main evaluation method
- `check_universalizability(maxim)` - Kant's categorical imperative test
- `get_rule_statistics()` - Usage analytics

### Virtue-Based Reputation Contract

Tracks character virtues and maintains agent reputation:

- **Honesty** vs Deceitfulness
- **Courage** vs Cowardice/Rashness  
- **Compassion** vs Callousness
- **Justice** vs Injustice
- **Temperance** vs Overindulgence
- **Wisdom** vs Foolishness

**Methods:**
- `check_compliance(action_description, agent_id)` - Virtue evaluation with reputation tracking
- `assess_golden_mean(virtue, intensity)` - Aristotelian golden mean analysis
- `get_agent_reputation(agent_id)` - Retrieve reputation profile
- `get_reputation_leaderboard(limit)` - Top-ranked agents

### Teleological Outcome Contract

Evaluates actions based on predicted consequences:

- **Human Wellbeing** - Health, happiness, life satisfaction
- **Personal Autonomy** - Freedom, choice, self-determination
- **Social Justice** - Fairness, equality, distribution
- **Knowledge & Truth** - Education, understanding, accuracy
- **Environmental Impact** - Sustainability, conservation
- **Social Cohesion** - Community, trust, cooperation

**Methods:**
- `check_compliance(action_description, affected_parties, time_horizon, certainty_level)` - Utility analysis
- `update_actual_outcome(prediction_id, actual_outcomes, actual_utility)` - Learning from results
- `simulate_outcome_scenario(base_action, modifications)` - Scenario comparison
- `get_prediction_accuracy_metrics()` - Model performance

## Configuration

### Environment Variables

Configure the blockchain through environment variables in `backend/backend.env`:

```bash
# Network settings
ETHICAL_ONTOLOGY_NETWORK_ID=ethical-ontology-local
ETHICAL_ONTOLOGY_BLOCKCHAIN_ENDPOINT=http://localhost:8545
ETHICAL_ONTOLOGY_BLOCK_TIME_SECONDS=10

# Auto-deployment
ETHICAL_CONTRACTS_AUTO_DEPLOY=true
ETHICAL_CONTRACTS_DEONTIC_RULES_AUTO_DEPLOY=true
ETHICAL_CONTRACTS_VIRTUE_REPUTATION_AUTO_DEPLOY=true
ETHICAL_CONTRACTS_TELEOLOGICAL_OUTCOMES_AUTO_DEPLOY=true

# Gas limits
ETHICAL_CONTRACTS_DEONTIC_RULES_GAS_LIMIT=500000
ETHICAL_CONTRACTS_VIRTUE_REPUTATION_GAS_LIMIT=750000
ETHICAL_CONTRACTS_TELEOLOGICAL_OUTCOMES_GAS_LIMIT=1000000
```

### Network Configuration

The blockchain network is configured in `ethical_ontology/config/network_config.py`:

- **Validator Nodes** - Mine blocks and validate transactions
- **Peer Nodes** - Participate in consensus without mining
- **Observer Nodes** - Read-only access to blockchain data

Default configuration includes:
- `validator_1` (port 8545) - Primary validator
- `peer_1` (port 8546) - Consensus participant  
- `peer_2` (port 8547) - Consensus participant
- `observer_1` (port 8548) - Read-only observer

## Development

### Adding New Ethical Rules

1. **Extend Smart Contracts** - Add new rules to existing contracts:

```python
# In ethical_ontology/chaincode/deontic_rule.py
self.rules["new_rule"] = {
    "rule_id": "deontic_006",
    "rule_name": "New Ethical Rule",
    "description": "Description of the rule",
    "keywords": ["keyword1", "keyword2"],
    "weight": 0.8
}
```

2. **Create New Contracts** - Implement specialized ethical frameworks:

```python
# Create ethical_ontology/chaincode/care_ethics.py
from .base_contract import BaseSmartContract

class CareEthicsContract(BaseSmartContract):
    def check_compliance(self, action_description, **kwargs):
        # Implement care ethics evaluation
        pass
```

3. **Update Configuration** - Register new contracts:

```python
# In ethical_ontology/config/contract_config.py
self.contracts["care_ethics"] = ContractConfig(
    contract_name="CareEthicsContract",
    contract_class="ethical_ontology.chaincode.care_ethics.CareEthicsContract",
    ethical_framework=EthicalFramework.CARE_BASED,
    # ... other config
)
```

### Testing

Run the comprehensive test suite:

```bash
# Unit tests for individual contracts
python -m pytest tests/test_contracts.py

# Integration tests with blockchain
python scripts/test_ethical_ontology.py --local --verbose

# API endpoint tests
python scripts/test_ethical_ontology.py --api-url http://localhost:5000 --verbose
```

## Troubleshooting

### Common Issues

1. **Import Errors** - Ensure the project root is in Python path:
```bash
export PYTHONPATH=/path/to/Ethics_Dash:$PYTHONPATH
```

2. **Port Conflicts** - Modify ports in docker-compose.yml or network config

3. **Contract Deployment Failures** - Check gas limits and contract syntax

4. **API Connection Issues** - Verify backend is running and blockchain service is healthy

### Debugging

Enable verbose logging:

```bash
# In deployment
python scripts/ethical_ontology_deploy.py --network ethical-ontology-local --verbose

# In testing  
python scripts/test_ethical_ontology.py --local --verbose
```

Check blockchain state:

```python
from ethical_ontology.blockchain.core import EthicalOntologyBlockchain

blockchain = EthicalOntologyBlockchain()
print(f"Chain length: {blockchain.get_chain_length()}")
print(f"Contracts: {list(blockchain.smart_contracts.keys())}")
print(f"Valid chain: {blockchain.is_chain_valid()}")
```

## Security Considerations

1. **Input Validation** - All user inputs are sanitized and validated
2. **Contract Isolation** - Each contract runs in isolated execution context
3. **Transaction Integrity** - All evaluations are recorded immutably
4. **Access Control** - API endpoints include proper authentication (when configured)
5. **Data Privacy** - Sensitive evaluation data can be anonymized

## Future Enhancements

1. **Real Hyperledger Fabric Integration** - Replace simulation with actual Fabric network
2. **Advanced Consensus Mechanisms** - Implement PBFT, PoS, or other algorithms
3. **Multi-Party Evaluation** - Enable collaborative ethical assessments
4. **AI Model Integration** - Use LLMs for more sophisticated rule evaluation
5. **Regulatory Compliance** - Add frameworks for specific industry regulations
6. **Performance Optimization** - Implement caching and batch processing

## References

- Paper: "Toward Decentralized Ethical AI Governance and Verification: A Strategic Roadmap"
- Hyperledger Fabric Documentation: https://hyperledger-fabric.readthedocs.io/
- Ethereum Smart Contracts: https://ethereum.org/en/developers/docs/smart-contracts/
- Ethics in AI: https://www.partnershiponai.org/

## Support

For technical support or questions about the Ethical Ontology Blockchain:

1. Check the deployment logs: `docker-compose logs ethical-ontology-blockchain`
2. Run diagnostic tests: `python scripts/test_ethical_ontology.py --verbose`
3. Review configuration: Ensure environment variables are properly set
4. Consult this documentation and the referenced paper for design decisions

## License

This implementation is part of the Ethics Dashboard project and follows the same licensing terms. 