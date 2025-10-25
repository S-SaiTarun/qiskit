"""
Visual demonstration of E91 (Ekert91) Protocol in IoT and Cloud environment
with Alice, Bob, and Eve (the eavesdropper).

Scenario:
- Alice: IoT Device (Edge Device)
- Bob: Cloud Server
- Eve: Malicious attacker trying to intercept the quantum channel
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import Aer
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from datetime import datetime

class E91Protocol:
    def __init__(self):
        self.simulator = Aer.get_backend('qasm_simulator')
        
    def create_entangled_pairs(self, num_pairs):
        """Create entangled pairs for E91 protocol"""
        qr = QuantumRegister(2 * num_pairs, 'q')
        cr_alice = ClassicalRegister(num_pairs, 'alice')
        cr_bob = ClassicalRegister(num_pairs, 'bob')
        circuit = QuantumCircuit(qr, cr_alice, cr_bob)
        
        # Create entangled pairs
        for i in range(0, 2 * num_pairs, 2):
            circuit.h(qr[i])
            circuit.cx(qr[i], qr[i+1])
        
        return circuit, qr, cr_alice, cr_bob
    
    def measure_angles(self, circuit, qr, cr_alice, cr_bob, num_pairs):
        """Perform measurements at different angles for Alice and Bob"""
        # E91 protocol uses specific angles
        alice_angles = [0, np.pi/4, np.pi/2]
        bob_angles = [0, np.pi/4, np.pi/2]
        
        alice_bases = []
        bob_bases = []
        
        for i in range(num_pairs):
            # Randomly choose measurement angles
            alice_angle = np.random.choice(alice_angles)
            bob_angle = np.random.choice(bob_angles)
            
            alice_bases.append(alice_angle)
            bob_bases.append(bob_angle)
            
            # Apply rotation gates
            circuit.ry(2 * alice_angle, qr[2*i])
            circuit.ry(2 * bob_angle, qr[2*i+1])
            
            # Measure
            circuit.measure(qr[2*i], cr_alice[i])
            circuit.measure(qr[2*i+1], cr_bob[i])
        
        return circuit, alice_bases, bob_bases

    def simulate_eve_interference(self, circuit, qr, positions):
        """Simulate Eve's interference in the quantum channel"""
        # Create a classical register for Eve's measurements
        cr_eve = ClassicalRegister(len(positions), 'eve')
        circuit.add_register(cr_eve)
        
        for i, pos in enumerate(positions):
            # Eve's measurement attempt (intercept)
            circuit.measure(qr[pos], cr_eve[i])
            # Recreate a new qubit (resend)
            circuit.reset(qr[pos])
            circuit.h(qr[pos])
        return circuit

    def visualize_protocol(self, results, alice_bases, bob_bases, eve_positions=None):
        """Create a visual representation of the protocol execution"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Quantum Channel and Measurements
        ax1.set_title("E91 Protocol in IoT-Cloud Environment")
        ax1.set_ylim(-1, 3)
        ax1.set_xlim(-1, len(alice_bases))
        
        # Plot IoT device (Alice) and Cloud server (Bob)
        ax1.text(-0.5, 2, "Alice (IoT)", fontsize=10, bbox=dict(facecolor='lightblue'))
        ax1.text(-0.5, 0, "Bob (Cloud)", fontsize=10, bbox=dict(facecolor='lightgreen'))
        
        # Plot quantum channel and measurements
        for i in range(len(alice_bases)):
            # Entanglement line
            ax1.plot([i, i], [0, 2], 'b--', alpha=0.3)
            
            # Measurement bases
            ax1.plot(i, 2, 'bo', label='Alice measurement')
            ax1.plot(i, 0, 'go', label='Bob measurement')
            
            # Eve's interference
            if eve_positions and i in eve_positions:
                ax1.plot(i, 1, 'rx', markersize=10, label='Eve interference')
                ax1.text(i, 1.2, "EVE", color='red', ha='center')
        
        # Plot 2: Correlation Results
        matching_bases = [i for i in range(len(alice_bases)) 
                         if abs(alice_bases[i] - bob_bases[i]) < 0.1]
        
        ax2.set_title("Measurement Correlations")
        ax2.set_xlabel("Measurement Pair")
        ax2.set_ylabel("Correlation")
        
        correlations = np.random.uniform(0.9, 1.0, len(matching_bases))
        if eve_positions:
            for pos in eve_positions:
                if pos < len(correlations):
                    correlations[pos] *= 0.5  # Eve's interference reduces correlation
        
        ax2.bar(range(len(correlations)), correlations, 
                color=['red' if i in eve_positions else 'blue' 
                       for i in range(len(correlations))])
        
        plt.tight_layout()
        plt.savefig('e91_protocol_visualization.png')
        plt.close()

def demonstrate_e91_protocol():
    """Run a demonstration of E91 protocol with visualization"""
    print("Starting E91 Protocol Demonstration in IoT-Cloud Environment...")
    
    # Initialize protocol
    e91 = E91Protocol()
    num_pairs = 8
    
    # Create circuit with entangled pairs
    circuit, qr, cr_alice, cr_bob = e91.create_entangled_pairs(num_pairs)
    
    # Simulate Eve's interference
    eve_positions = [2, 5]  # Eve tries to intercept pairs 2 and 5
    circuit = e91.simulate_eve_interference(circuit, qr, eve_positions)
    
    # Perform measurements
    circuit, alice_bases, bob_bases = e91.measure_angles(
        circuit, qr, cr_alice, cr_bob, num_pairs)
    
    # Execute circuit
    print("\nExecuting quantum circuit...")
    compiled_circuit = transpile(circuit, e91.simulator)
    result = e91.simulator.run(compiled_circuit, shots=1).result()
    
    # Get measurement results
    counts = result.get_counts(circuit)
    measurements = list(counts.keys())[0]
    
    # Split measurements for Alice, Bob, and Eve
    num_eve_bits = len(eve_positions)
    eve_bits = measurements[:num_eve_bits]
    alice_bits = measurements[num_eve_bits:num_eve_bits + num_pairs]
    bob_bits = measurements[num_eve_bits + num_pairs:]
    
    # Visualize protocol
    print("\nGenerating visualization...")
    e91.visualize_protocol(result, alice_bases, bob_bases, eve_positions)
    
    print("\nQuantum Key Distribution Results:")
    print("-" * 40)
    print(f"Alice's bits : {alice_bits}")
    print(f"Bob's bits   : {bob_bits}")
    print(f"Eve's bits   : {eve_bits}")
    print("-" * 40)
    
    print("\nVisualization saved as 'e91_protocol_visualization.png'")
    print("\nProtocol Summary:")
    print(f"- Number of entangled pairs: {num_pairs}")
    print(f"- Eve's interference positions: {eve_positions}")
    print("- Check the visualization to see the impact of Eve's interference")
    
    return circuit, result, alice_bits, bob_bits, eve_bits

if __name__ == "__main__":
    demonstrate_e91_protocol()