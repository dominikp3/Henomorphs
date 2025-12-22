from lib.DecodedContract import DecodedContract


class ColonyNameSystem:
    _names_map: dict = None

    def __init__(self, contract: DecodedContract):
        self.contract = contract

    def _get_names(self):
        if not self._names_map:
            d = self.contract.call_decoded("getColonyRanking", 0, 1000)
            self._names_map = {}
            for i in d:
                self._names_map[i["name"]] = i["colonyId"]
        return self._names_map

    def lookup(self, name: str | bytes) -> bytes:
        if type(name) is bytes:
            return name
        n = self._get_names()
        adres = n.get(name)
        if not adres and name[:2] == "0x":
            adres = bytes.fromhex(name[2:])
        return adres

    def rlookup(self, adres: bytes) -> str:
        n = self._get_names()
        try:
            return list(n.keys())[list(n.values()).index(adres)]
        except:
            return f"0x{adres.hex()}"
