from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import time
import traceback
from lib.Colors import Colors
from lib.Encryption import Encryption
import os
import json
import jsonschema


class HenoBase:
    ChickChar = "\U0001f425"

    def __init__(self, password):
        self.web3 = Web3()
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        self.contract_chargepod_address = "0xA899050674ABC1EC6F433373d55466342c27Db76"
        self.contract_staking_address = "0xA16C7963be1d90006A1D36c39831052A89Bc97BE"
        self.contract_nft_address = "0xCEaA5d6418198D827279313f0765d67d3ac4D61f"
        self.contract_zico_address = "0x486ebcFEe0466Def0302A944Bd6408cD2CB3E806"

        with open("abi/abi_chargepod.json", "r") as file:
            self.contract_chargepod = self.web3.eth.contract(
                address=self.contract_chargepod_address, abi=file.read()
            )

        with open("abi/abi_stake.json", "r") as file:
            self.contract_staking = self.web3.eth.contract(
                address=self.contract_staking_address, abi=file.read()
            )

        with open("abi/abi_nft.json", "r") as file:
            self.contract_nft = self.web3.eth.contract(
                address=self.contract_nft_address, abi=file.read()
            )

        with open("abi/abi_zico.json", "r") as file:
            self.contract_zico = self.web3.eth.contract(
                address=self.contract_zico_address, abi=file.read()
            )

        config_schema = {
            "type": "object",
            "properties": {
                "Config": {
                    "type": "object",
                    "properties": {
                        "max_transaction_attempts": {"type": "integer", "minimum": 1},
                        "random_action_on_fail": {"type": "integer", "minimum": 0},
                        "delay": {"type": "number", "minimum": 0},
                        "debug": {"type": "boolean"},
                        "rpc": {"type": "string"},
                    },
                    "required": [
                        "max_transaction_attempts",
                        "random_action_on_fail",
                        "delay",
                    ],
                },
                "Henomorphs": {
                    "type": "array",
                    "uniqueItems": True,
                    "minItems": 1,
                    "items": {
                        "required": ["CollectionID", "TokenID", "Action"],
                        "properties": {
                            "CollectionID": {
                                "type": "integer",
                                "minimum": 2,
                                "maximum": 3,
                            },
                            "TokenID": {"type": "integer", "minimum": 2},
                            "Action": {"type": "integer", "minimum": 0, "maximum": 5},
                        },
                    },
                },
            },
            "required": ["Config", "Henomorphs"],
        }

        with open("userdata/config.json", "r") as file:
            j = json.load(file)
            jsonschema.validate(instance=j, schema=config_schema)
            self.config = j["Config"]
            self.tokens = j["Henomorphs"]

        if (
            self.config["random_action_on_fail"]
            >= self.config["max_transaction_attempts"]
        ):
            raise Exception(
                "random_action_on_fail must be smaller than max_transaction_attempts"
            )

        self.debug_mode = self.config.get("debug", False)
        self.node_url = self.config.get("rpc", "https://polygon-rpc.com")

        with open("userdata/privkey.bin", "rb") as file:
            self.private_key = Encryption.decrypt(file.read(), password).decode("utf-8")
            PA = self.web3.eth.account.from_key(self.private_key)
            self.public_address = PA.address

        self.web3.provider = Web3.HTTPProvider(self.node_url)

        if self.web3.is_connected():
            print("-" * 50)
            print(f"{Colors.OKBLUE}Connection Successful{Colors.ENDC}")
            print("-" * 50)
        else:
            print("-" * 50)
            print(f"{Colors.FAIL}Connection Failed{Colors.ENDC}")
            print("-" * 50)
            raise Exception("Connection Failed")

    @staticmethod
    def SaveKey(key, password):
        try:
            Web3().eth.account.from_key(key)
        except:
            print(f"{Colors.FAIL}This is not valid Ethereum private key!{Colors.ENDC}")
            exit()
        with open("userdata/privkey.bin", "wb") as file:
            file.write(Encryption.encrypt(key.encode("utf-8"), password))

    @staticmethod
    def IsKeySaved():
        return os.path.isfile("userdata/privkey.bin")

    def Transaction(self, function):
        # Call the function
        call_function = function.build_transaction(
            {
                "chainId": self.web3.eth.chain_id,
                "from": self.public_address,
                "nonce": self.web3.eth.get_transaction_count(self.public_address),
            }
        )

        if self.debug_mode:
            print("call_function:")
            print(call_function)

        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(
            call_function, private_key=self.private_key
        )

        # Send transaction
        send_tx = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for transaction receipt
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
        if self.debug_mode:
            print(tx_receipt)  # Optional
        if tx_receipt["status"] != 1:
            raise Exception("Transaction failed")

    def TryAction(self, func: callable, p) -> bool:
        attemptsLeft = self.config["max_transaction_attempts"]
        while attemptsLeft > 0:
            try:
                func(attemptsLeft, p)
                attemptsLeft = -1
            except Exception as e:
                print(f"{Colors.FAIL}[Error]")
                print(f"{e}{Colors.ENDC}")
                if self.debug_mode:
                    print(Colors.FAIL, end="")
                    traceback.print_exc()
                    print(Colors.ENDC)
                attemptsLeft -= 1
                if attemptsLeft > 0:
                    print("Retrying...", end=" ", flush=True)
                time.sleep(self.config["delay"])
        return attemptsLeft == -1
