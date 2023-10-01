import random
import time


# Define Schema
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


# Define Wallet Addresses and their roles
def generate_wallet_addresses(num_wallets, dishonest_ratio=0.2):
    # num_wallets: Total number of wallet addresses to generate
    # dishonest_ratio: The ratio of dishonest addresses to generate

    wallet_addresses = {}
    num_dishonest = int(num_wallets * dishonest_ratio)

    for i in range(1, num_wallets + 1):
        role = "dishonest" if i <= num_dishonest else "honest"
        is_human = random.choice([True, False])
        is_bot = not is_human
        creditworthiness = random.randint(0, 100)

        wallet_addresses[f"address{i}"] = {
            "role": role,
            "is_human": is_human,
            "is_bot": is_bot,
            "creditworthiness": creditworthiness,
        }

    return wallet_addresses


# Generate Attestations
def generate_attestations(num_attestations, wallet_addresses, attestations=[]):
    for _ in range(num_attestations):
        attester = random.choice(list(wallet_addresses.keys()))
        recipient = random.choice(list(wallet_addresses.keys()))
        while recipient == attester:  # Ensure recipient and attester are different
            recipient = random.choice(list(wallet_addresses.keys()))

        uid = len(attestations) + 1
        attestation_time = time.time()  # Current time in seconds since the Epoch

        # Select a random claim type
        claim_type = random.choice(["is_human", "is_bot", "creditworthiness"])
        if claim_type == "creditworthiness":
            claim_value = random.randint(0, 100)  # Random creditworthiness score
        else:
            claim_value = random.choice([True, False])  # Random boolean value

        data = {claim_type: claim_value}

        # If attester is honest, correct the data to be true
        if wallet_addresses[attester]["role"] == "honest":
            if claim_type == "creditworthiness":
                data[claim_type] = wallet_addresses[recipient][claim_type]
            else:
                data[claim_type] = wallet_addresses[recipient][claim_type]

        # If there are previous attestations, randomly decide whether to attest to one
        isTrue = None
        if attestations and random.choice([True, False]):
            isTrue = random.choice(attestations).uid

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
