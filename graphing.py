import networkx as nx
import matplotlib.pyplot as plt


def create_network_graph(wallet_addresses, attestations):
    G = (
        nx.DiGraph()
    )  # Directed graph, as attestations are directional from attester to recipient

    for attestation in attestations:
        attester = attestation.attester
        recipient = attestation.recipient

        # Add nodes
        G.add_node(attester, role=wallet_addresses[attester])
        G.add_node(recipient, role=wallet_addresses[recipient])

        # Add edge
        G.add_edge(attester, recipient, uid=attestation.uid, isTrue=attestation.isTrue)

    return G


def draw_network_graph(G):
    pos = nx.spring_layout(G)  # Positioning of nodes
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=700,
        node_color="skyblue",
        font_size=10,
        font_weight="bold",
        arrowsize=20,
    )

    # Draw edge labels
    edge_labels = {
        (u, v): f"{d['uid']}:{d['isTrue']}" for u, v, d in G.edges(data=True)
    }
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")

    plt.show()


# Example Usage
# attestations = [...]  # List of attestations
# wallet_addresses = {...}  # Dictionary of wallet addresses and their roles
