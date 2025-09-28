from copy import deepcopy
from datetime import datetime
import time
import traceback
from tabulate import tabulate
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class ColonyWars(HenoBase):
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
            + f"defensiveStake: {d["defensiveStake"] / self.ZicoDividor}\n"
            + f"territoriesCount: {d["territoriesCount"]}\n"
            + f"inAlliance: {self.GetColoredBool(d["inAlliance"])}\n\n"
            + f"THREATS:\n"
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
            i["stakeAmount"] = i["stakeAmount"] / self.ZicoDividor
        print(self.DictToPrettyString(d))

    def CWCompareWithColony(self, potentialVictim):
        d = self.contract_chargepod.call_decoded("compareBattlePower", self.colony["Colony"], potentialVictim)
        print(self.DictToPrettyString(d))

    def CWRanking(self, fullAddress: bool):
        d = self.contract_chargepod.call_decoded("getSeasonWarPrizeRanking", self.colony["Season"], 1000)
        for i in d:
            isMy = i["colonyId"] == bytes.fromhex(self.colony["Colony"][2:])
            i["colonyId"] = self.bToHex(i["colonyId"])
            i["estimatedPrize"] = i["estimatedPrize"] / self.ZicoDividor
            i["earnedThisSeason"] = i["earnedThisSeason"] / self.ZicoDividor
            if not fullAddress:
                i["colonyId"] = self.shortAddr(i["colonyId"])
                i["ownerAddress"] = self.shortAddr(i["ownerAddress"])
            if isMy:
                i["colonyId"] = f"{Colors.WARNING}{i["colonyId"]}{Colors.ENDC}"
            i["inAlliance"] = self.GetColoredBool(i["inAlliance"])
        print(tabulate(d, headers="keys"))

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

    def CWPrintCurrentBattles(self):
        d = self.CWGetUnresolvedBattles()
        for i in d:
            snapshot = self.contract_chargepod.functions.getBattleSnapshot(i["battleId"]).call()
            i["battleStartTime"] = datetime.fromtimestamp(int(i["battleStartTime"])).strftime("%Y-%m-%d %H:%M:%S")
            i["battleId"] = self.bToHex(i["battleId"])
            i["opponent"] = self.bToHex(i["opponent"])
            i["stakeAmount"] = i["stakeAmount"] / self.ZicoDividor
            i["isAttackerDefend"] = len(snapshot[1]) != 0
            i["snapshot"] = snapshot
            i["TotalAttackerPower"] = sum(snapshot[0])
            i["TotalDefenderPower"] = sum(snapshot[1])
        print(self.DictToPrettyString(d))

    def CWPrintWeatherForecast(self):
        battlefieldWeather = self.contract_chargepod.call_decoded("getBattlefieldWeather")
        weatherAdvantage = self.contract_chargepod.call_decoded("checkWeatherAdvantage")
        weatherForecast = self.contract_chargepod.call_decoded("getWeatherForecast")
        weatherForecast["timeUntilChange"] = self.secondsToHMS(weatherForecast["timeUntilChange"])

        match (battlefieldWeather["weatherType"]):
            case 0:  # Clear
                weather_icon = "\U00002600"
            case 1:  # Storm
                weather_icon = "\U0001F329"
            case 2:  # Fog
                weather_icon = "\U0001f32b"
            case 3:  # Wind
                weather_icon = "\U0001F343" 
            case 4:  # Rain
                weather_icon = "\U0001f327"
            case _:  # Malfunction
                weather_icon = "\U00002753"

        match (weatherAdvantage["favorType"]):
            case 0:
                favours = "favours attackers"
            case 1:
                favours = "favours defenders"
            case 2:
                favours = "is neutral"
            case _:
                favours = f"<Unknown>"

        print(
            f"{Colors.OKBLUE}Battlefield weather:{Colors.ENDC}\n"
            + f"{battlefieldWeather["weatherName"]} {weather_icon}\n"
            + f"Attacker Mod: {battlefieldWeather["attackerMod"]}%\n"
            + f"Defender Mod: {battlefieldWeather["defenderMod"]}%\n"
            + f"Weather {favours}, {weatherAdvantage["advantage"]}% advantage."
        )
        print(
            f"{Colors.OKBLUE}Weather Forecast:{Colors.ENDC}\n"
            + f"Current: {weatherForecast["current"]}\n"
            + f"Prognosed: {weatherForecast["next"]} in {weatherForecast["timeUntilChange"]}\n"
        )

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
                tmp["stakeAmount"] = tmp["stakeAmount"] / self.ZicoDividor
                print(f"{i})")
                print(self.DictToPrettyString(tmp))
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
                    self.colony["Colony"], victim, kit["CollectionIDs"], kit["TokenIDs"], int(stakeAmmount * self.ZicoDividor)
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
