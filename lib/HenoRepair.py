import time
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoRepair(HenoBase):
    # returns threahold and max repair amount
    def _get_repair_params(self, conf: dict) -> tuple[int, int]:
        threshold = conf.get("threshold", -1)
        max_repair = conf.get("max_repair", -1)
        if threshold < 0:
            threshold = int(input("Threshold (greater or equal): "))
        if max_repair < 0:
            max_repair = int(input("Max repair amount: "))
        return (threshold, max_repair)

    def RepairWearSequence(self):
        (threshold, reduction) = self._get_repair_params(
            self.config.get("repair_wear", {})
        )

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

    def RepairWearBatch(self):
        (threshold, reduction) = self._get_repair_params(
            self.config.get("repair_wear", {})
        )

        repairData = {
            "collectionIds": [],
            "tokenIds": [],
            "repairAmount": 0,
            "repairAmounts": [],
            "uniformRepair": False,
        }

        def _prepare_data(t):
            data = self.contract_chargepod.functions.getRepairStatus(
                t["CollectionID"], t["TokenID"]
            ).call()
            if int(data[2]) >= int(threshold) and int(data[2]) > 0:
                r = min(reduction, int(data[2]))
                print(
                    f"Wear repair: ({t['CollectionID']}, {t['TokenID']}), Reduction: {r}"
                )
                repairData["collectionIds"].append(t["CollectionID"])
                repairData["tokenIds"].append(t["TokenID"])
                repairData["repairAmounts"].append(r)
            else:
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), dont need repair wear.{Colors.ENDC}"
                )

        def _batch_repair(*_):
            print("Performing batch wear repair: ", end=" ", flush=True)
            self.Transaction(
                self.contract_staking.functions.batchRepairTokenWear(repairData)
            )
            print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")
            time.sleep(self.config["delay"])

        for t in self.tokens:
            _prepare_data(t)

        if len(repairData["tokenIds"]) == 0:
            print(f"{Colors.WARNING}No tokens availabe to repair!{Colors.ENDC}")
            return

        self.TryAction(_batch_repair, None)

    def RepairCharge(self):
        (threshold, repair) = self._get_repair_params(
            self.config.get("repair_charge", {})
        )

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
