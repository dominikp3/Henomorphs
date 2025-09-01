import time
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoInspect(HenoBase):
    def Inspect(self):
        self.logger.log("Starting inspection")

        def _Inspect(_, p):
            print("Performing core Inspection: ", end=" ", flush=True)
            self.logger.log(f"Performing core Inspection for tokens: {str([{"CollectionID": p[0][i], "TokenID": p[1][i]} for i in range(len(p[0]))])}")
            self.Transaction(self.contract_nft.functions.inspect(p[0], p[1]))
            self.printSuccessMessage()

        tokensToInspect = [[], []]
        print("Getting data...")
        for token in self.tokens:
            data = self.contract_chargepod.functions.checkBiopodCalibration(token["CollectionID"], token["TokenID"]).call()[1]
            print(f"{self.ChickChar}", end=" ", flush=True)
            t = int(time.time()) - int(data[10])
            if t <= 12 * 60 * 60:
                tr = 12 * 60 * 60 - t
                print(
                    f"{Colors.WARNING}Cannot inspect token ({token['CollectionID']}, {token['TokenID']}). Next inspection possible in: {self.secondsToHMS(tr)}{Colors.ENDC}"
                )
            elif int(data[2]) >= 100:
                print(f"{Colors.WARNING}Cannot inspect token ({token['CollectionID']}, {token['TokenID']}). Kinship: {data[2]}{Colors.ENDC}")
            else:
                tokensToInspect[0].append(token["CollectionID"])
                tokensToInspect[1].append(token["TokenID"])
        print()

        if len(tokensToInspect[0]) == 0:
            print(f"{Colors.WARNING}No tokens availabe to inspect!{Colors.ENDC}")
            self.logger.log("No tokens availabe to inspect!")
            return

        self.TryAction(_Inspect, tokensToInspect)
