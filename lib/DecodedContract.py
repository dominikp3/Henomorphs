import json
from web3 import Web3
from eth_utils import keccak
import eth_abi


class DecodedContract:
    def __init__(
        self, web3: Web3, address: str, abi_path: str = None, abi_data: dict = None
    ):
        if abi_path:
            with open(abi_path, "r") as file:
                self.abi = json.load(file)
        elif abi_data:
            self.abi = abi_data
        else:
            raise ValueError("Provide either abi_path or abi_data")

        self.web3 = web3
        self.address = address
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        self._function_outputs_cache = {}

    def __getattr__(self, name):
        # automatycznie przekazuje dostęp do metod kontraktu, np. functions, address, events itd.
        return getattr(self.contract, name)

    def _parse_output(self, abi_output, value):
        if abi_output["type"] == "tuple":
            components = abi_output["components"]
            return {
                comp["name"]: self._parse_output(comp, val)
                for comp, val in zip(components, value)
            }
        elif abi_output["type"].endswith("[]"):
            base_type = abi_output["type"][:-2]
            if base_type == "tuple":
                return [
                    self._parse_output(
                        {"type": "tuple", "components": abi_output["components"]}, item
                    )
                    for item in value
                ]
            else:
                return list(value)
        else:
            return value

    def _get_function_outputs(self, function_name):
        if function_name in self._function_outputs_cache:
            return self._function_outputs_cache[function_name]

        for entry in self.abi:
            if entry.get("type") == "function" and entry.get("name") == function_name:
                outputs = entry["outputs"]
                self._function_outputs_cache[function_name] = outputs
                return outputs

        raise ValueError(f"Function '{function_name}' not found in ABI")

    def decode_result(self, function_name: str, raw_result):
        outputs = self._get_function_outputs(function_name)

        if len(outputs) == 1:
            return self._parse_output(outputs[0], raw_result)
        else:
            return {
                (out.get("name") or f"output_{i}"): self._parse_output(out, val)
                for i, (out, val) in enumerate(zip(outputs, raw_result))
            }

    def call_decoded(self, function_name: str, *args, **kwargs):
        """
        Call a contract function and return the decoded result as a dict with field names.
        Example: call_decoded("getOverview")
        """
        fn = getattr(self.contract.functions, function_name)
        raw_result = fn(*args).call(**kwargs)
        return self.decode_result(function_name, raw_result)

    def decode_contract_error(self, error_data: str) -> dict | None:
        """
        Decode custom error

        Args:
            error_data: str — hex error code as string (eg. "0x12345678...")

        Returns:
            dict: {
                'name': str,
                'args': dict,
                'signature': str,
            }
            or None
        """

        if not error_data or not error_data.startswith("0x"):
            raise ValueError("Invalid error data")

        # 4-bajtowy selector błędu
        selector = bytes.fromhex(error_data[2:10])
        data = bytes.fromhex(error_data[10:])

        # Szukamy błędu w ABI kontraktu
        for item in self.contract.abi:
            if item.get("type") == "error":
                sig = f"{item['name']}({','.join(i['type'] for i in item['inputs'])})"
                sig_hash = keccak(text=sig)[:4]
                # print(f"{sig} => {sig_hash.hex()}")
                if sig_hash == selector:
                    # Dekodujemy argumenty
                    types = [i["type"] for i in item["inputs"]]
                    names = [i["name"] for i in item["inputs"]]
                    decoded_values = eth_abi.decode(types, data)

                    return {
                        "name": item["name"],
                        "args": dict(zip(names, decoded_values)),
                        "signature": sig,
                    }

        return None  # nie znaleziono błędu
