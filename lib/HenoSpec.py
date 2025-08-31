from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoSpec(HenoBase):
    def GetSpec(self, t) -> int:
        return self.GetSpec2(t["CollectionID"], t["TokenID"])

    def GetSpec2(self, collectionID, tokenID) -> int:
        return self.contract_chargepod.functions.getSpecialization(collectionID, tokenID).call()

    def ChangeSpecializations(self):
        self.logger.log("Started specializations change")

        def _ChangeSpec(_, t):
            spec = t.get("Spec", -1)
            if spec < 0:
                print(f"{Colors.WARNING}Token without specialization, skipping.{Colors.ENDC}")
                return
            curSpec = self.GetSpec(t)
            if curSpec == spec:
                print(f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), specialization already set.")
            else:
                print(f"Changing specialization: ({t['CollectionID']}, {t['TokenID']}), {spec}", end=" ", flush=True)
                self.logger.log(f"Changing specialization: ({t['CollectionID']}, {t['TokenID']}), {spec}")
                self.Transaction(self.contract_chargepod.functions.changeSpecialization(int(t["CollectionID"]), int(t["TokenID"]), int(spec)))
                self.printSuccessMessage()
                self.delay()

        for t in self.tokens:
            self.TryAction(_ChangeSpec, t)
