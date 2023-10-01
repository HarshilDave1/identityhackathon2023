import copy
from math import log, exp
import random


def initialize_trust_scores(attestations):
    for attestation in attestations:
        # Initialize trust score for attestation
        attestation.Ta = 0  # Initialization to 0

        # Initialize trust score for claim
        claim = list(attestation.data.keys())[0]
        attestation.Tc = {claim: 0}  # Initialization to 0

        # Initialize trust score for identity (attester)
        attestation.Ti_attester[claim] = 0.9 if random.choice([True, False]) else 0


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


def check_convergence(previous_attestations, current_attestations, convergence_threshold):
    # Check if the difference between previous and current trust scores is below the convergence threshold
    for prev_attestation, curr_attestation in zip(previous_attestations, current_attestations):
        # Check convergence for Ta
        if abs(prev_attestation.Ta - curr_attestation.Ta) >= convergence_threshold:
            return False
        
        # Check convergence for Tc
        for claim, Tc_value in prev_attestation.Tc.items():
            if abs(Tc_value - curr_attestation.Tc[claim]) >= convergence_threshold:
                return False
        
        # Check convergence for Ti_recipient
        for claim, Ti_value in prev_attestation.Ti_recipient.items():
            if abs(Ti_value - curr_attestation.Ti_recipient[claim]) >= convergence_threshold:
                return False
        
        # If you also store Ti_attester in each attestation and want to check convergence for it:
        # for claim, Ti_value in prev_attestation.Ti_attester.items():
        #     if abs(Ti_value - curr_attestation.Ti_attester[claim]) >= convergence_threshold:
        #         return False
    
    return True


def trust_attestations(trust_identity_attester, attestation):
    # Inputs: trust_identity of the attester
    # Outputs: Ta - the trust score of the attestation
    d = 0.9  # Coefficient predefined in paper
    confidence = 1  # Confidence factor from attester in attestation
    claim = list(attestation.data.keys())[0]
    Ta = trust_identity_attester[claim] * d * confidence
    return Ta


def trust_claims(input_attestation,linked_attestations):
    # Inputs: All of the attestations linked to that claim
    # Outputs: Tc - the trust of the claim
    # The function must find all of the isTrue attestations linked to the previous attestation
    s = log(0.5) / 20  # Assuming the base of the logarithm is e
    
    Ta_sum = sum(attestation.Ta for attestation in linked_attestations) + input_attestation.Ta
    
    exponent = s * Ta_sum * len(linked_attestations)
    Tc = 1 - exp(exponent)
    return Tc



def trust_identities(input_attestation,linked_attestations):
    # Inputs: All of the attestations linked to an identity
    # Outputs: Dictionary with Ti for each claim of the identity
    
    claim = list(input_attestation.data.keys())[0] 
    Ui = input_attestation.Tc  # Intermediary variable. Sum of trust score of all linked attestations for this claim
    issuers = set()  # Set to keep track of distinct attestation issuers 
    for attestation in linked_attestations:
        issuers.add(attestation.attester)  # Add the issuer of the attestation to the set
       
        Ui[claim] = Ui[claim] + attestation.Tc[claim]  # Sum up the Tc values for each claim
    
    n = len(linked_attestations)  # Number of linked attestations
    l = len(issuers)  # Number of distinct attestation issuers
    
    # Calculate Ti for each claim
    Ui_sum = {claim: Ui_value * n * l for claim, Ui_value in Ui.items()}
    
    # Use math below to calculate Ti
    Ti = {}
    for claim, Ui_value in Ui_sum.items():
        k = -0.001
        f = 500
        Ti[claim] = (1-exp(k*(Ui_value-f)))/(1+exp(k*(Ui_value-f)))*0.5+0.5
    
    return Ti




def calculate_trust(attestations, num_rounds=10, convergence_threshold=0.01):
    initialize_trust_scores(attestations)
    previous_attestations = copy.deepcopy(attestations)  # Deep copy to avoid reference issues
    
    for round in range(num_rounds):
        for attestation in attestations:
            # Calculate Ta using trust_identity of the attester
            attestation.Ta = trust_attestations(attestation.Ti_attester, attestation)
            
            # Find linked attestations for claim and calculate Tc
            linked_attestations_for_claim = find_linked_attestations_for_claim(attestations, attestation.uid)
            claim = list(attestation.data.keys())[0]  # Since each attestation contains only one claim
            attestation.Tc[claim] = trust_claims(attestation,linked_attestations_for_claim)

            
            # Find linked attestations for recipient and calculate Ti
            linked_attestations_for_identity = find_linked_attestations_for_identity(attestations, attestation.recipient)
            attestation.Ti_recipient = trust_identities(attestation,linked_attestations_for_identity)
        
        # Check convergence
        if check_convergence(previous_attestations, attestations, convergence_threshold):
            break
        
        previous_attestations = copy.deepcopy(attestations)
    
    return attestations

