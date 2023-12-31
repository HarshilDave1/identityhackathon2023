import copy
from math import log, exp
import random


def initialize_trust_scores(attestations, wallet_addresses,predefined_claims):
    for attestation in attestations:
        # Initialize trust score for attestation
        attestation.Ta = 0  # Initialization to 0
        
        # Initialize trust score for claim
        claim = list(attestation.data.keys())[0]
        attestation.Tc = {claim: 0}  # Initialization to 0

        # Initialize trust score for identity (attester)
        # Check if the attester is honest
        trusted = wallet_addresses[attestation.attester]['role'] == 'trusted'
        if trusted:
            for claim in predefined_claims:
                attestation.Ti_attester[claim] =  1
                #wallet_addresses[attestation.attester]["calculated_trust"][claim] = attestation.Ti_attester[claim]
        else:
            attestation.Ti_attester[claim]  = 0  
      
def find_linked_attestations_for_claim(attestations, target_attestation_uid):
    # Find all attestations that have said isTrue about the given attestation
    linked_attestations = [
        attestation
        for attestation in attestations
        if attestation.isTrue == target_attestation_uid
    ]
    return linked_attestations


def find_linked_attestations_for_identity(input_attestation, attestations):
    # Find all attestations linked to the given identity and claim
    linked_attestations = [
        attestation for attestation in attestations 
        if attestation.recipient == input_attestation.recipient 
        and attestation.data == input_attestation.data
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
        
    
    return True


def trust_attestations(trust_identity_attester, claim):
    # Inputs: trust_identity of the attester
    # Outputs: Ta - the trust score of the attestation
    d = 0.9  # Coefficient predefined in paper
    confidence = 1  # Confidence factor from attester in attestation. Could be customized per user.
    
    threshold = 0.01
    if trust_identity_attester[claim] > threshold:
        Ta = trust_identity_attester[claim] * d * confidence
    else:
        Ta = 0 
    # print(f'Input Ti {trust_identity_attester[claim] }')
    # print(f'output Ta {Ta}')
    return Ta


def trust_claims(input_attestation,linked_attestations):
    # Inputs: All of the attestations linked to that claim
    # Outputs: Tc - the trust of the claim
    # The function must find all of the isTrue attestations linked to the previous attestation
    s = log(0.5) / 20  # Assuming the base of the logarithm is e
    Ta_sum = sum(attestation.Ta for attestation in linked_attestations) + input_attestation.Ta
    exponent = s * Ta_sum * (len(linked_attestations)+1)
    Tc = round(1 - exp(exponent), ndigits=2)
    # print(f'output Tc {Tc} with {len(linked_attestations)} linked attestations')
    return Tc


def trust_identities(input_attestation,linked_attestations):
    # Inputs: All of the attestations linked to an identity
    # Outputs: Dictionary with Ti for each claim of the identity
    
    claim = list(input_attestation.data.keys())[0] 
    Ui = {claim: 0}   # Intermediary variable. Sum of trust score of all linked attestations for this claim
    Ui[claim] += input_attestation.Tc[claim]
    issuers = set()  # Set to keep track of distinct attestation issuers 
    for attestation in linked_attestations:
        issuers.add(attestation.attester)  # Add the issuer of the attestation to the set
       
        Ui[claim] += attestation.Tc[claim]   # Sum up the Tc values for each claim
    n = len(linked_attestations)  # Number of linked attestations
    l = len(issuers)  # Number of distinct attestation issuers
    # Calculate Ti for each claim
    Ui_sum = {claim: Ui_value * n * l for claim, Ui_value in Ui.items()}
    # Use math below to calculate Ti
    #Ti = {}
    k = -0.01
    f = 500
    Ti = round((1-exp(k*(Ui_sum[claim]-f)))/(1+exp(k*(Ui_sum[claim]-f)))*0.5+0.5 , ndigits=2)
    # print(f'output Ti {Ti} with {len(linked_attestations)} linked claims')
    return Ti


def calculate_trust(attestations, wallet_addresses,predefined_claims = ["is_safe", "is_unsafe", "gitcoinScore"], num_rounds=100, convergence_threshold=0.01):
    initialize_trust_scores(attestations, wallet_addresses,predefined_claims)
    previous_attestations = copy.deepcopy(attestations)  # Deep copy to avoid reference issues
    
    for round in range(num_rounds):
        for attestation in attestations:
            # Calculate Ta using trust_identity of the attester
            
            claim = list(attestation.data.keys())[0]  # Since each attestation contains only one claim
            attester_address = attestation.attester
            if claim in predefined_claims:
                attestation.Ti_attester[claim] = wallet_addresses[attester_address]["calculated_trust"][claim]
            else:
                claim = list(attestation.data[claim].keys())[0]
                attestation.Ti_attester[claim] = wallet_addresses[attester_address]["calculated_trust"][claim]
            
            attestation.Ta = trust_attestations(attestation.Ti_attester, claim)
            
            # Find linked attestations for claim and calculate Tc
            linked_attestations_for_claim = find_linked_attestations_for_claim(attestations, attestation.uid)
            attestation.Tc[claim] = trust_claims(attestation,linked_attestations_for_claim)
            # Find linked attestations for recipient and calculate Ti
            linked_attestations_for_identity = find_linked_attestations_for_identity(attestation,attestations)
            attestation.Ti_recipient[claim] = trust_identities(attestation,linked_attestations_for_identity)
            # Update wallet address trust metrics
            recipient_address = attestation.recipient
            if recipient_address: # address is None if attestation is made to another attestation
                if wallet_addresses[recipient_address]["role"] != "trusted":
                    wallet_addresses[recipient_address]["calculated_trust"][claim] = attestation.Ti_recipient[claim]
        # Check convergence
        if check_convergence(previous_attestations, attestations, convergence_threshold):
            print(f'Converged in {round} rounds!')
            break
        previous_attestations = copy.deepcopy(attestations)
        
    return attestations, wallet_addresses 

