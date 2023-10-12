import random
import time


class Attestation:
    def __init__(self, uid, time, recipient, attester, data, isTrue=None):
        self.uid = uid
        self.time = time
        self.recipient = recipient
        self.attester = attester
        self.data = data  # This will hold the claims
        self.isTrue = (
            isTrue  # This will hold the uid of the attestation being attested to
        )
        self.Ti_attester = {}  # Initialize as an empty dictionary
        self.Ta = 0
        self.Tc = 0
        self.Ti_recipient = {}

def print_trusted_wallet_addresses(wallet_addresses):
    print("Trusted Wallet Addresses:")
    for address, properties in wallet_addresses.items():
        if properties["role"] == "trusted":
            print(address)

# Define Wallet Addresses and their roles
def generate_wallet_addresses(num_wallets, dishonest_ratio=0.1, trusted_ratio=0.2):
    # num_wallets: Total number of wallet addresses to generate
    # dishonest_ratio: The ratio of dishonest addresses to generate
    # trusted_ratio: The ratio of trusted addresses to generate

    wallet_addresses = {}
    num_dishonest = int(num_wallets * dishonest_ratio)
    num_trusted = int(num_wallets * trusted_ratio)
    num_honest = num_wallets - num_dishonest - num_trusted

    for i in range(1, num_wallets + 1):
        if i <= num_dishonest:
            role = "dishonest"
        elif i <= num_dishonest + num_trusted:
            role = "trusted"
        else:
            role = "honest"
        
        is_safe = random.choice([True, False])
        if role == "dishonest": 
            is_safe = False
        is_unsafe = not is_safe
        creditworthiness = random.random()
        if role == 'trusted':
            wallet_addresses[f"address{i}"] = {
                "role": role,
                "is_safe": True,
                "is_unsafe": False,
                "creditworthiness": creditworthiness,
                "calculated_trust": {
                    "is_safe": 1,
                    "is_unsafe": 1,
                    "creditworthiness": 1,
                },  
            }
        else:
            wallet_addresses[f"address{i}"] = {
                "role": role,
                "is_safe": is_safe,
                "is_unsafe": is_unsafe,
                "creditworthiness": creditworthiness,
                "calculated_trust": {
                    "is_safe": 0,
                    "is_unsafe": 0,
                    "creditworthiness": 0,
                },  
            }
        
    return wallet_addresses



# Generate Attestations
def generate_attestations(num_attestations, wallet_addresses, attestations=[]):
    while len(attestations) < num_attestations:
        attester = random.choice(list(wallet_addresses.keys()))
        recipient = random.choice(list(wallet_addresses.keys()))
        while recipient == attester:  # Ensure recipient and attester are different
            recipient = random.choice(list(wallet_addresses.keys()))

        uid = len(attestations) + 1
        attestation_time = time.time()  # Current time in seconds since the Epoch

        # If there are previous attestations, randomly decide whether to attest to one
        isTrue = None
        if attestations and random.choice([ True, False]):
            pick = random.choice(attestations)
            isTrue = pick.uid
            while pick.isTrue: #Attestations cannot be nested. (attestations of attestations of attestations)
                pick = random.choice(attestations)
                isTrue = pick.uid
                
            recipient = None  # Set recipient to None
            data = {str(isTrue): attestations[isTrue - 1].data}  # Match data in receiving attestation. -1 for python index
            attestation = Attestation(
                            uid, attestation_time, recipient, attester, data, isTrue
                        )
            attestations.append(attestation)
        else:
            # Select a random claim type
            claim_type = random.choice(["is_safe"])
            if claim_type == "creditworthiness":
                claim_value = random.randint(0, 100)  # Random creditworthiness score
            else:
                if wallet_addresses[attester]["role"] == "honest" or wallet_addresses[attester]["role"] == "trusted"  and recipient is not None:
                    if wallet_addresses[recipient][claim_type]: #Only allow True attestations.
                        claim_value = wallet_addresses[recipient][claim_type]
                        data = {claim_type: claim_value}
                        attestation = Attestation(
                            uid, attestation_time, recipient, attester, data, isTrue
                        )
                        attestations.append(attestation)
                        #print(f'True attestation {attestation.uid}')
                    else:
                        continue
                elif wallet_addresses[attester]["role"] == "dishonest":
                    claim_value = random.choice([True, False])  # Random boolean value
                    #print(f'Dishonest {attester} saying {claim_value}')

                    data = {claim_type: claim_value}

                    attestation = Attestation(
                        uid, attestation_time, recipient, attester, data, isTrue
                    )
                    attestations.append(attestation)
       
    return attestations



# Main Function
def main():
    num_wallets = 10
    wallet_addresses = generate_wallet_addresses(num_wallets)
    attestations = generate_attestations(
        100, wallet_addresses
    )  # Generate 100 attestations
    # Print the generated attestations for review
    for attestation in attestations:
        print(
            f"Attestation UID: {attestation.uid}, Attester: {attestation.attester}, Recipient: {attestation.recipient}, Data: {attestation.data}, isTrue: {attestation.isTrue}"
        )


if __name__ == "__main__":
    main()
