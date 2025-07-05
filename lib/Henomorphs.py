from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from tabulate import tabulate
from datetime import datetime
import time
import traceback
from lib.XorEncryption import XorEncryption
from lib.Colors import Colors
import os
import random
import json
import jsonschema


class Henomorphs:
    def __init__(self, password):
        self.web3 = Web3()
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        contract_chargepod_address = (
            "0xA899050674ABC1EC6F433373d55466342c27Db76"  # chargepod
        )
        contract_staking_address = (
            "0xA16C7963be1d90006A1D36c39831052A89Bc97BE"  # staking
        )
        contract_nft_address = "0xCEaA5d6418198D827279313f0765d67d3ac4D61f"  # nft

        with open("abi/abi_chargepod.json", "r") as file:
            self.contract_chargepod = self.web3.eth.contract(
                address=contract_chargepod_address, abi=file.read()
            )

        with open("abi/abi_stake.json", "r") as file:
            self.contract_staking = self.web3.eth.contract(
                address=contract_staking_address, abi=file.read()
            )

        with open("abi/abi_nft.json", "r") as file:
            self.contract_nft = self.web3.eth.contract(
                address=contract_nft_address, abi=file.read()
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

        with open("config.json", "r") as file:
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

        with open("privkey.bin", "rb") as file:
            self.private_key = XorEncryption.Decrypt(file.read(), password)
            PA = self.web3.eth.account.from_key(self.private_key)
            self.public_address = PA.address

        self.web3.provider = Web3.HTTPProvider(self.node_url)

        if self.web3.is_connected():
            print("-" * 50)
            print(f"{Colors.OKBLUE}Connection Successful{Colors.ENDC}")
            print("-" * 50)
        else:
            print(f"{Colors.FAIL}Connection Failed{Colors.ENDC}")

    @staticmethod
    def SaveKey(key, password):
        with open("privkey.bin", "wb") as file:
            file.write(XorEncryption.Encrypt(key, password))

    @staticmethod
    def IsKeySaved():
        return os.path.isfile("privkey.bin")

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

    def TryAction(self, func, p):
        attemptsLeft = self.config["max_transaction_attempts"]
        while attemptsLeft > 0:
            try:
                func(attemptsLeft, p)
                attemptsLeft = 0
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
            data = self.contract_chargepod.functions.checkBiopodCalibration(
                t["CollectionID"], t["TokenID"]
            ).call()
            data = list(data[1])
            data.pop(1)
            data[0] = f"({t['CollectionID']}) {data[0]}"
            for i in [2, 5, 9]:
                data[i] = datetime.fromtimestamp(int(data[i])).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            d.append(data)
            print("\U0001f425", end=" ", flush=True)
        print()
        print(tabulate(d, headers=headers))

    def Inspect(self):
        def _Inspect(_, p):
            print("Performing core Inspection: ", end=" ", flush=True)
            self.Transaction(self.contract_nft.functions.inspect(p[0], p[1]))
            print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")

        tokensToInspect = [[], []]
        print("Getting data...")
        for token in self.tokens:
            data = self.contract_chargepod.functions.checkBiopodCalibration(
                token["CollectionID"], token["TokenID"]
            ).call()[1]
            print("\U0001f425", end=" ", flush=True)
            t = int(time.time()) - int(data[10])
            if t <= 12 * 60 * 60:
                tr = 12 * 60 * 60 - t
                print(
                    f"{Colors.WARNING}Cannot inspect token ({token['CollectionID']}, {token['TokenID']}). Next inspection possible in: {int(tr / 60 / 60):02d}:{int((int(tr / 60)) - 60 * int(tr / 60 / 60)):02d}{Colors.ENDC}"
                )
            else:
                tokensToInspect[0].append(token["CollectionID"])
                tokensToInspect[1].append(token["TokenID"])
        print()

        if len(tokensToInspect[0]) == 0:
            print(f"{Colors.WARNING}No tokens availabe to inspect!{Colors.ENDC}")
            return

        self.TryAction(_Inspect, tokensToInspect)

    def PerformColonyAction(self):
        def _PerformColonyAction(attempt, t):
            if t["Action"] <= 0:
                print(f"{Colors.WARNING}Token without action, skipping.{Colors.ENDC}")
                return
            data = self.contract_chargepod.functions.getLastTokenAction(
                t["CollectionID"], t["TokenID"]
            ).call()
            if int(time.time()) <= int(data[2]):
                tr = int(data[2]) - int(time.time())
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), token in cooldown preiod. Next action possible in: {int(tr / 60 / 60):02d}:{int((int(tr / 60)) - 60 * int(tr / 60 / 60)):02d}{Colors.ENDC}"
                )
            elif int(time.time()) - int(data[1]) <= 60 * 60:
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), was performed action recently.{Colors.ENDC}"
                )
            else:
                action = t["Action"]
                if (
                    self.config["max_transaction_attempts"] - attempt
                    >= self.config["random_action_on_fail"]
                    and self.config["random_action_on_fail"] > 0
                ):
                    action = random.randint(1, 5)
                print(
                    f"Performing action: ({t['CollectionID']}, {t['TokenID']}), {action}",
                    end=" ",
                    flush=True,
                )
                self.Transaction(
                    self.contract_chargepod.functions.performAction(
                        int(t["CollectionID"]), int(t["TokenID"]), int(action)
                    )
                )
                print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")
                time.sleep(self.config["delay"])

        for t in self.tokens:
            self.TryAction(_PerformColonyAction, t)

    def RepairWear(self, threshold, reduction):
        def _RepairWear(_, t):
            data = self.contract_chargepod.functions.getRepairStatus(
                t["CollectionID"], t["TokenID"]
            ).call()
            if int(data[2]) >= int(threshold) and int(data[2]) > 0:
                r = min(reduction, int(data[2]))
                print(
                    f"Performing wear repair: ({t['CollectionID']}, {t['TokenID']}), Reduction: {r}",
                    end=" ",
                    flush=True,
                )
                self.Transaction(
                    self.contract_staking.functions.repairTokenWear(
                        int(t["CollectionID"]), int(t["TokenID"]), int(r)
                    )
                )
                print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")
                time.sleep(self.config["delay"])
            else:
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), dont need repair wear.{Colors.ENDC}"
                )

        for t in self.tokens:
            self.TryAction(_RepairWear, t)

    def RepairCharge(self, threshold, repair):
        def _RepairCharge(_, t):
            data = self.contract_chargepod.functions.getRepairStatus(
                t["CollectionID"], t["TokenID"]
            ).call()
            toRepair = int(data[1]) - int(data[0])
            if toRepair >= int(threshold) and toRepair > 0:
                r = min(repair, int(toRepair))
                print(
                    f"Performing charge repair: ({t['CollectionID']}, {t['TokenID']}), Repair: {r}",
                    end=" ",
                    flush=True,
                )
                self.Transaction(
                    self.contract_chargepod.functions.repairCharge(
                        int(t["CollectionID"]), int(t["TokenID"]), int(r)
                    )
                )
                print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")
                time.sleep(self.config["delay"])
            else:
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), dont need repair charge.{Colors.ENDC}"
                )

        for t in self.tokens:
            self.TryAction(_RepairCharge, t)

    def ClaimAll(self):
        def _ClaimAll(*_):
            print("Claiming all rewards: ", end=" ", flush=True)
            self.Transaction(self.contract_staking.functions.claimAllRewards())
            print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")

        self.TryAction(_ClaimAll, None)

    def GetPendingRewards(self):
        data = self.contract_staking.functions.calculateAccuratePendingRewards(
            self.public_address, False
        ).call()
        return data[0] / 1000000000000000000
