"""
Optimized Flask-based Quantum-Secure Communication API Server.
Maintains full quantum security features with alternative implementation strategies.
"""

from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import traceback
import random
import base64
import os
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from concurrent.futures import ThreadPoolExecutor
import threading
from functools import lru_cache

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

def _build_cors_actual_response(response_body):
    response = jsonify(response_body)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# Thread-safe cache with locks
class ThreadSafeCache:
    def __init__(self):
        self._cache = {
            "keys": {
                "classic": None,
                "quantum": None,
                "eve": None
            },
            "circuits": [],
            "measurements": {},
            "qber_history": []
        }
        self._lock = threading.Lock()
    
    def get(self, key, subkey=None):
        with self._lock:
            if subkey:
                if key not in self._cache or not isinstance(self._cache[key], dict):
                    return None
                return self._cache[key].get(subkey)
            return self._cache.get(key)
    
    def set(self, key, subkey, value=None):
        """Set a value in the cache. If value is None, treat subkey as the value and ignore any third parameter."""
        with self._lock:
            if value is None:
                # Two-parameter version: set(key, value)
                self._cache[key] = subkey
            else:
                # Three-parameter version: set(key, subkey, value)
                if key not in self._cache:
                    self._cache[key] = {}
                if not isinstance(self._cache[key], dict):
                    self._cache[key] = {}
                self._cache[key][subkey] = value
    
    def clear(self):
        with self._lock:
            self.__init__()

cache = ThreadSafeCache()

# Quantum Circuit Pool for reuse
class QuantumCircuitPool:
    def __init__(self, pool_size=5):
        self.pool_size = pool_size
        self.simulator = AerSimulator()
        self.circuits = []
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        for _ in range(self.pool_size):
            qr = QuantumRegister(2, 'q')
            cr = ClassicalRegister(2, 'c')
            qc = QuantumCircuit(qr, cr)
            qc.h(qr[0])
            qc.cx(qr[0], qr[1])
            self.circuits.append(qc)
    
    def get_circuit(self):
        with self.lock:
            if not self.circuits:
                self._initialize_pool()
            return self.circuits.pop() if self.circuits else self._create_new_circuit()
    
    def _create_new_circuit(self):
        qr = QuantumRegister(2, 'q')
        cr = ClassicalRegister(2, 'c')
        qc = QuantumCircuit(qr, cr)
        qc.h(qr[0])
        qc.cx(qr[0], qr[1])
        return qc
    
    def return_circuit(self, circuit):
        with self.lock:
            if len(self.circuits) < self.pool_size:
                circuit.data.clear()
                circuit.h(circuit.qubits[0])
                circuit.cx(circuit.qubits[0], circuit.qubits[1])
                self.circuits.append(circuit)

circuit_pool = QuantumCircuitPool()

class OptimizedQuantumDES:
    """Optimized DES implementation with quantum key handling"""
    def __init__(self, key_bits):
        # Convert bits to bytes for DES key (use first 64 bits or pad if shorter)
        key_bytes = []
        bits = key_bits + [0] * (64 - len(key_bits))  # Pad to 64 bits if needed
        for i in range(0, 64, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            key_bytes.append(byte)
        self.key = bytes(key_bytes)

    def encrypt(self, message):
        cipher = DES.new(self.key, DES.MODE_ECB)
        padded_data = pad(message.encode(), DES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted).decode()

    def decrypt(self, encrypted_message):
        cipher = DES.new(self.key, DES.MODE_ECB)
        encrypted = base64.b64decode(encrypted_message)
        decrypted = cipher.decrypt(encrypted)
        return unpad(decrypted, DES.block_size).decode()

def calculate_qber(key1, key2):
    """Calculate quantum bit error rate"""
    if not key1 or not key2 or len(key1) != len(key2):
        return 0.0
    return sum(1 for a, b in zip(key1, key2) if a != b) / len(key1)

def generate_quantum_key(length=64):
    """Generate simulated quantum key"""
    simulator = AerSimulator()
    key = []
    circuit = circuit_pool.get_circuit()
    
    for _ in range(length):
        circuit.measure_all()
        result = simulator.run(circuit).result()
        counts = result.get_counts(circuit)
        # Get the most common measurement result
        measurement = max(counts.items(), key=lambda x: x[1])[0]
        key.append(int(measurement[0]))  # Take first bit
        circuit.data.clear()  # Reset circuit
        circuit.h(circuit.qubits[0])
        circuit.cx(circuit.qubits[0], circuit.qubits[1])
        
    circuit_pool.return_circuit(circuit)
    return key

@app.route('/init_keys', methods=['GET', 'POST', 'OPTIONS'])
def init_keys():
    """Initialize keys with parallel processing"""
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    try:
        # Generate classic and quantum keys in parallel
        with ThreadPoolExecutor() as executor:
            classic_future = executor.submit(lambda: [random.randint(0, 1) for _ in range(64)])
            quantum_future = executor.submit(generate_quantum_key)
            eve_future = executor.submit(generate_quantum_key)
            
            classic_key = classic_future.result()
            quantum_key = quantum_future.result()
            eve_bits = eve_future.result()
        
        # Calculate QBER
        qber = calculate_qber(quantum_key, eve_bits)
        
        # Update cache
        cache.set("keys", "classic", classic_key)
        cache.set("keys", "quantum", quantum_key)
        cache.set("keys", "eve", eve_bits)
        
        return _build_cors_actual_response({
            "classic_key": classic_key,
            "quantum_key": quantum_key,
            "qber": qber
        })
    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Print to console
        app.logger.error(error_msg)  # Log to Flask logger
        return _build_cors_actual_response({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/encrypt', methods=['POST', 'OPTIONS'])
def encrypt():
    """Encrypt a message using simplified encryption"""
    try:
        data = request.json
        if not data or 'message' not in data or 'key_type' not in data:
            return _build_cors_actual_response({"error": "Missing required parameters"}), 400
            
        message = data['message']
        key_type = data['key_type']
        
        if key_type not in ['classic', 'quantum']:
            return _build_cors_actual_response({"error": "Invalid key type"}), 400
        
        current_key = cache.get("keys", key_type)
        if not current_key:
            return _build_cors_actual_response({"error": f"No {key_type} key initialized"}), 400
        
        cipher = OptimizedQuantumDES(current_key)
        encrypted_msg = cipher.encrypt(message)
        
        return _build_cors_actual_response({
            "encrypted_msg": encrypted_msg,
            "key_used": current_key[:16]  # Return first 16 bits for display
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/decrypt', methods=['POST', 'OPTIONS'])
def decrypt():
    """Decrypt a message using simplified decryption"""
    try:
        data = request.json
        if not data or 'encrypted_msg' not in data or 'key_type' not in data:
            return _build_cors_actual_response({"error": "Missing required parameters"}), 400
            
        encrypted_msg = data['encrypted_msg']
        key_type = data['key_type']
        
        if key_type not in ['classic', 'quantum']:
            return _build_cors_actual_response({"error": "Invalid key type"}), 400
            
        current_key = cache.get("keys", key_type)
        if not current_key:
            return _build_cors_actual_response({"error": f"No {key_type} key initialized"}), 400
        
        cipher = OptimizedQuantumDES(current_key)
        decrypted_msg = cipher.decrypt(encrypted_msg)
        
        return _build_cors_actual_response({
            "decrypted_msg": decrypted_msg
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/eve_attack', methods=['POST', 'OPTIONS'])
def eve_attack():
    """Simplified Eve attack simulation"""
    try:
        data = request.json
        if not data or 'key_type' not in data:
            return _build_cors_actual_response({"error": "Missing required parameters"}), 400
            
        key_type = data['key_type']
        if key_type not in ['classic', 'quantum']:
            return _build_cors_actual_response({"error": "Invalid key type"}), 400
            
        current_key = cache.get("keys", key_type)
        eve_key = cache.get("keys", "eve")
        if not current_key or not eve_key:
            return _build_cors_actual_response({"error": "Keys not initialized"}), 400
        
        # For classic key, more realistic cracking simulation
        if key_type == 'classic':
            # Generate a new random key for Eve's attempt
            eve_attempt_key = [random.randint(0, 1) for _ in range(64)]
            cache.set("keys", "eve", eve_attempt_key)
            
            # In classic crypto, Eve might get parts of the key right through brute force
            correct_bits = random.randint(32, 58)  # Getting 50-90% of bits correct
            for i in range(correct_bits):
                bit_pos = random.randint(0, 63)
                eve_attempt_key[bit_pos] = current_key[bit_pos]
            
            # High number of matching bits indicates successful crack
            matches = sum(a == b for a, b in zip(current_key, eve_attempt_key))
            success = matches > 48  # More than 75% bits matched
            
            if success:
                cache.set("keys", "eve", current_key)  # Eve got the full key
                return jsonify({
                    "status": "cracked",
                    "log_msg": f"Classic encryption cracked! Eve obtained the key. ({matches}/64 bits matched)",
                    "eve_key": current_key[:16]
                })
            else:
                return jsonify({
                    "status": "progress",
                    "log_msg": f"Brute force attempt: {matches}/64 bits matched in classic key.",
                    "eve_key": eve_attempt_key[:16]
                })
        
        # For quantum key, simulate brute force attempts but with quantum effects
        else:
            # Generate Eve's attempt at guessing the quantum key
            eve_attempt_key = [random.randint(0, 1) for _ in range(64)]
            cache.set("keys", "eve", eve_attempt_key)
            
            # Calculate matches, but with quantum uncertainty
            matches = sum(a == b for a, b in zip(current_key, eve_attempt_key))
            
            # Very low matches (0-16 bits) - Eve's attempt was ineffective but detected
            if matches <= 16:
                return jsonify({
                    "status": "detected_safe",
                    "log_msg": f"Quantum interference detected but within safe limits. No key regeneration needed. ({matches}/64 bits matched)",
                    "eve_key": eve_attempt_key[:16]
                })
            # Matches above safe threshold (17+ bits) - Concerning interference detected
            elif matches < 24:
                # Generate new quantum key automatically
                new_quantum_key = generate_quantum_key()
                cache.set("keys", "quantum", new_quantum_key)
                return jsonify({
                    "status": "detected_reinit",
                    "log_msg": f"Significant quantum interference detected! Key compromised and regenerated. ({matches}/64 bits matched)",
                    "eve_key": eve_attempt_key[:16],
                    "new_quantum_key": new_quantum_key
                })
            # High matches (24-32 bits) - Serious breach attempt detected
            elif matches < 32:
                # Generate new quantum key automatically
                new_quantum_key = generate_quantum_key()
                cache.set("keys", "quantum", new_quantum_key)
                return jsonify({
                    "status": "detected_reinit",
                    "log_msg": f"Critical quantum state collapse! Key must be regenerated. ({matches}/64 bits matched)",
                    "eve_key": eve_attempt_key[:16],
                    "new_quantum_key": new_quantum_key
                })
            # Extreme breach (32+ bits) - Severe security compromise
            else:
                # Generate new quantum key automatically
                new_quantum_key = generate_quantum_key()
                cache.set("keys", "quantum", new_quantum_key)
                return jsonify({
                    "status": "detected_reinit",
                    "log_msg": f"SEVERE SECURITY BREACH! {matches}/64 bits matched - Immediate key regeneration required!",
                    "eve_key": eve_attempt_key[:16],
                    "new_quantum_key": new_quantum_key
                })
        
        # For quantum key, calculate QBER
        current_key = cache.get("keys", key_type)
        eve_key = cache.get("keys", "eve")
        qber = calculate_qber(current_key, eve_key) if current_key and eve_key else 0.0
        if qber > 0.11:  # Threshold for security
            return _build_cors_actual_response({
                "status": "detected",
                "log_msg": "Quantum interference detected! Key discarded.",
                "eve_key": eve_key[:16]
            })
        
        return _build_cors_actual_response({
            "status": "failed",
            "log_msg": "Eve's attack failed. Communication remains secure.",
            "eve_key": eve_key[:16]
        })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET', 'OPTIONS'])
def serve_index():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    """Serve the pindex.html file"""
    return send_from_directory('static', 'pindex.html')

if __name__ == '__main__':
    # Create the static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True, port=5001)  # Using different port from main server