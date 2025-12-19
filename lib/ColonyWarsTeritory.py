from copy import deepcopy
from time import time
from tabulate import tabulate
from lib.ColonyWars import ColonyWars
from lib.Colors import Colors


class ColonyWarsTeritory(ColonyWars):
    _MyTeritories: list[int] | None = None

    def CWGetMyTeritories(self):
        if self._MyTeritories is None:
            self._MyTeritories = self.contract_chargepod.call_decoded(
                "getColonyTerritories", self.colony["Colony"]
            )
        return self._MyTeritories

    def CWTPSColorOp(self, d: dict):
        """Dict to Pretty String and colorize opponent / defender names"""
        ps = self.DictToPrettyString(d)
        ps = self.DictPSColorize(ps, "defenderName", Colors.OKBLUE)
        ps = self.DictPSColorize(ps, "attackerName", Colors.OKBLUE)
        return ps

    def CWGetMyTeritoriesStstus(self):
        def _maintain(_, i):
            print(f"Maintain Territory [{i}]:", end=" ", flush=True)
            self.logger.log(f"Maintain Territory [{i}]")
            self.Transaction(self.contract_chargepod.functions.maintainTerritory(i))
            self.printSuccessMessage()

        def _repair(_, i):
            print(f"Repair teritory [{i}]:", end=" ", flush=True)
            self.logger.log(f"Repair Territory [{i}]")
            self.Transaction(self.contract_chargepod.functions.repairTerritory(i))
            self.printSuccessMessage()

        ids = self.CWGetMyTeritories()
        info = []
        for i in ids:
            t = self.contract_chargepod.call_decoded("getTerritoryInfo", i)
            t = {"id": i, "name": t.pop("name")} | t
            t.pop("controllingColony")
            info.append(t)

        maintenance = []
        repair = []
        for i in info:
            last = int(time()) - i.pop("lastMaintenancePayment")
            col = ""
            if last > 86400:
                col = Colors.FAIL if last > 172800 else Colors.WARNING
                if last > self.config.get("terrain_maintenance_threshold", 86400):
                    maintenance.append(i["id"])
            if i["damageLevel"] > self.config.get("terrain_repair_threshold", 0):
                repair.append(i["id"])
            i["lastMaintenancePayment"] = self.secondsToHMS(last)
            s = self.DictToPrettyString(i)
            s = self.DictPSColorize(s, "lastMaintenancePayment", col)
            print(f"{s}\n")

        if (len(maintenance) > 0 or len(repair) > 0) and input(
            "Let me take care of your teritories [y/n]: "
        ) == "y":
            for m in maintenance:
                self.TryAction(_maintain, m)
            for r in repair:
                self.TryAction(_repair, r)

    def CWGetUnresolvedSieges(self):
        ss = []
        d = self.contract_chargepod.call_decoded("getActiveTerritorySeiges")
        for s in d:
            colony = self.hexToB(self.colony["Colony"])
            if s["attackerColony"] == colony or s["defenderColony"] == colony:
                ss.append(s)
        return ss

    def CWGetSiegesAvailabeForDefend(self):
        colony = self.hexToB(self.colony["Colony"])
        a = []
        l = self.CWGetUnresolvedSieges()
        for i in l:
            if i["defenderColony"] == colony:
                s = self.contract_chargepod.functions.getSiegeSnapshot(
                    i["siegeId"]
                ).call()
                if len(s[1]) == 0 and int(time()) - int(i["siegeEndTime"]) < 0:
                    a.append(i)
        return a

    def CWGetSiegesAvailabeForResolve(self):
        a = []
        l = self.CWGetUnresolvedSieges()
        for i in l:
            if int(time()) - int(i["siegeEndTime"]) >= 0:
                a.append(i)
        return a

    def CWPrintCurrentSieges(self):
        d = self.CWGetUnresolvedSieges()
        for i in d:
            snapshot = self.contract_chargepod.functions.getSiegeSnapshot(
                i["siegeId"]
            ).call()
            i["stakeAmount"] /= self.ZicoDividor
            i["siegeStartTime"] = self.timestampToStr(i["siegeStartTime"])
            i["siegeEndTime"] = self.timestampToStr(i["siegeEndTime"])
            i["siegeId"] = self.bToHex(i["siegeId"])
            i["defenderName"] = self.cns.rlookup(i["defenderColony"])
            i["attackerName"] = self.cns.rlookup(i["attackerColony"])
            i["defenderColony"] = self.bToHex(i["defenderColony"])
            i["attackerColony"] = self.bToHex(i["attackerColony"])
            i["defenderColony"] = self.bToHex(i["defenderColony"])
            i["snapshot"] = snapshot
            i["TotalAttackerPower"] = sum(snapshot[0])
            i["TotalDefenderPower"] = sum(snapshot[1])
            i["timeRemaining"] = self.secondsToHMS(i["timeRemaining"])
        print(self.CWTPSColorOp(d))

    def CWSelectSiege(self, sieges):
        siege = None

        if len(sieges) == 0:
            print(f"{Colors.FAIL}No siege availabe!{Colors.ENDC}")
        else:
            print(f"{Colors.HEADER}Sieges availabe:{Colors.ENDC}")
            i = 1
            for c in sieges:
                tmp = deepcopy(c)
                tmp["stakeAmount"] /= self.ZicoDividor
                tmp["siegeStartTime"] = self.timestampToStr(tmp["siegeStartTime"])
                tmp["siegeEndTime"] = self.timestampToStr(tmp["siegeEndTime"])
                tmp["siegeId"] = self.bToHex(tmp["siegeId"])
                i["defenderName"] = self.cns.rlookup(i["defenderColony"])
                i["attackerName"] = self.cns.rlookup(i["attackerColony"])
                tmp["attackerColony"] = self.bToHex(tmp["attackerColony"])
                tmp["defenderColony"] = self.bToHex(tmp["defenderColony"])
                tmp["timeRemaining"] = self.secondsToHMS(tmp["timeRemaining"])
                print(f"{i})")
                print(self.CWTPSColorOp(tmp))
                print()
                i += 1
            if 0 < (v := int(input("Select siege: "))) < i:
                siege = sieges[v - 1]
            else:
                print(f"{Colors.FAIL}Selected non existing siege!{Colors.ENDC}")
        return siege

    def CWSiege(self, terrain: int, stakeAmmount: int, kit=None):
        if self.alliance.TAntiBetrayal(terrain):
            return False

        if kit == None:
            kit = self.CWSelectKit()

        if kit == None:
            return False

        self.logger.log("Started Siege")
        if not self.CWIsKitAvailabe(kit):
            print(f"{Colors.FAIL}Selected kit is not availabe!{Colors.ENDC}")
            self.logger.log("ERROR: Selected kit is not availabe!")
            return False

        cd = self.contract_chargepod.functions.getCombatCooldowns(
            self.colony["Colony"]
        ).call()
        # 2 - siege cooldown
        if cd[2] > 0:
            print(
                f"{Colors.FAIL}Collony in cooldown preiod! {self.secondsToHMS(cd[2])}{Colors.ENDC}"
            )
            self.logger.log("ERROR: Collony in cooldown preiod!")
            return False

        def _Siege(*_):
            print("Performing siege: ", end=" ", flush=True)
            self.logger.log(f"Performing siege on {terrain}")
            self.logger.log(f"Using kit: {str(kit)}")
            self.Transaction(
                self.contract_chargepod.functions.siegeTerritory(
                    terrain,
                    self.colony["Colony"],
                    kit["CollectionIDs"],
                    kit["TokenIDs"],
                    int(stakeAmmount * self.ZicoDividor),
                )
            )
            self.printSuccessMessage()

        return self.TryAction(_Siege, None)

    def CWDefendSiege(self, siege=None, kit=None) -> bool:
        if siege == None:
            siege = self.CWSelectSiege(self.CWGetSiegesAvailabeForDefend())

        if siege == None:
            return False

        if kit == None:
            kit = self.CWSelectKit()

        if kit == None:
            return False

        self.logger.log("Started Siege Defense")
        if not self.CWIsKitAvailabe(kit):
            print(f"{Colors.FAIL}Selected kit is not availabe!{Colors.ENDC}")
            self.logger.log("ERROR: Selected kit is not availabe!")
            return False

        def _DefendSiege(*_):
            print("Defending siege: ", end=" ", flush=True)
            self.logger.log(f"Defending siege: {self.bToHex(siege["siegeId"])}")
            self.logger.log(f"Using kit: {str(kit)}")
            self.Transaction(
                self.contract_chargepod.functions.defendSiege(
                    siege["siegeId"], kit["CollectionIDs"], kit["TokenIDs"]
                )
            )
            self.printSuccessMessage()

        return self.TryAction(_DefendSiege, None)

    def CWResolveSiege(self, siege=None):
        if siege == None:
            siege = self.CWSelectSiege(self.CWGetSiegesAvailabeForResolve())

        if siege == None:
            return

        self.logger.log("Started Resolve Siege")

        def _Resolve(*_):
            print("Resolve Siege: ", end=" ", flush=True)
            self.logger.log(f"Resolve Siege: {self.bToHex(siege["siegeId"])}")
            self.Transaction(
                self.contract_chargepod.functions.resolveSiege(siege["siegeId"])
            )
            self.printSuccessMessage()

        self.TryAction(_Resolve, None)

    def CWPrintTeritories(self, showAddress: bool = False):
        d = self.contract_chargepod.call_decoded("getAllTerritoriesRaidStatus")
        for i in d:
            isMy = i["territoryId"] in self.CWGetMyTeritories()
            isAlliance = self.alliance.IsTAlliance(i["territoryId"])
            i["ColonyName"] = self.cns.rlookup(i["controllingColony"])
            i["controllingColony"] = self.bToHex(i["controllingColony"])
            i["raidCooldownRemaining"] = self.secondsToHMS(i["raidCooldownRemaining"])
            i["lastRaidTime"] = self.timestampToStr(i["lastRaidTime"])
            if not showAddress:
                i.pop("controllingColony")
                if i["ColonyName"][:2] == "0x":
                    i["ColonyName"] = self.shortAddr(i["ColonyName"])
            if isMy:
                i["territoryName"] = (
                    f"{Colors.OKGREEN}{i["territoryName"]}{Colors.ENDC}"
                )
            elif isAlliance:
                i["territoryName"] = (
                    f"{Colors.WARNING}{i["territoryName"]}{Colors.ENDC}"
                )
        for i in range(len(d)):
            d[i] = {
                "ID": d[i].pop("territoryId"),
                "territoryName": d[i].pop("territoryName"),
                "ColonyName": d[i].pop("ColonyName"),
            } | d[i]
        print(tabulate(d, headers="keys"))
        print(f"Colors: {Colors.OKGREEN}My  {Colors.WARNING}Alliance{Colors.ENDC}")

    def CWRaidTeritory(self, teritoryId, stake):
        self.logger.log("Started Raid teritory")

        def _Raid(*_):
            print("Raid teritory: ", end=" ", flush=True)
            self.logger.log(f"Raid teritory: {teritoryId}, s: {stake}")
            self.Transaction(
                self.contract_chargepod.functions.raidTerritory(
                    teritoryId, int(stake * self.ZicoDividor)
                )
            )
            self.printSuccessMessage()

        self.TryAction(_Raid, None)
