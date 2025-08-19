import time
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoInspect(HenoBase):
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
