import networkx as nx
import matplotlib.pyplot as plt


def create_network_graph(wallet_addresses, attestations, trust_scores):
    G = (
        nx.DiGraph()
    )  # Directed graph, as attestations are directional from attester to recipient

    for attestation in attestations:
        attester = attestation.attester
        recipient = attestation.recipient

        # Add nodes with trust scores (Ti) as attributes
        G.add_node(
            attester,
            role=wallet_addresses[attester],
            Ti=trust_scores.get(attester, {}).get("Ti", 0),
        )
        G.add_node(
            recipient,
            role=wallet_addresses[recipient],
            Ti=trust_scores.get(recipient, {}).get("Ti", 0),
        )

        # Add edge with trust scores (Ta, Tc) as attributes
        G.add_edge(
            attester,
            recipient,
            uid=attestation.uid,
            isTrue=attestation.isTrue,
            Ta=trust_scores.get(attester, {}).get("Ta", 0),
            Tc=trust_scores.get(attester, {}).get("Tc", 0),
        )

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

    # Draw node labels with trust scores (Ti)
    node_labels = {
        node: f'{node}\nTi={data["Ti"]}' for node, data in G.nodes(data=True)
    }
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_color="black")

    # Draw edge labels with trust scores (Ta, Tc)
    edge_labels = {
        (u, v): f"{d['uid']}\nTa={d['Ta']}\nTc={d['Tc']}"
        for u, v, d in G.edges(data=True)
    }
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")

    plt.show()


# Example Usage
# attestations = [...]  # List of attestations
# wallet_addresses = {...}  # Dictionary of wallet addresses and their roles
# trust_scores = {...}  # Dictionary of trust scores for each attestation, claim, and identity
G = create_network_graph(attestations, trust_scores)
draw_network_graph(G)
