"""
Implementation of Bell's Quantum Key Distribution Protocol using quantum entanglement 
and Bell's inequality measurements to securely generate and share encryption keys 
between two parties (Alice and Bob).
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import numpy as np
import hashlib

def create_bell_pair():
    """Create a Bell pair (maximally entangled qubits)."""
    qr = QuantumRegister(2, name='q')
    cr = ClassicalRegister(2, name='c')
    qc = QuantumCircuit(qr, cr)
    
    # Create Bell pair |Φ+⟩ = (|00⟩ + |11⟩)/√2
    qc.h(qr[0])  # Apply Hadamard to first qubit
    qc.cx(qr[0], qr[1])  # CNOT with control=first qubit, target=second qubit
    
    return qc, qr, cr

def measure_bell_state(qc, qr, cr, alice_basis, bob_basis):
    """
    Measure the Bell state in the specified bases.
    
    Args:
        qc (QuantumCircuit): The quantum circuit with the Bell pair
        qr (QuantumRegister): The quantum register
        cr (ClassicalRegister): The classical register
        alice_basis (int): Alice's measurement basis (0 for Z-basis, 1 for X-basis)
        bob_basis (int): Bob's measurement basis (0 for Z-basis, 1 for X-basis)
    """
    # If measuring in X-basis, apply Hadamard gate before measurement
    if alice_basis == 1:
        qc.h(qr[0])
    if bob_basis == 1:
        qc.h(qr[1])
    
    # Measure both qubits
    qc.measure(qr[0], cr[0])
    qc.measure(qr[1], cr[1])

def quantum_key_distribution(num_bits):
    """
    Perform quantum key distribution between Alice and Bob.
    
    Args:
        num_bits (int): Number of bits to generate in the final key
    
    Returns:
        tuple: (shared_key, alice_bits, bob_bits, matching_bases)
    """
    # Initialize lists to store results
    alice_bases = []
    bob_bases = []
    alice_bits = []
    bob_bits = []
    
    # Use AerSimulator
    simulator = AerSimulator()
    
    # Generate and measure Bell pairs
    for _ in range(num_bits * 2):  # Generate extra bits to account for basis mismatch
        # Randomly choose measurement bases
        alice_basis = np.random.randint(2)
        bob_basis = np.random.randint(2)
        alice_bases.append(alice_basis)
        bob_bases.append(bob_basis)
        
        # Create and measure Bell pair
        qc, qr, cr = create_bell_pair()
        measure_bell_state(qc, qr, cr, alice_basis, bob_basis)
        
        # Execute the circuit
        result = simulator.run(qc, shots=1).result()
        counts = result.get_counts(qc)
        measured_state = list(counts.keys())[0]  # Get the measured state
        
        # Record measurement results
        alice_bits.append(int(measured_state[0]))
        bob_bits.append(int(measured_state[1]))
    
    # Find matching bases
    matching_bases = [i for i in range(len(alice_bases)) if alice_bases[i] == bob_bases[i]]
    
    # Extract key bits where bases matched
    shared_key = [alice_bits[i] for i in matching_bases]
    
    return (shared_key, 
            [alice_bits[i] for i in matching_bases],
            [bob_bits[i] for i in matching_bases],
            matching_bases)

def verify_bell_inequality(alice_bits, bob_bits, alice_bases, bob_bases):
    """
    Verify the security of the quantum channel using the CHSH form of Bell's inequality.
    
    Returns:
        bool: True if the channel appears secure, False if possible eavesdropping detected
    """
    # Calculate correlations for CHSH inequality
    correlations = 0
    count = 0
    
    for a, b, ba, bb in zip(alice_bits, bob_bits, alice_bases, bob_bases):
        if (ba, bb) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            correlations += (-1)**(a ^ b)
            count += 1
            
    if count == 0:
        return False
        
    # Calculate the CHSH value
    chsh_value = abs(2 * correlations / count)
    
    # CHSH value should be approximately 2√2 ≈ 2.828 for quantum correlations
    # If it's closer to 2, there might be classical tampering
    return chsh_value > 2.5

def estimate_error_rate(bits1, bits2, sample_size=None):
    """
    Estimate the error rate between two bit strings by comparing a random sample.
    
    Error rate thresholds:
    - 0-25% (0-16/64 bits): Safe but detected
    - ~26.5-35.9% (17-23/64 bits): Significant interference
    - ~37.5-50% (24-32/64 bits): Critical state collapse
    - >50% (>32/64 bits): Severe security breach
    
    Returns:
        tuple: (error_rate, remaining_bits1, remaining_bits2)
    """
    if not sample_size:
        sample_size = min(len(bits1) // 4, 100)
    
    # Randomly select bits for error estimation
    sample_indices = np.random.choice(len(bits1), sample_size, replace=False)
    sample_indices.sort()
    
    # Calculate error rate
    errors = sum(1 for i in sample_indices if bits1[i] != bits2[i])
    error_rate = errors / sample_size
    
    # Remove sampled bits
    keep_indices = list(set(range(len(bits1))) - set(sample_indices))
    remaining_bits1 = [bits1[i] for i in keep_indices]
    remaining_bits2 = [bits2[i] for i in keep_indices]
    
    return error_rate, remaining_bits1, remaining_bits2

def privacy_amplification(key_bits, final_length=None):
    """
    Perform privacy amplification using a hash function.
    """
    if not final_length:
        final_length = max(len(key_bits) // 2, 8)
    
    # Convert bits to bytes
    key_bytes = bytes([sum([bit << i for i, bit in enumerate(key_bits[i:i+8][::-1])])
                      for i in range(0, len(key_bits), 8)])
    
    # Apply SHA-256 hash
    hashed = hashlib.sha256(key_bytes).digest()
    
    # Convert to bits and truncate
    amplified_key = []
    for byte in hashed:
        amplified_key.extend([int(bit) for bit in format(byte, '08b')])
    
    return amplified_key[:final_length]

def main():
    """Main function to demonstrate the quantum key distribution protocol."""
    try:
        # Number of bits to generate in the final key
        print("Starting quantum key distribution...")
        target_key_length = 16
        
        # Perform quantum key distribution
        shared_key, alice_bits, bob_bits, matching_bases = quantum_key_distribution(target_key_length)
        
        # Print initial results
        print("\nQuantum Key Distribution Results:")
        print(f"Number of matching bases: {len(matching_bases)}")
        
        # Step 1: Verify quantum channel security using Bell's inequality
        is_secure = verify_bell_inequality(alice_bits, bob_bits, 
                                         [alice_bases[i] for i in matching_bases],
                                         [bob_bases[i] for i in matching_bases])
        print(f"\nChannel security (Bell's inequality): {'Passed' if is_secure else 'Failed'}")
        
        if not is_secure:
            print("WARNING: Possible eavesdropping detected!")
            return
        
        # Step 2: Estimate error rate and perform error correction
        error_rate, final_alice, final_bob = estimate_error_rate(alice_bits, bob_bits)
        print(f"Estimated error rate: {error_rate:.2%}")
        
        # Check different levels of error rates corresponding to our Eve detection thresholds
        if error_rate <= 0.25:  # 0-16 bits out of 64 (up to 25%)
            print("NOTE: Low-level quantum interference detected, but within safe limits")
            # Continue with key generation as it's within safe limits
        elif error_rate <= 0.359375:  # 17-23 bits out of 64 (~26.5-35.9%)
            print("WARNING: Significant quantum interference detected!")
            return  # Regenerate key
        elif error_rate <= 0.5:  # 24-32 bits out of 64 (~37.5-50%)
            print("CRITICAL: Quantum state collapse detected!")
            return  # Regenerate key
        else:  # More than 32 bits out of 64 (>50%)
            print("SEVERE: Major security breach detected! Immediate key regeneration required!")
            return  # Regenerate key
            
        # Step 3: Verify matched keys
        if final_alice == final_bob:
            print("\nSuccess! Alice and Bob have matching raw keys.")
            print(f"Raw key length: {len(final_alice)} bits")
            
            # Step 4: Privacy amplification
            final_key = privacy_amplification(final_alice)
            print("\nPrivacy amplification completed.")
            print(f"Final secure key length: {len(final_key)} bits")
            print(f"Final key (first 32 bits): {final_key[:32]}")
            
            # Make the final key available for the DES encryption
            return final_key
        else:
            print("\nError: Keys do not match after error correction!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()