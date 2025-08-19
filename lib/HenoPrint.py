from datetime import datetime
from tabulate import tabulate
from lib.HenoBase import HenoBase


class HenoPrint(HenoBase):
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
            print(f"{self.ChickChar}", end=" ", flush=True)
        print()
        print(tabulate(d, headers=headers))
