import time
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoRepair(HenoBase):
    # returns threahold and max repair amount
    def _get_repair_params(self, confn: str) -> tuple[int, int]:
        conf = self.config.get(confn, {})
        threshold = conf.get("threshold", -1)
        max_repair = conf.get("max_repair", -1)
        if threshold < 0:
            threshold = int(input("Threshold (greater or equal): "))
        if max_repair < 0:
            max_repair = int(input("Max repair amount: "))
        return (threshold, max_repair)

    def RepairWearSequence(self):
        self.logger.log("Starting wear repair (Sequence)")
        (threshold, reduction) = self._get_repair_params("repair_wear")

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
                self.logger.log(
                    f"Performing wear repair: ({t['CollectionID']}, {t['TokenID']}), Reduction: {r}"
                )
                self.Transaction(
                    self.contract_staking.functions.repairTokenWear(
                        int(t["CollectionID"]), int(t["TokenID"]), int(r)
                    )
                )
                self.printSuccessMessage()
            else:
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), dont need repair wear. ({data[2]}){Colors.ENDC}"
                )

        for t in self.tokens:
            self.TryAction(_RepairWear, t)

    def RepairWearBatch(self):
        self.logger.log("Starting wear repair (Batch)")
        (threshold, reduction) = self._get_repair_params("repair_wear")

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
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), dont need repair wear. ({data[2]}){Colors.ENDC}"
                )

        def _batch_repair(*_):
            print("Performing batch wear repair: ", end=" ", flush=True)
            self.logger.log(
                "Performing batch wear repair for tokens: "
                + f"{str([{"CollectionID": repairData["collectionIds"][i], "TokenID": repairData["tokenIds"][i], "repair": repairData["repairAmounts"][i]} for i in range(len(repairData["tokenIds"]))])}"
            )
            self.Transaction(
                self.contract_staking.functions.batchRepairTokenWear(repairData)
            )
            self.printSuccessMessage()

        for t in self.tokens:
            _prepare_data(t)

        if len(repairData["tokenIds"]) == 0:
            print(f"{Colors.WARNING}No tokens availabe to repair!{Colors.ENDC}")
            return

        self.TryAction(_batch_repair, None)

    def RepairChargeSequence(self):
        self.logger.log("Starting charge repair (Sequence)")
        (threshold, repair) = self._get_repair_params("repair_charge")

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
                self.logger.log(
                    f"Performing charge repair: ({t['CollectionID']}, {t['TokenID']}), Repair: {r}"
                )
                self.Transaction(
                    self.contract_chargepod.functions.repairCharge(
                        int(t["CollectionID"]), int(t["TokenID"]), int(r)
                    )
                )
                self.printSuccessMessage()
            else:
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), dont need repair charge. ({toRepair}){Colors.ENDC}"
                )

        for t in self.tokens:
            self.TryAction(_RepairCharge, t)

    ### Na dzień dzisiejszy (21.08.2025) NIE DZIAŁA
    ### UPDATE 01.09.2025: Nadal nie działa :(
    #
    # def RepairChargeBatch(self):
    #     self.logger.log("Starting charge repair (Batch)")
    #     (threshold, repair) = self._get_repair_params("repair_charge")

    #     repairData = {"collectionIds": [], "tokenIds": [], "operations": []}

    #     def _prepare_data(t):
    #         data = self.contract_chargepod.functions.getRepairStatus(t["CollectionID"], t["TokenID"]).call()
    #         toRepair = int(data[1]) - int(data[0])
    #         if toRepair >= int(threshold) and toRepair > 0:
    #             r = min(repair, int(toRepair))
    #             print(f"Charge repair: ({t['CollectionID']}, {t['TokenID']}), Repair: {r}")
    #             repairData["collectionIds"].append(t["CollectionID"])
    #             repairData["tokenIds"].append(t["TokenID"])
    #             repairData["operations"].append(
    #                 {
    #                     "chargePoints": r,
    #                     "wearReduction": 0,
    #                     "emergencyMode": False,
    #                     "skipValidation": False,
    #                 }
    #             )
    #         else:
    #             print(f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), dont need repair charge. ({toRepair}){Colors.ENDC}")

    #     def _batch_repair(*_):
    #         print("Performing batch charge repair: ", end=" ", flush=True)
    #         self.logger.log(
    #             "Performing batch charge repair for tokens: "
    #             + f"{str([{"CollectionID": repairData["collectionIds"][i], "TokenID": repairData["tokenIds"][i], "repair": repairData["operations"][i]["chargePoints"]} for i in range(len(repairData["tokenIds"]))])}"
    #         )
    #         self.Transaction(
    #             self.contract_chargepod.functions.batchRepair(
    #                 repairData["collectionIds"],
    #                 repairData["tokenIds"],
    #                 repairData["operations"],
    #             )
    #         )
    #         self.printSuccessMessage()
    #         self.delay()

    #     for t in self.tokens:
    #         _prepare_data(t)

    #     if len(repairData["tokenIds"]) == 0:
    #         print(f"{Colors.WARNING}No tokens availabe to repair!{Colors.ENDC}")
    #         self.logger.log("No tokens availabe to repair!")
    #         return

    #     self.TryAction(_batch_repair, None)
