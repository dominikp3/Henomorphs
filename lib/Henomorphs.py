from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from tabulate import tabulate
from datetime import datetime
import time
import traceback
from lib.XorEncryption import XorEncryption
import os
import random


class Henomorphs:
    # Initialize endpoint URL
    node_url = "https://polygon-rpc.com"
    max_attempts = 3  # Attempt 3 times if transaction fails
    random_action_on_fail = True

    def __init__(self, password):
        # Create the node connection
        self.web3 = Web3(Web3.HTTPProvider(self.node_url))
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        # Verify if the connection is successful
        if self.web3.is_connected():
            print("-" * 50)
            print("Connection Successful")
            print("-" * 50)
        else:
            print("Connection Failed")

        contract_address = "0xA899050674ABC1EC6F433373d55466342c27Db76"  # chargepod
        contract_address2 = "0xA16C7963be1d90006A1D36c39831052A89Bc97BE"  # staking
        contract_address3 = "0xCEaA5d6418198D827279313f0765d67d3ac4D61f"  # nft

        # Create smart contract instance
        with open("abi/abi_chargepod.json", "r") as file:
            self.contract_chargepod = self.web3.eth.contract(
                address=contract_address, abi=file.read()
            )

        with open("abi/abi_stake.json", "r") as file:
            self.contract_staking = self.web3.eth.contract(
                address=contract_address2, abi=file.read()
            )

        with open("abi/abi_nft.json", "r") as file:
            self.contract_nft = self.web3.eth.contract(
                address=contract_address3, abi=file.read()
            )

        with open("privkey.bin", "rb") as file:
            self.private_key = XorEncryption.Decrypt(file.read(), password)
            PA = self.web3.eth.account.from_key(self.private_key)
            self.public_address = PA.address

        self.tokens = []
        with open("tokens.txt", "r") as file:
            nn = file.read().rstrip().split(",")  # using rstrip to remove the \n
            for n in nn:
                self.tokens.append(int(n))

        self.tokensActions = []
        with open("tokensActions.txt", "r") as file:
            nn = file.read().rstrip().split(",")  # using rstrip to remove the \n
            for n in nn:
                self.tokensActions.append(int(n))

        if len(self.tokens) != len(self.tokensActions):
            raise Exception("mismatch number of tokens and tokens actions")

    @staticmethod
    def SaveKey(key, password):
        with open("privkey.bin", "wb") as file:
            file.write(XorEncryption.Encrypt(key, password))

    @staticmethod
    def IsKeySaved():
        return os.path.isfile("privkey.bin")

    def Transaction(self, function):
        # initialize the chain id, we need it to build the transaction for replay protection
        Chain_id = self.web3.eth.chain_id

        # Call the function
        call_function = function.build_transaction(
            {
                "chainId": Chain_id,
                "from": self.public_address,
                "nonce": self.web3.eth.get_transaction_count(self.public_address),
            }
        )

        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(
            call_function, private_key=self.private_key
        )

        # Send transaction
        send_tx = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for transaction receipt
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
        print(tx_receipt)  # Optional
        if tx_receipt["status"] != 1:
            raise Exception("Transaction failed")

    def _PerformColonyAction(self, itemID, actionID):
        print("Performing action: " + str(itemID) + ", " + str(actionID))
        self.Transaction(
            self.contract_chargepod.functions.performAction(
                2, int(itemID), int(actionID)
            )
        )
        print("Transacion successful")

    def PerformColonyAction(self):
        i = 0
        for t in self.tokens:
            attempt = self.max_attempts
            while attempt > 0:
                try:
                    if self.tokensActions[i] <= 0:
                        print("Token without action, skipping")
                        attempt = 0
                        continue
                    data = self.contract_chargepod.functions.checkBiopodCalibration(
                        2, t
                    ).call()
                    data = list(data[1])
                    if int(time.time()) - int(data[6]) > 60 * 60:
                        action = self.tokensActions[i]
                        if attempt < self.max_attempts and self.random_action_on_fail:
                            action = random.randint(1, 5)
                        self._PerformColonyAction(t, action)
                        time.sleep(3)
                    else:
                        print(
                            "Skipped token "
                            + str(t)
                            + ", was performed action recently"
                        )
                    i += 1
                    attempt = 0
                except Exception as e:
                    print("Error: ")
                    print(e)
                    traceback.print_exc()
                    attempt -= 1
                    if attempt > 0:
                        print("Retrying ...")

    def PrintInfo(self):
        print("Getting data...")
        d = []
        headers = [
            "tokenId",
            # "owner",
            "kinship",
            "lastInteraction",
            "experience",
            "charge",
            "lastCharge",
            "level",
            "prowess",
            "wear",
            "lastRecalibration",
            "calibrationCount",
            "locked",
            "agility",
            "intelligence",
            "bioLevel",
        ]
        for t in self.tokens:
            data = self.contract_chargepod.functions.checkBiopodCalibration(2, t).call()
            data = list(data[1])
            data.pop(1)
            for i in [2, 5, 9]:
                data[i] = datetime.fromtimestamp(int(data[i])).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            d.append(data)
        print(tabulate(d, headers=headers))

    def _Inspect(self):
        print("Performing core Inspection: ")
        self.Transaction(self.contract_nft.functions.inspect(self.tokens))
        print("Transacion successful")

    def Inspect(self):
        attempt = self.max_attempts
        while attempt > 0:
            try:
                self._Inspect()
                attempt = 0
            except Exception as e:
                print("Error: ")
                print(e)
                traceback.print_exc()
                attempt -= 1
                if attempt > 0:
                    print("Retrying ...")

    def _RepairWear(self, itemID, wearReduction):
        print("Performing wear repair: " + str(itemID))
        self.Transaction(
            self.contract_staking.functions.repairTokenWear(
                2, int(itemID), int(wearReduction)
            )
        )
        print("Transacion successful")

    def RepairWear(self, threshold, reduction):
        for t in self.tokens:
            attempt = self.max_attempts
            while attempt > 0:
                try:
                    data = self.contract_chargepod.functions.checkBiopodCalibration(
                        2, t
                    ).call()
                    data = list(data[1])
                    if int(data[9]) >= int(threshold):
                        self._RepairWear(t, reduction)
                    else:
                        print("Skipped token " + str(t) + ", dont need repair wear")
                    attempt = 0
                except Exception as e:
                    print("Error: ")
                    print(e)
                    traceback.print_exc()
                    attempt -= 1
                    if attempt > 0:
                        print("Retrying ...")
