import numpy as np
import pyphi

# --- Configuration: a simple 2-node deterministic network ---

num_nodes = 2
num_states = 2 ** num_nodes

# Build the transition probability matrix (TPM)
# Each of the 4 possible input states maps deterministically to itself
tpm = np.zeros((num_states, num_nodes), dtype=int)
for state in range(num_states):
    bits = [
        (state >> (num_nodes - 1 - i)) & 1
        for i in range(num_nodes)
    ]
    tpm[state, :] = bits

# Fully connected adjacency for demonstration
connectivity = np.ones((num_nodes, num_nodes), dtype=bool)

# Optional node labels
node_labels = ['node0', 'node1']

# Instantiate the PyPhi network using positional args
NETWORK = pyphi.Network(
    tpm,
    connectivity,
    node_labels
)

