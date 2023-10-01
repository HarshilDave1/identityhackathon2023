import copy
from math import log


def initialize_trust_scores(attestations):
    # Initialize trust scores for each attestation (Ta), claim (Tc), and identity (Ti) to some default value
    trust_scores = {
        "Ta": {},  # Trust scores for attestations
        "Tc": {},  # Trust scores for claims
        "Ti": {},  # Trust scores for identities
    }

    for attestation in attestations:
        # Initialize trust score for attestation
        trust_scores["Ta"][attestation.uid] = 0.1  # Example initialization

        # Initialize trust score for claim
        # Assuming attestation.data contains the claim information
        for claim in attestation.data.keys():
            trust_scores["Tc"][claim] = 0.1  # Example initialization

        # Initialize trust score for identity (recipient)
        recipient = attestation.recipient
        trust_scores["Ti"][recipient] = 0.1  # Example initialization

        # Initialize trust score for identity (attester)
        attester = attestation.attester
        trust_scores["Ti"][attester] = 0.1  # Example initialization

    return trust_scores


def find_linked_attestations_for_claim(attestations, target_attestation_uid):
    # Find all attestations that have said isTrue about the given attestation
    linked_attestations = [
        attestation
        for attestation in attestations
        if attestation.isTrue == target_attestation_uid
    ]
    return linked_attestations


def find_linked_attestations_for_identity(attestations, identity):
    # Find all attestations linked to the given identity
    linked_attestations = [
        attestation for attestation in attestations if attestation.recipient == identity
    ]
    return linked_attestations


def check_convergence(previous_trust_scores, trust_scores, convergence_threshold):
    # Check if the difference between previous and current trust scores is below the convergence threshold
    for score_type in ["Ta", "Tc", "Ti"]:
        for uid, score in trust_scores[score_type].items():
            if (
                abs(score - previous_trust_scores[score_type][uid])
                >= convergence_threshold
            ):
                return False
    return True


def trust_attestations(trust_identity_attester):
    # Inputs: trust_identity of the attester
    # Outputs: Ta - the trust score of the attestation
    d = 0.9  # Coefficient predefined in paper
    confidence = 1  # Confidence factor from attester in attestation
    Ta = trust_identity_attester * d * confidence
    return Ta


def trust_claims(linked_attestations, attestation_trust_scores):
    # Inputs: All of the attestations linked to that claim
    # Outputs: Tc - the trust of the claim
    # The function must find all of the isTrue attestations linked to the previous attestation

    Ta_sum = sum(
        attestation_trust_scores[attestation.uid] for attestation in linked_attestations
    )
    s = log(0.5) / 20  # Assuming the base of the logarithm is e
    Tc = s * Ta_sum
    return Tc


def trust_identities(linked_attestations, attestation_claim_scores):
    # Inputs: All of the attestations linked to an identity
    # Outputs: Ti - the trust of the identity
    # The actual math will be implemented by the user
    Tc_sum = sum(
        attestation_claim_scores[attestation.uid] for attestation in linked_attestations
    )
    Ti = Tc_sum  # Placeholder
    return Ti


def calculate_trust(attestations, num_rounds=10, convergence_threshold=0.01):
    trust_scores = initialize_trust_scores(attestations)

    for round in range(num_rounds):
        previous_trust_scores = copy.deepcopy(
            trust_scores
        )  # Deep copy to avoid reference issues

        for attestation in attestations:
            # Calculate Ta using trust_identity of the attester
            Ta = trust_attestations(trust_scores["Ti"][attestation.attester])
            trust_scores["Ta"][attestation.uid] = Ta  # Update Ta in trust_scores

            # Find linked attestations for claim and calculate Tc
            linked_attestations_for_claim = find_linked_attestations_for_claim(
                attestations, attestation.uid
            )
            Tc = trust_claims(linked_attestations_for_claim, trust_scores["Ta"])
            for claim in attestation.data.keys():
                trust_scores["Tc"][claim] = Tc  # Update Tc in trust_scores

            # Find linked attestations for recipient and calculate Ti
            linked_attestations_for_identity = find_linked_attestations_for_identity(
                attestations, attestation.recipient
            )
            Ti_recipient = trust_identities(
                linked_attestations_for_identity, trust_scores["Tc"]
            )
            trust_scores["Ti"][
                attestation.recipient
            ] = Ti_recipient  # Update Ti in trust_scores for recipient

            # Find linked attestations for attester and calculate Ti
            linked_attestations_for_identity = find_linked_attestations_for_identity(
                attestations, attestation.attester
            )
            Ti_attester = trust_identities(linked_attestations_for_identity)
            trust_scores["Ti"][
                attestation.attester
            ] = Ti_attester  # Update Ti in trust_scores for attester

        # Check convergence
        if check_convergence(
            previous_trust_scores, trust_scores, convergence_threshold
        ):
            break

    return trust_scores
