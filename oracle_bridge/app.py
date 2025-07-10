from flask import Flask, jsonify, request
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

web3_url = os.getenv('PVB_WEB3_URL', 'http://ganache:8545')
submission_contract_address = os.getenv('SUBMISSION_CONTRACT_ADDRESS')

w3 = Web3(Web3.HTTPProvider(web3_url))

# Minimal ABI for verifySubmission
submission_abi = [
    {
        "inputs": [{"name": "_dataHash", "type": "bytes32"}],
        "name": "verifySubmission",
        "outputs": [
            {"name": "deviceId", "type": "bytes32"},
            {"name": "verifierAddress", "type": "address"},
            {"name": "dataHash", "type": "bytes32"},
            {"name": "signature", "type": "string"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "dataUri", "type": "string"},
            {"name": "metadata", "type": "string"},
            {"name": "isVerified", "type": "bool"},
            {"name": "blockNumber", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

submission_contract = w3.eth.contract(address=submission_contract_address, abi=submission_abi)

@app.route('/verify_pvb_data', methods=['GET'])
def verify_pvb_data():
    data_hash = request.args.get('data_hash')
    if not data_hash:
        return jsonify({'error': 'data_hash parameter required'}), 400
    
    try:
        data_hash_bytes = w3.to_bytes(hexstr=data_hash)
        result = submission_contract.functions.verifySubmission(data_hash_bytes).call()
        
        response = {
            'device_id': result[0].hex(),
            'verifier_address': result[1],
            'data_hash': result[2].hex(),
            'signature': result[3],
            'timestamp': result[4],
            'data_uri': result[5],
            'metadata': result[6],
            'is_verified': result[7],
            'block_number': result[8]
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 