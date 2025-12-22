from time import time
from lib.CNS import ColonyNameSystem
from lib.DecodedContract import DecodedContract
from lib.HenoBase import HenoBase


class CDefStake:
    _dstakes_map: dict = None
    _last_t = 0

    def __init__(self, heno: HenoBase):
        self.heno = heno

    # Parameter rank is for optimization
    # To not call getSeasonWarPrizeRanking twice
    def get_stakes(self, rank=None):
        if not self._dstakes_map or time() - self._last_t > 43200:
            dstakes = {}
            print("Refreshing defstake cache")
            if not rank:
                colonies = self.heno.contract_chargepod.call_decoded(
                    "getSeasonWarPrizeRanking", self.heno.colony["Season"], 1000
                )
            else:
                colonies = rank
            colonies = [c["colonyId"] for c in colonies]
            for c in colonies:
                dsi = self.heno.contract_chargepod.call_decoded(
                    "getDefensiveStakeInfo", c
                )
                dstakes[c] = dsi["currentStake"] / HenoBase.ZicoDividor
                print(HenoBase.ChickChar, end=" ", flush=True)
            print()
            self._last_t = time()
            self._dstakes_map = dstakes
        return self._dstakes_map

    def get_col_dstake(self, colony: bytes):
        return self.get_stakes().get(colony, 0)
