from copy import deepcopy
from datetime import datetime
from pprint import pprint
import time
import traceback
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class ColonyWars(HenoBase):
    def bToHex(self, bytes):
        return f"0x{bytes.hex()}"

    def CWIsConfigured(self) -> bool:
        return self.colony is not None

    def CWSelectKit(self):
        kit = None
        kits = self.colony["WarKits"]

        if len(kits) == 1:
            kit = kits[0]
        elif len(kits) > 1:
            print(f"{Colors.HEADER}Multiple War Kits detected:{Colors.ENDC}")
            i = 1
            for c in kits:
                print(f"{i}) {c.get("name", "")}")
                print(f"\t{c["CollectionIDs"]}")
                print(f"\t{c["TokenIDs"]}\n")
                i += 1
            if 0 < (v := int(input("Select kit: "))) < i:
                kit = kits[v - 1]
            else:
                print(f"{Colors.FAIL}Selected non existing kit!{Colors.ENDC}")
        return kit

    def CWIsKitAvailabe(self, kit) -> bool:
        d = self.contract_chargepod.functions.canStartBattle(kit["CollectionIDs"], kit["TokenIDs"]).call()
        for i in d:
            if i == False:
                return False
        return True

    def CWPrintStatus(self):
        d = self.contract_chargepod.call_decoded("getColonyStrategicOverview", self.colony["Colony"])
        d2 = self.contract_chargepod.call_decoded("getColonyCombatRank", self.colony["Season"], self.colony["Colony"])
        print(
            f"canAttack: {self.GetColoredBool(d["readiness"]["canAttack"])}\n"
            + f"canDefend: {self.GetColoredBool(d["readiness"]["canDefend"])}\n"
            + f"canSiege: {self.GetColoredBool(d["readiness"]["canSiege"])}\n"
            + f"canRaid: {self.GetColoredBool(d["readiness"]["canRaid"])}\n"
            + f"Cooldown: {self.secondsToHMS(max(d["readiness"]["cooldowns"]))}\n"
            + f"THREATS:\n\n"
            + f"level: {d["threats"]["level"]}\n"
            + f"underAttack: {self.GetColoredBool(d["threats"]["underAttack"])}\n"
            + f"territoriesUnderSiege: {self.GetColoredBool(d["threats"]["territoriesUnderSiege"])}\n\n"
            + f"Rank: {d2["position"]}. place (score: {d2["score"]})\n"
        )

    def CWPrintBattleHistory(self):
        d = self.contract_chargepod.call_decoded("getColonyBattleHistory", self.colony["Colony"], self.colony["Season"])
        for i in d:
            i["battleStartTime"] = datetime.fromtimestamp(int(i["battleStartTime"])).strftime("%Y-%m-%d %H:%M:%S")
            i["battleId"] = self.bToHex(i["battleId"])
            i["opponent"] = self.bToHex(i["opponent"])
        pprint(d)

    def CWGetUnresolvedBattles(self):
        bs = []
        d = self.contract_chargepod.call_decoded("getColonyBattleHistory", self.colony["Colony"], self.colony["Season"])
        for b in d:
            if b["resolved"] == False:
                bs.append(b)
        return bs

    def CWGetAvailabeForDefend(self):
        a = []
        l = self.CWGetUnresolvedBattles()
        for i in l:
            if i["wasAttacker"] == False:
                s = self.contract_chargepod.functions.getBattleSnapshot(i["battleId"]).call()
                if len(s[1]) == 0 and time.time() - int(i["battleStartTime"]) <= 60 * 60 * 2:
                    a.append(i)
        return a

    def CWGetAvailabeForResolve(self):
        a = []
        l = self.CWGetUnresolvedBattles()
        for i in l:
            if time.time() - int(i["battleStartTime"]) >= 60 * 60 * 2:
                a.append(i)
        return a

    def CWSelectBattle(self, battles):
        battle = None

        if len(battles) == 0:
            print(f"{Colors.FAIL}No battle availabe!{Colors.ENDC}")
        else:
            print(f"{Colors.HEADER}Battles availabe:{Colors.ENDC}")
            i = 1
            for c in battles:
                tmp = deepcopy(c)
                tmp["battleStartTime"] = datetime.fromtimestamp(int(tmp["battleStartTime"])).strftime("%Y-%m-%d %H:%M:%S")
                tmp["battleId"] = self.bToHex(tmp["battleId"])
                tmp["opponent"] = self.bToHex(tmp["opponent"])
                tmp["stakeAmount"] = tmp["stakeAmount"] / 1000000000000000000
                print(f"{i})")
                pprint(tmp)
                print()
                i += 1
            if 0 < (v := int(input("Select battle: "))) < i:
                battle = battles[v - 1]
            else:
                print(f"{Colors.FAIL}Selected non existing battle!{Colors.ENDC}")
        return battle

    def CWAttack(self, victim: str, stakeAmmount: int, kit=None):
        if kit == None:
            kit = self.CWSelectKit()

        if kit == None:
            return

        self.logger.log("Started Attack")
        if not self.CWIsKitAvailabe(kit):
            print(f"{Colors.FAIL}Selected kit is not availabe!{Colors.ENDC}")
            self.logger.log("ERROR: Selected kit is not availabe!")
            return

        cd = self.contract_chargepod.functions.getCombatCooldowns(self.colony["Colony"]).call()
        if max(cd) > 0:
            print(f"{Colors.FAIL}Collony in cooldown preiod! {self.secondsToHMS(max(cd))}{Colors.ENDC}")
            self.logger.log("ERROR: Collony in cooldown preiod!")
            return

        def _Attack(*_):
            print("Performing attack: ", end=" ", flush=True)
            self.logger.log(f"Performing attack: ")
            self.logger.log(f"Using kit: {str(kit)}")
            self.Transaction(
                self.contract_chargepod.functions.initiateAttack(
                    self.colony["Colony"], victim, kit["CollectionIDs"], kit["TokenIDs"], int(stakeAmmount * 1000000000000000000)
                )
            )
            self.printSuccessMessage()
            self.delay()

        self.TryAction(_Attack, None)

    def CWDefend(self, battle=None, kit=None) -> bool:
        if battle == None:
            battle = self.CWSelectBattle(self.CWGetAvailabeForDefend())

        if battle == None:
            return False

        if kit == None:
            kit = self.CWSelectKit()

        if kit == None:
            return False

        self.logger.log("Started Defense")
        if not self.CWIsKitAvailabe(kit):
            print(f"{Colors.FAIL}Selected kit is not availabe!{Colors.ENDC}")
            self.logger.log("ERROR: Selected kit is not availabe!")
            return False

        def _Defend(*_):
            print("Defending: ", end=" ", flush=True)
            self.logger.log(f"Defending: ")
            self.logger.log(f"Using kit: {str(kit)}")
            self.Transaction(self.contract_chargepod.functions.defendBattle(battle["battleId"], kit["CollectionIDs"], kit["TokenIDs"]))
            self.printSuccessMessage()
            self.delay()

        return self.TryAction(_Defend, None)

    def CWResolveBattle(self, battle=None):
        if battle == None:
            battle = self.CWSelectBattle(self.CWGetAvailabeForResolve())

        if battle == None:
            return

        self.logger.log("Started Resolve Battle")

        def _Resolve(*_):
            print("Resolve Battle: ", end=" ", flush=True)
            self.logger.log(f"Resolve Battle: {self.bToHex(battle["battleId"])}")
            self.Transaction(self.contract_chargepod.functions.resolveBattle(battle["battleId"]))
            self.printSuccessMessage()
            self.delay()

        self.TryAction(_Resolve, None)

    def CallWithoutCrash(self, func, arg=None):
        try:
            func(arg)
        except Exception as e:
            estr = "".join(traceback.format_exception(e))
            print(f"{Colors.FAIL}{estr}{Colors.ENDC}")
            try:
                self.logger.log(f"Error:\n{estr}")
            except:
                pass
            pass

    def CWAIDefender(self):
        print(f"{Colors.WARNING}Activated AI defender. Use CTRL-C to terminate{Colors.ENDC}")
        self.logger.log("[AI Defender] Activated AI defender.")

        def _bot_defend_battle(battle):
            kits = self.colony["WarKits"]
            for kit in kits:
                if self.CWDefend(battle, kit):
                    print(f"{Colors.OKGREEN}Succesfully defended battle: {self.bToHex(battle["battleId"])}{Colors.ENDC}")
                    self.logger.log(f"[AI Defender] Succesfully defended battle: {self.bToHex(battle["battleId"])}")
                    return
            print(f"{Colors.FAIL}Failed to defended battle: {self.bToHex(battle["battleId"])}{Colors.ENDC}")
            self.logger.log(f"[AI Defender] Failed to defended battle: {self.bToHex(battle["battleId"])}")

        def _bot_main_loop(_):
            print("Checking for threats... ")

            battles = self.CWGetAvailabeForDefend()

            if len(battles) == 0:
                print("No threats found")

            if len(battles) > 0:
                print(f"{Colors.WARNING}Found {len(battles)} threats!!!{Colors.ENDC}")
                self.logger.log(f"[AI Defender] Found {len(battles)} threats!!!")

                for b in battles:
                    self.CallWithoutCrash(_bot_defend_battle, b)

        while True:
            self.CallWithoutCrash(_bot_main_loop)
            time.sleep(self.delay_ai_defender)
