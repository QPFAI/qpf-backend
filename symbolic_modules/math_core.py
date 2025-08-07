#!/usr/bin/env python3
# ────────────────────────────────────────────────────────────────────────────────
# QPF Symbolic Math Core — math_core.py
#
# Core mathematical operations for the Quantum Perception Field
# Including: Activation, State Projection, Entropy, Collapse, Resonance, Feedback
#
# Requires: numpy
# ────────────────────────────────────────────────────────────────────────────────

import numpy as np

# Numerical stability for log/exp
EPS = 1e-12

# ─── Activation (sigmoid) ──────────────────────────────────────────────────────
def activation(w):
    """
    Sigmoid activation: a_i = 1 / (1 + exp(-w_i))
    Args:
        w (np.ndarray): Weight vector, shape (N,)
    Returns:
        a (np.ndarray): Activation vector, shape (N,)
    """
    return 1.0 / (1.0 + np.exp(-w))

# ─── State Vector Projection ───────────────────────────────────────────────────
def project_state(a, psi_vectors):
    """
    Project symbolic state as a weighted sum of basis vectors.
    Args:
        a (np.ndarray): Activation vector, shape (N,)
        psi_vectors (np.ndarray): State/basis vectors, shape (N, D)
    Returns:
        np.ndarray: Projected state vector, shape (D,)
    """
    return np.sum(a[:, None] * psi_vectors, axis=0)

# ─── Entropy Calculation ──────────────────────────────────────────────────────
def entropy(a):
    """
    Computes entropy S = -sum_i (a_i^2 * log(a_i^2))
    Args:
        a (np.ndarray): Activation vector, shape (N,)
    Returns:
        float: Entropy value
    """
    p2 = a ** 2
    return -np.sum(p2 * np.log(p2 + EPS))

# ─── Collapse Update ──────────────────────────────────────────────────────────
def collapse_weights(w, collapsed_index, alpha):
    """
    Update weights on collapse event.
    w_i(t+) = (1 - alpha) * w_i(t-) + alpha * δ_{ik}
    Args:
        w (np.ndarray): Previous weights, shape (N,)
        collapsed_index (int): Index to reinforce (dominant concept)
        alpha (float): Collapse learning rate [0,1]
    Returns:
        np.ndarray: Updated weights, shape (N,)
    """
    w_new = (1.0 - alpha) * w
    w_new[collapsed_index] += alpha
    return w_new

# ─── Resonance Energy ─────────────────────────────────────────────────────────
def resonance(a, W):
    """
    Resonance energy: E = a^T W a
    Args:
        a (np.ndarray): Activation vector, shape (N,)
        W (np.ndarray): Connectivity matrix, shape (N,N)
    Returns:
        float: Resonance energy
    """
    return float(a.T @ W @ a)

# ─── Feedback Modulation ──────────────────────────────────────────────────────
def feedback_modulation(lambda_vec, F):
    """
    Feedback effect (for post-collapse adjustment): λ·F
    Args:
        lambda_vec (np.ndarray): Feedback gain vector, shape (N,)
        F (np.ndarray): Feedback vector, shape (N,)
    Returns:
        float: Feedback sum
    """
    return float(np.dot(lambda_vec, F))

# ─── Utility: Softmax (optional) ──────────────────────────────────────────────
def softmax(x):
    """
    Numerically stable softmax.
    Args:
        x (np.ndarray): Input vector
    Returns:
        np.ndarray: Softmax probabilities
    """
    z = x - np.max(x)
    exp_z = np.exp(z)
    return exp_z / (np.sum(exp_z) + EPS)

# ─── Collapse Trigger ─────────────────────────────────────────────────────────
def check_collapse(S, S_crit):
    """
    Determine whether to trigger collapse.
    Args:
        S (float): Current entropy
        S_crit (float): Collapse threshold
    Returns:
        bool: True if collapse should occur
    """
    return S > S_crit

# ─── Example Usage / Test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    # Example: 5-concept system
    N, D = 5, 3
    w = np.random.randn(N)
    psi = np.random.randn(N, D)
    W = np.random.randn(N, N)
    lambda_vec = np.ones(N) * 0.2
    F = np.random.randn(N)
    alpha = 0.05
    S_crit = 1.5

    a = activation(w)
    print("Activations:", a)
    S = entropy(a)
    print("Entropy:", S)
    print("Collapse?", check_collapse(S, S_crit))
    proj = project_state(a, psi)
    print("Projected state:", proj)
    E = resonance(a, W)
    print("Resonance energy:", E)
    fb = feedback_modulation(lambda_vec, F)
    print("Feedback mod:", fb)
    if check_collapse(S, S_crit):
        w = collapse_weights(w, np.argmax(a), alpha)
        print("Collapsed weights:", w)
