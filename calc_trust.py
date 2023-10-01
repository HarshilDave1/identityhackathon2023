import copy
from math import log, exp
import random


def initialize_trust_scores(attestations):
    # Initialize trust scores for each attestation (Ta), claim (Tc), and identity (Ti) to some default value
    trust_scores = {
        "Ta": {},  # Trust scores for attestations
        "Tc": {},  # Trust scores for claims
        "Ti": {},  # Trust scores for identities
    }

    for attestation in attestations:
        # Initialize trust score for attestation
        trust_scores["Ta"][attestation.uid] = 0  # Initialization to 0

        # Initialize trust score for claim
        # Assuming attestation.data contains the claim information
        for claim in attestation.data.keys():
            trust_scores["Tc"][claim] = 0  # Initialization to 0

        # Initialize trust score for identity (attester)
        attester = attestation.attester
        # Check if the attester is already in the dictionary
        if attester not in trust_scores["Ti"]:
            trust_scores["Ti"][
                attester
            ] = {}  # Initialize as an empty dictionary if not present

        # Randomly assign some attesters a value of 0.9
        for claim in attestation.data.keys():
            trust_scores["Ti"][attester][claim] = (
                0.9 if random.choice([True, False]) else 0
            )

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
            if score_type == "Ti":  # For "Ti", we have nested dictionaries
                for claim, claim_score in score.items():
                    if (
                        abs(claim_score - previous_trust_scores[score_type][uid][claim])
                        >= convergence_threshold
                    ):
                        return False
            else:  # For "Ta" and "Tc", we have single-level dictionaries
                if (
                    abs(score - previous_trust_scores[score_type][uid])
                    >= convergence_threshold
                ):
                    return False
    return True


def trust_attestations(trust_identity_attester, attestation):
    # Inputs: trust_identity of the attester
    # Outputs: Ta - the trust score of the attestation
    d = 0.9  # Coefficient predefined in paper
    confidence = 1  # Confidence factor from attester in attestation
    claim = list(attestation.data.keys())[0]
    Ta = trust_identity_attester[claim] * d * confidence
    return Ta


def trust_claims(linked_attestations, attestation_trust_scores):
    # Inputs: All of the attestations linked to that claim
    # Outputs: Tc - the trust of the claim
    # The function must find all of the isTrue attestations linked to the previous attestation

    Ta_sum = sum(
        attestation_trust_scores[attestation.uid] for attestation in linked_attestations
    )
    s = log(0.5) / 20  # Assuming the base of the logarithm is e
    exponent = s * Ta_sum * len(linked_attestations)
    Tc = 1 - exp(exponent)
    return Tc


def trust_identities(linked_attestations, attestation_claim_scores):
    # Inputs: All of the attestations linked to an identity
    # Outputs: Dictionary with Ti for each claim of the identity

    Ti = {}
    for attestation in linked_attestations:
        claim = list(attestation.data.keys())[
            0
        ]  # Since each attestation contains only one claim
        Ti[claim] = attestation_claim_scores[
            claim
        ]  # Assign the Tc value of the claim to Ti

    return Ti


def calculate_trust(attestations, num_rounds=10, convergence_threshold=0.01):
    trust_scores = initialize_trust_scores(attestations)

    for round in range(num_rounds):
        previous_trust_scores = copy.deepcopy(
            trust_scores
        )  # Deep copy to avoid reference issues

        for attestation in attestations:
            # Calculate Ta using trust_identity of the attester
            Ta = trust_attestations(
                trust_scores["Ti"][attestation.attester], attestation
            )
            trust_scores["Ta"][attestation.uid] = Ta  # Update Ta in trust_scores

            # Find linked attestations for claim and calculate Tc
            linked_attestations_for_claim = find_linked_attestations_for_claim(
                attestations, attestation.uid
            )
            claim = list(attestation.data.keys())[
                0
            ]  # Since each attestation contains only one claim
            Tc = trust_claims(linked_attestations_for_claim, trust_scores["Ta"])
            trust_scores["Tc"][claim] = Tc  # Update Tc in trust_scores

            # Find linked attestations for recipient and calculate Ti
            linked_attestations_for_identity = find_linked_attestations_for_identity(
                attestations, attestation.recipient
            )
            Ti_recipient = trust_identities(
                linked_attestations_for_identity, trust_scores["Tc"]
            )

            # Update Ti in trust_scores for each claim of the recipient
            for claim, Ti_value in Ti_recipient.items():
                trust_scores["Ti"][attestation.recipient][claim] = Ti_value

        # Check convergence
        if check_convergence(
            previous_trust_scores, trust_scores, convergence_threshold
        ):
            break

    return trust_scores
