from datetime import timedelta
import math
from pprint import pformat
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import time
import traceback
from lib.Colors import Colors
from lib.DecodedContract import DecodedContract
from lib.Encryption import Encryption
import os
import json
import jsonschema
from lib.HenoAutoGenConfig import HenoAutoGenConfig
from lib.ConfigSchema import config_schema, heno_config_schema, colony_config_schema
from lib.FileLogger import FileLogger
from web3.exceptions import ContractCustomError


class HenoBase:
    ChickChar = "\U0001f425"
    ZicoDividor = 1000000000000000000

    def __init__(
        self, account, password, henoConfFile, configGenOnly=False, colonyConfFile=None
    ):
        self.web3 = Web3()
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        self.contract_chargepod_address = "0xA899050674ABC1EC6F433373d55466342c27Db76"
        self.contract_staking_address = "0xA16C7963be1d90006A1D36c39831052A89Bc97BE"
        self.contract_nft_address = "0xCEaA5d6418198D827279313f0765d67d3ac4D61f"
        self.contract_zico_address = "0x486ebcFEe0466Def0302A944Bd6408cD2CB3E806"
        self.contract_ylw_address = "0x79e60C812161eBcAfF14b1F06878c6Be451CD3Ef"

        self.contract_staking = DecodedContract(
            self.web3, self.contract_staking_address, abi_path="abi/abi_stake.json"
        )
        self.contract_chargepod = DecodedContract(
            self.web3,
            self.contract_chargepod_address,
            abi_path="abi/abi_chargepod.json",
        )

        if not configGenOnly:
            self.contract_nft = DecodedContract(
                self.web3, self.contract_nft_address, abi_path="abi/abi_nft.json"
            )
            self.contract_zico = DecodedContract(
                self.web3, self.contract_zico_address, abi_path="abi/abi_zico.json"
            )
            self.contract_ylw = DecodedContract(
                self.web3, self.contract_ylw_address, abi_path="abi/abi_ylw.json"
            )

        if os.path.isfile("userdata/config.json"):
            with open("userdata/config.json", "r") as file:
                self.config = json.load(file)
                jsonschema.validate(instance=self.config, schema=config_schema)
        else:
            print(
                f"{Colors.WARNING}No config.json file found! Using default config.{Colors.ENDC}"
            )
            self.config = {}

        self.max_transaction_attempts = self.config.get("max_transaction_attempts", 5)
        self.random_action_on_fail = self.config.get("random_action_on_fail", 0)
        self.delay_t = self.config.get("delay", 3)
        self.delay_ai_defender = self.config.get("ai_defender_delay", 600)
        if self.random_action_on_fail >= self.max_transaction_attempts:
            raise Exception(
                "random_action_on_fail must be smaller than max_transaction_attempts"
            )
        self.debug_mode = self.config.get("debug", False)
        self.logger = FileLogger(
            f"userdata/logs/{account}", self.config.get("log", False)
        )
        self.node_url = self.config.get("rpc", "https://polygon-rpc.com")

        self.web3.provider = Web3.HTTPProvider(self.node_url)

        with open(f"userdata/{account}privkey.bin", "rb") as file:
            self.private_key = Encryption.decrypt(file.read(), password).decode("utf-8")
            PA = self.web3.eth.account.from_key(self.private_key)
            self.public_address = PA.address

        print("-" * 50)
        print(f"{Colors.OKBLUE}Wallet: {self.public_address}{Colors.ENDC}")
        if self.config.get("print_priv_key", False):
            print(f"{Colors.FAIL}Private key: {self.private_key}{Colors.ENDC}")

        if self.web3.is_connected():
            print("-" * 50)
            print(f"{Colors.OKBLUE}Connection Successful{Colors.ENDC}")
            print("-" * 50)
        else:
            print("-" * 50)
            print(
                f"{Colors.FAIL}Connection Failed\n Ensure that rpc ({self.node_url}) works or use different one.{Colors.ENDC}"
            )
            print("-" * 50)
            raise Exception("Connection Failed")

        self.logger.log("-" * 100)
        self.logger.log(
            f"Successfully logged in: {self.public_address}, using config: '{henoConfFile}'"
        )

        self.henoConfPath = f"userdata/{account}{henoConfFile}"
        self.colonyConfPath = (
            f"userdata/{account}{colonyConfFile}"
            if colonyConfFile is not None
            else None
        )
        if configGenOnly or not os.path.isfile(self.henoConfPath):
            print(
                f"{Colors.WARNING}No {henoConfFile} file found! Trying to generate one...{Colors.ENDC}"
            )
            self.logger.log(f"No {henoConfFile} file found! Trying to generate one...")
            self.tokens = []
            HenoAutoGenConfig.genConfig(self)
            exit()

        with open(self.henoConfPath, "r") as file:
            self.tokens = json.load(file)
            jsonschema.validate(instance=self.tokens, schema=heno_config_schema)

        self.colony = None
        if self.colonyConfPath is not None:
            with open(self.colonyConfPath, "r") as file:
                self.colony = json.load(file)
                jsonschema.validate(instance=self.colony, schema=colony_config_schema)

    @staticmethod
    def SaveKey(account, key, password):
        try:
            Web3().eth.account.from_key(key)
        except:
            print(f"{Colors.FAIL}This is not valid Ethereum private key!{Colors.ENDC}")
            exit()
        with open(f"userdata/{account}privkey.bin", "wb") as file:
            file.write(Encryption.encrypt(key.encode("utf-8"), password))

    @staticmethod
    def IsKeySaved(account):
        return os.path.isfile(f"userdata/{account}privkey.bin")

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

        gas_mul = self.config.get("gas_mul", 1.0)
        if not math.isclose(gas_mul, 1.0):

            def mul(s):
                v = call_function.get(s, 0)
                call_function[s] = int(v * gas_mul)
                if self.debug_mode:
                    print(f"Increasing {s}: {v} -> {call_function[s]}")

            # "gas"
            for i in ["maxPriorityFeePerGas", "maxFeePerGas"]:
                mul(i)

        def clamp_gas(callParam, confParam):
            if (m := self.config.get(confParam, -1)) >= 0:
                m_wei = int(m * 1000000000)
                call_function[callParam] = min(call_function[callParam], m_wei)
                if self.debug_mode:
                    print(f"{callParam} after clamp: {call_function[callParam]}")

        for i, j in [
            ("maxPriorityFeePerGas", "gas_max_priority"),
            ("maxFeePerGas", "gas_max_total"),
        ]:
            clamp_gas(i, j)

        if (d := self.config.get("dummy", 0)) > 0:
            if d == 1:
                return
            else:
                raise Exception("Transaction failed")

        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(
            call_function, private_key=self.private_key
        )

        # Send transaction
        send_tx = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        self.logger.log(f"TX Hash: {send_tx.to_0x_hex()}")
        if self.config.get("print_tx_hash", False):
            print(send_tx.to_0x_hex(), end=" ", flush=True)
            if self.debug_mode:
                print()

        # Wait for transaction receipt
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
        if self.debug_mode:
            print(tx_receipt)  # Optional
        if tx_receipt["status"] != 1:
            raise Exception("Transaction failed")

    def TryAction(self, func: callable, p) -> bool:
        attemptsLeft = self.max_transaction_attempts
        while attemptsLeft > 0:
            try:
                func(attemptsLeft, p)
                attemptsLeft = -1
            except Exception as e:
                print(f"{Colors.FAIL}[Error]")
                print(f"{type(e).__name__}: {e}")
                if isinstance(e, ContractCustomError):
                    print(f"Decoded error:\n{self.decode_contract_error(e.data)}")
                self.logger.log(f"Transaction failed: {type(e).__name__}: {e}")
                if self.debug_mode:
                    print(Colors.FAIL, end="")
                    traceback.print_exc()
                    print(Colors.ENDC)
                attemptsLeft -= 1
                print(f"{Colors.ENDC}", end="")
                if attemptsLeft > 0:
                    print("Retrying...", end=" ", flush=True)
                    self.logger.log("Retrying...")
                self.delay()
        return attemptsLeft == -1

    def delay(self):
        time.sleep(self.delay_t)

    def decode_contract_error(self, error_data: str) -> str:
        for c in [
            self.contract_staking,
            self.contract_chargepod,
            self.contract_nft,
            self.contract_zico,
            self.contract_ylw,
        ]:
            if decoded := c.decode_contract_error(error_data):
                return str(decoded)
        return "Unable to decode error data!"

    # 0 - ask, 1 - sequence, 2 - batch
    def GetConfigAlgorithm(self, n: str) -> int:
        match self.config.get("algorithms", {}).get(n, "ask"):
            case "sequence":
                return 1
            case "batch":
                return 2
            case _:
                return 0

    def printSuccessMessage(self):
        print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")
        self.logger.log("Transaction successfull")
        self.delay()

    def secondsToHMS(self, time):
        return str(timedelta(seconds=time))

    def GetColoredBool(self, b: bool):
        if b:
            return f"{Colors.OKGREEN}True{Colors.ENDC}"
        else:
            return f"{Colors.FAIL}False{Colors.ENDC}"

    def bToHex(self, bytes):
        return f"0x{bytes.hex()}"

    def shortAddr(self, strHexAdr):
        return f"{strHexAdr[0:6]}...{strHexAdr[-4:]}"

    def DictToPrettyString(self, dict, colorBool=True):
        s = pformat(dict, sort_dicts=False)
        if colorBool:
            s = s.replace("True", f"{Colors.OKGREEN}True{Colors.ENDC}")
            s = s.replace("False", f"{Colors.FAIL}False{Colors.ENDC}")
        return s

    def CallWithoutCrash(self, func, arg=None):
        try:
            func(arg)
        except Exception as e:
            estr = "".join(traceback.format_exception(e))
            print(f"{Colors.FAIL}{estr}{Colors.ENDC}")
            try:
                self.logger.log(f"Error:\n{estr}")
            except:
                pass
            pass

    def SelectContract(self):
        print("1) contract_chargepod")
        print("2) contract_staking")
        c = None
        match (input("Select contract: ")):
            case "1":
                c = self.contract_chargepod
            case "2":
                c = self.contract_staking
        return c

    def InputMultipleArgs(self) -> list:
        n = int(input("Number of args: "))
        l = []
        for i in range(n):
            a = input(f"Arg{i}: ")
            try:
                a = eval(a)
            except:
                pass
            l.append(a)
        return l

    def TestCustomRead(self, contract: DecodedContract, func: str, args: list):
        def _Read(_):
            print(self.DictToPrettyString(contract.call_decoded(func, *args)))

        self.CallWithoutCrash(_Read)

    def TestCustomWrite(self, contract: DecodedContract, func: str, args: list):
        def _Write(*_):
            print(
                "Calling function: ",
                end=" ",
                flush=True,
            )
            fn = getattr(contract.functions, func)
            self.Transaction(fn(*args))
            self.printSuccessMessage()

        self.TryAction(_Write, None)
