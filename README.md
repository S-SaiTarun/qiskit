# Quantum Key Distribution for IoT-Cloud Security

This project implements a quantum-safe communication system between IoT devices and cloud servers using the E91 quantum key distribution protocol and DES encryption.

## Project Structure

```
D:\githubt\qiskit\
├── keydes.py              # Main implementation file with IoT-Cloud simulation
├── quantum_e91_demo.py    # E91 protocol implementation using Qiskit
├── quantumkey.py         # Quantum key distribution utilities
└── quantum_cryptography_presentation.md  # Documentation and presentation
```

## Dependencies

- Python 3.13+
- Qiskit
- Qiskit-Aer (Quantum circuit simulator)
- PyCryptodome (For DES encryption)
- Matplotlib (For visualization)
- NumPy

Install dependencies using:
```bash
python -m pip install qiskit qiskit-aer pycryptodome matplotlib numpy
```

## Core Components

### 1. keydes.py
Main simulation file that demonstrates secure IoT-Cloud communication.

**Features:**
- Quantum-enhanced DES encryption
- IoT device (Alice) simulation
- Cloud server (Bob) simulation
- Eavesdropper (Eve) detection
- Interactive message encryption/decryption
- Visual demonstration of Eve's failed decryption attempts

**Recent Updates:**
- Added visual representation of Eve's failed decryption attempts with garbled text
- Added side-by-side comparison of original vs Eve's decrypted message
- Implemented continuous message loop with user input
- Added key visualization for Alice, Bob, and Eve
- Enhanced error handling and user feedback

### 2. quantum_e91_demo.py
Implementation of the E91 quantum key distribution protocol.

**Features:**
- Quantum circuit creation for entangled pairs
- Measurement basis selection
- Eve's interference simulation
- Visual representation of quantum channels
- Correlation measurements

**Recent Updates:**
- Fixed quantum circuit measurement compatibility
- Added Eve's measurement collection
- Enhanced visualization of quantum states
- Updated Qiskit imports for latest version
- Added detailed measurement results display

### 3. quantumkey.py
Utility functions for quantum key generation and distribution.

## Usage

1. Start the simulation:
```bash
python keydes.py
```

2. Follow the interactive prompts to:
   - Observe quantum key generation
   - Send encrypted messages
   - See encryption/decryption process
   - Monitor Eve's interference attempts

## Example Communication Flow

```
=== IoT-Cloud Quantum Cryptography Demonstration ===

[Step 1] Quantum Key Distribution

## Visualization of Eve's Failed Decryption

The system now provides a clear visualization of Eve's failed decryption attempts:

```
[ALICE] IoT Device sends:
   Plaintext: Hello World!
   Encrypted: <encrypted data>

[EVE] Spy intercepts message:
   Attempting to decrypt with intercepted bits...
   Eve's garbled decryption: @#$%^&*()_+
   
   Decryption comparison:
   Original : Hello World!
   Eve sees : Ḩ₣ℓ╝◊ ω∩я⌡δ¥
   ⚠️ Eve's key is wrong, resulting in garbage data!

[BOB] Cloud Server receives:
   Decrypted: Hello World!
```

This demonstrates how:
- Eve's incorrect quantum measurements lead to a wrong decryption key
- Attempted decryption produces garbled, unreadable text
- The quantum encryption remains secure despite interception

## Example Communication Flow

```
=== IoT-Cloud Quantum Cryptography Demonstration ===

[Step 1] Quantum Key Distribution
- Alice and Bob establish quantum channel
- Generate entangled quantum pairs
- Perform measurements in random bases
- Detect any eavesdropping attempts

[Step 2] Secure Communication
- Alice encrypts message using quantum key
- Eve attempts to intercept (and fails)
- Bob successfully decrypts message
- Keys are compared for verification

[Step 3] Security Verification
- Check quantum correlations
- Verify Bell's inequality
- Detect any interference
- Ensure secure key establishment
```

## Visualization

The program generates a visualization (`e91_protocol_visualization.png`) showing:
- Quantum channel setup
- Measurement correlations
- Eve's interference points
- Security verification results

## Security Features

1. **Quantum Key Distribution**
   - Uses quantum entanglement
   - Immune to eavesdropping
   - Immediate intrusion detection
   - Perfect forward secrecy

2. **Classical Encryption**
   - DES encryption with quantum-generated keys
   - Secure key refresh mechanism
   - Padding for variable message lengths

3. **Eavesdropping Detection**
   - Real-time interference monitoring
   - Bell's inequality verification
   - Correlation measurements
   - Quantum state disturbance detection

## Recent Updates Log

### October 25, 2025
1. Enhanced visualization of encryption keys
2. Added Eve's decryption attempts
3. Fixed Qiskit compatibility issues
4. Updated quantum circuit measurements
5. Added detailed documentation

### Earlier Updates
1. Initial implementation of E91 protocol
2. Added IoT-Cloud simulation
3. Implemented DES encryption
4. Created visualization system
5. Added interactive message system

## Contributing

Feel free to contribute to this project by:
1. Reporting issues
2. Suggesting enhancements
3. Submitting pull requests
4. Improving documentation
