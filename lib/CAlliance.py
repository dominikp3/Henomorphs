from time import time
from lib.Colors import Colors
from lib.Henomorphs import Henomorphs


class ColonyAlliance:
    _alliance_stat = -1
    _alliance_data: dict = None
    _alliance_wallet_colonies: dict = None
    _alliance_col_ter: dict = None
    _last_t = 0
    _last_t_2 = 0

    def __init__(self, heno: Henomorphs):
        self.hen = heno

    def _get_alliance_data(self, get_territories: bool = True):
        if self._alliance_stat < 0 or time() - self._last_t > 3600:
            self._alliance_stat = -1
            c = self.hen.contract_chargepod.call_decoded(
                "isColonyProtectedByAlliance", self.hen.colony["Colony"]
            )
            if c["protected"]:
                self._alliance_wallet_colonies = {}
                self._alliance_data = self.hen.contract_chargepod.call_decoded(
                    "getAllianceInfo", c["allianceId"]
                )
                self._alliance_data["id"] = c["allianceId"]
                for wallet in self._alliance_data["members"]:
                    self._alliance_wallet_colonies[wallet] = []
                    colonies = self.hen.contract_chargepod.call_decoded(
                        "getUserColonies", wallet
                    )
                    for col in colonies:
                        self._alliance_wallet_colonies[wallet].append(col["colonyId"])
            self._alliance_stat = 1 if c["protected"] else 0
            self._last_t = time()
        if (
            self._alliance_stat == 1
            and get_territories
            and (not self._alliance_col_ter or time() - self._last_t_2 > 3600)
        ):
            ter = self.hen.contract_chargepod.call_decoded(
                "getAllTerritoriesRaidStatus"
            )
            self._alliance_col_ter = {}
            for cList in self._alliance_wallet_colonies.values():
                for c in cList:
                    self._alliance_col_ter[c] = []
                    for t in ter:
                        if t["controllingColony"] == c:
                            self._alliance_col_ter[c].append(t["territoryId"])
            self._last_t_2 = time()

    def PrintAlliance(self):
        self._get_alliance_data()
        if self._alliance_stat == 0:
            print(f"{Colors.WARNING}You are not in alliance!{Colors.ENDC}")
            return
        ad = self._alliance_data
        awc = self._alliance_wallet_colonies
        act = self._alliance_col_ter
        print(
            f"{Colors.HEADER}Alliance: {ad['name']}{Colors.ENDC} ({self.hen.bToHex(ad['id'])})\n"
            f"Alliance leader: {Colors.OKBLUE}{self.hen.cns.rlookup(ad['leader'])}{Colors.ENDC} ({self.hen.bToHex(ad['leader'])})\n"
            f"Treasury: {ad['treasury']/self.hen.ZicoDividor}\n"
            f"Stability: {ad['stability']}%\n"
            f"Active: {self.hen.GetColoredBool(ad['active'])}\n"
            f"Wallets in alliance:"
        )
        for wallet in ad["members"]:
            print(f"\t{Colors.OKBLUE}{wallet}{Colors.ENDC}\n\tCollonies:")
            for c in awc[wallet]:
                print(
                    f"\t\t{Colors.OKBLUE}{self.hen.cns.rlookup(c)}{Colors.ENDC}\n"
                    f"\t\tID: {self.hen.bToHex(c)}\n"
                    f"\t\tTerritories: {act[c]}\n"
                )

    def IsCAlliance(self, colony: bytes):
        self._get_alliance_data(False)
        if self._alliance_stat == 1:
            ad = self._alliance_data
            awc = self._alliance_wallet_colonies
            for wallet in ad["members"]:
                for c in awc[wallet]:
                    if c == colony:
                        return True
        return False

    def IsTAlliance(self, tid: int):
        self._get_alliance_data()
        if self._alliance_stat == 1:
            ad = self._alliance_data
            awc = self._alliance_wallet_colonies
            act = self._alliance_col_ter
            for wallet in ad["members"]:
                for c in awc[wallet]:
                    for t in act[c]:
                        if t == tid:
                            return True
        return False

    def CAntiBetrayal(self, attackedCollony: bytes) -> bool:
        """Return True if attacked colony is in alliance"""
        if attackedCollony == self.hen.hexToB(self.hen.colony["Colony"]):
            print(f"{Colors.FAIL}You trying to attack yourself!{Colors.ENDC}")
            return True
        if self.hen.anti_betrayal and self.IsCAlliance(attackedCollony):
            print(f"{Colors.FAIL}Betrayal!{Colors.ENDC}")
            return True
        return False

    def TAntiBetrayal(self, attackedTerrain: int) -> bool:
        """Return True if attacked terrain is owned by alliance"""
        my_t = self.hen.CWGetMyTeritories()
        if attackedTerrain in my_t:
            print(f"{Colors.FAIL}You trying to attack yourself!{Colors.ENDC}")
            return True
        if self.hen.anti_betrayal and self.IsTAlliance(attackedTerrain):
            print(f"{Colors.FAIL}Betrayal!{Colors.ENDC}")
            return True
        return False
