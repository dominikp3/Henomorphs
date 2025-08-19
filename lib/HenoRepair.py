import time
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoRepair(HenoBase):
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
