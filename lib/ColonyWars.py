from copy import deepcopy
from datetime import datetime, timedelta
import time
from tabulate import tabulate
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class ColonyWars(HenoBase):
    def CWIsConfigured(self) -> bool:
        return self.colony is not None

    def CWPSColorOp(self, d: dict):
        """Dict to Pretty String and colorize opponent name"""
        ps = self.DictToPrettyString(d)
        ps = self.DictPSColorize(ps, "opponentName", Colors.OKBLUE)
        return ps

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
        d = self.contract_chargepod.functions.canStartBattle(
            kit["CollectionIDs"], kit["TokenIDs"]
        ).call()
        for i in d:
            if i == False:
                return False
        return True

    def CWPrintStatus(self):
        d = self.contract_chargepod.call_decoded(
            "getColonyStrategicOverview", self.colony["Colony"]
        )
        d2 = self.contract_chargepod.call_decoded(
            "getColonyCombatRank", self.colony["Colony"]
        )
        # Cooldowns: attack, raid, siege, betrayal
        print(
            f"canAttack: {self.GetColoredBool(d["readiness"]["canAttack"])}\n"
            + f"canDefend: {self.GetColoredBool(d["readiness"]["canDefend"])}\n"
            + f"canSiege: {self.GetColoredBool(d["readiness"]["canSiege"])}\n"
            + f"canRaid: {self.GetColoredBool(d["readiness"]["canRaid"])}\n"
            + f"Cooldowns:\n"
            + f"\tAttack: {self.secondsToHMS(d["readiness"]["cooldowns"][0])}\n"
            + f"\tRaid: {self.secondsToHMS(d["readiness"]["cooldowns"][1])}\n"
            + f"\tSiege: {self.secondsToHMS(d["readiness"]["cooldowns"][2])}\n"
            + f"\tBetrayal: {self.secondsToHMS(d["readiness"]["cooldowns"][3])}\n"
            + f"defensiveStake: {d["defensiveStake"] / self.ZicoDividor}\n"
            + f"territoriesCount: {d["territoriesCount"]}\n"
            + f"inAlliance: {self.GetColoredBool(d["inAlliance"])}\n\n"
            + f"THREATS:\n"
            + f"level: {d["threats"]["level"]}\n"
            + f"underAttack: {self.GetColoredBool(d["threats"]["underAttack"])}\n"
            + f"territoriesUnderSiege: {self.GetColoredBool(d["threats"]["territoriesUnderSiege"])}\n\n"
            + f"Rank: {d2["rank"]}. place (score: {d2["score"]}). Total participants: {d2["totalParticipants"]}\n"
        )

    def CWPrintBattleHistory(self):
        d = self.contract_chargepod.call_decoded(
            "getColonyBattleHistory",
            self.colony["Colony"],
            self.colony["Season"],
            0,
            1000,
        )["battles"]
        for i in d:
            i["battleStartTime"] = self.timestampToStr(i["battleStartTime"])
            i["battleId"] = self.bToHex(i["battleId"])
            i["opponentName"] = self.cns.rlookup(i["opponent"])
            i["opponent"] = self.bToHex(i["opponent"])
            i["stakeAmount"] = i["stakeAmount"] / self.ZicoDividor
        print(self.CWPSColorOp(d))

    def CWCompareWithColony(self, potentialVictim: str):
        d = self.contract_chargepod.call_decoded(
            "compareBattlePower",
            self.colony["Colony"],
            self.cns.lookup(potentialVictim),
        )
        print(self.DictToPrettyString(d))

    def CWRanking(self, showAddress: bool, defStake: bool):
        d = self.contract_chargepod.call_decoded(
            "getSeasonWarPrizeRanking", self.colony["Season"], 1000
        )
        if defStake:
            self.dsi.get_stakes(d)
        for i in d:
            if defStake:
                i["DefStake"] = self.dsi.get_col_dstake(i["colonyId"])
            isMy = i["colonyId"] == self.hexToB(self.colony["Colony"])
            isAlliance = self.alliance.IsCAlliance(i["colonyId"])
            i["Name"] = self.cns.rlookup(i["colonyId"])
            i["colonyId"] = self.bToHex(i["colonyId"])
            i["estimatedPrize"] = i["estimatedPrize"] / self.ZicoDividor
            i["earnedThisSeason"] = i["earnedThisSeason"] / self.ZicoDividor
            if not showAddress:
                i.pop("ownerAddress")
                i.pop("colonyId")
                if i["Name"][:2] == "0x":
                    i["Name"] = self.shortAddr(i["Name"])
            if isMy:
                i["Name"] = f"{Colors.OKGREEN}{i["Name"]}{Colors.ENDC}"
            elif isAlliance:
                i["Name"] = f"{Colors.WARNING}{i["Name"]}{Colors.ENDC}"
            i["inAlliance"] = self.GetColoredBool(i["inAlliance"])
        for i in range(len(d)):
            d[i] = {"rank": d[i].pop("rank"), "Name": d[i].pop("Name")} | d[i]
        if defStake:
            print()
        print(tabulate(d, headers="keys"))
        print(f"Colors: {Colors.OKGREEN}My  {Colors.WARNING}Alliance{Colors.ENDC}")

    def CWGetUnresolvedBattles(self):
        bs = []
        d = self.contract_chargepod.call_decoded(
            "getColonyBattleHistory",
            self.colony["Colony"],
            self.colony["Season"],
            0,
            1000,
        )["battles"]
        for b in d:
            if b["resolved"] == False:
                bs.append(b)
        return bs

    def CWGetAvailabeForDefend(self):
        a = []
        l = self.CWGetUnresolvedBattles()
        for i in l:
            if i["wasAttacker"] == False:
                s = self.contract_chargepod.functions.getBattleSnapshot(
                    i["battleId"]
                ).call()
                if (
                    len(s[1]) == 0
                    and time.time() - int(i["battleStartTime"]) <= 60 * 60 * 2
                ):
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
            snapshot = self.contract_chargepod.functions.getBattleSnapshot(
                i["battleId"]
            ).call()
            i["battleStartTime"] = self.timestampToStr(i["battleStartTime"])
            i["opponentName"] = self.cns.rlookup(i["opponent"])
            i["battleId"] = self.bToHex(i["battleId"])
            i["opponent"] = self.bToHex(i["opponent"])
            i["stakeAmount"] = i["stakeAmount"] / self.ZicoDividor
            i["isAttackerDefend"] = len(snapshot[1]) != 0
            i["snapshot"] = snapshot
            i["TotalAttackerPower"] = sum(snapshot[0])
            i["TotalDefenderPower"] = sum(snapshot[1])
        print(self.CWPSColorOp(d))

    def CWPrintWeatherForecast(self):
        battlefieldWeather = self.contract_chargepod.call_decoded(
            "getBattlefieldWeather"
        )
        weatherAdvantage = self.contract_chargepod.call_decoded("checkWeatherAdvantage")

        match (battlefieldWeather["weatherType"]):
            case 0:  # Clear
                weather_icon = "\U00002600"
            case 1:  # Storm
                weather_icon = "\U0001f329"
            case 2:  # Fog
                weather_icon = "\U0001f32b"
            case 3:  # Wind
                weather_icon = "\U0001f343"
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
        weatherForecast = self.contract_chargepod.call_decoded("getWeatherForecast")
        weatherForecast["timeUntilChange"] = self.secondsToHMS(
            weatherForecast["timeUntilChange"]
        )
        print(
            f"{Colors.OKBLUE}Weather Forecast:{Colors.ENDC}\n"
            + f"{weatherForecast["next"]} in {weatherForecast["timeUntilChange"]}"
            + (
                f"\n{Colors.WARNING}FORECAST IS NOT RELIABLE"
                if not weatherForecast["forecastReliable"]
                else ""
            )
        )

        daily = self.contract_chargepod.call_decoded("getDailyWeatherForecast")
        utc_offset = datetime.now().astimezone().utcoffset()

        def tformat(i):
            t = timedelta(hours=2 * i) + utc_offset
            hours, remainder = divmod(t.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}"

        print(f"{Colors.OKBLUE}Daily Forecast:{Colors.ENDC}")
        for i in range(daily["currentPeriod"], 12):
            t = timedelta(hours=i * 2) + utc_offset
            print(f"{tformat(i)} - {tformat(i+1)}\t{daily["periods"][i]}")
        print()

    def CWSelectBattle(self, battles):
        battle = None

        if len(battles) == 0:
            print(f"{Colors.FAIL}No battle availabe!{Colors.ENDC}")
        else:
            print(f"{Colors.HEADER}Battles availabe:{Colors.ENDC}")
            i = 1
            for c in battles:
                tmp = deepcopy(c)
                tmp["battleStartTime"] = self.timestampToStr(tmp["battleStartTime"])
                tmp["opponentName"] = self.cns.rlookup(tmp["opponent"])
                tmp["battleId"] = self.bToHex(tmp["battleId"])
                tmp["opponent"] = self.bToHex(tmp["opponent"])
                tmp["stakeAmount"] = tmp["stakeAmount"] / self.ZicoDividor
                print(f"{i})")
                print(self.CWPSColorOp(tmp))
                print()
                i += 1
            if 0 < (v := int(input("Select battle: "))) < i:
                battle = battles[v - 1]
            else:
                print(f"{Colors.FAIL}Selected non existing battle!{Colors.ENDC}")
        return battle

    def CWAttack(self, victim: str, stakeAmmount: int, kit=None):
        lvictim = self.cns.lookup(victim)
        if lvictim == None:
            print(
                f"{Colors.FAIL}'{victim}' is not recognized as valid colony name or address!{Colors.ENDC}"
            )
            return False

        if self.alliance.CAntiBetrayal(lvictim):
            return False

        if kit == None:
            kit = self.CWSelectKit()

        if kit == None:
            return False

        self.logger.log("Started Attack")
        if not self.CWIsKitAvailabe(kit):
            print(f"{Colors.FAIL}Selected kit is not availabe!{Colors.ENDC}")
            self.logger.log("ERROR: Selected kit is not availabe!")
            return

        cd = self.contract_chargepod.functions.getCombatCooldowns(
            self.colony["Colony"]
        ).call()
        # 0 - attack cooldown
        if cd[0] > 0:
            print(
                f"{Colors.FAIL}Collony in cooldown preiod! {self.secondsToHMS(cd[0])}{Colors.ENDC}"
            )
            self.logger.log("ERROR: Collony in cooldown preiod!")
            return False

        def _Attack(*_):
            print("Performing attack: ", end=" ", flush=True)
            self.logger.log(f"Performing attack on colony {self.bToHex(lvictim)}")
            self.logger.log(f"Using kit: {str(kit)}")
            self.Transaction(
                self.contract_chargepod.functions.initiateAttack(
                    self.colony["Colony"],
                    lvictim,
                    kit["CollectionIDs"],
                    kit["TokenIDs"],
                    int(stakeAmmount * self.ZicoDividor),
                )
            )
            self.printSuccessMessage()

        return self.TryAction(_Attack, None)

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
            self.logger.log(f"Defending battle: {self.bToHex(battle["battleId"])}")
            self.logger.log(f"Using kit: {str(kit)}")
            self.Transaction(
                self.contract_chargepod.functions.defendBattle(
                    battle["battleId"], kit["CollectionIDs"], kit["TokenIDs"]
                )
            )
            self.printSuccessMessage()

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
            self.Transaction(
                self.contract_chargepod.functions.resolveBattle(battle["battleId"])
            )
            self.printSuccessMessage()

        self.TryAction(_Resolve, None)

    def CWColonyHealth(self, tcid=False):
        def _repair(_, i):
            print("Repair colony health:", end=" ", flush=True)
            self.logger.log(f"Repair colony health: {self.colony["Colony"]}")
            self.Transaction(
                self.contract_chargepod.functions.restoreColonyHealth(
                    self.colony["Colony"], i
                )
            )
            self.printSuccessMessage()

        d = self.contract_chargepod.call_decoded(
            "getColonyHealthDetails", self.colony["Colony"]
        )
        d["restorationCost"] /= self.ZicoDividor
        print(self.DictToPrettyString(d))
        d2 = list(
            self.contract_chargepod.call_decoded("getRestorationOptions").values()
        )
        l2 = int(len(d2) / 2)
        print(f"{Colors.HEADER}Availabe options:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}0) Do nothing{Colors.ENDC}")
        for i in range(l2):
            print(
                f"{Colors.OKCYAN}{i+1}) {d2[i+l2]} ({int(d2[i])/self.ZicoDividor} ZICO or something IDK){Colors.ENDC}"
            )
        sel = input("Select: ")
        sel = int(sel)
        if sel > 0 and sel < l2:
            self.TryAction(_repair, sel)

    def CWAdvisedTargets(
        self, only_hex=False, s_rev: bool = False, p_col: list[bytes] = []
    ) -> tuple[dict, dict]:
        col = self.colony["Colony"]
        threshold = self.colony.get("weak_defstake_threshold", 0)
        wt = {"targets": [], "stakes": []}
        if threshold <= 0:
            wt = self.contract_chargepod.call_decoded(
                "getSupposedWeakTargets", col, 100
            )
        else:
            colonies = self.contract_chargepod.call_decoded(
                "getSeasonWarPrizeRanking", self.colony["Season"], 1000
            )
            self.dsi.get_stakes(colonies)
            colonies = [c["colonyId"] for c in colonies]
            for c in colonies:
                ds = self.dsi.get_col_dstake(c)
                if ds <= threshold and not self.alliance.IsCAlliance(c):
                    wt["targets"].append(c)
                    wt["stakes"].append(ds * self.ZicoDividor)
        for pc in p_col:
            if pc not in wt["targets"]:
                wt["targets"].append(pc)
                wt["stakes"].append(self.dsi.get_col_dstake(pc) * self.ZicoDividor)
        wtl = len(wt["targets"])
        wtt = []
        for i in range(wtl):
            if only_hex:
                wtt.append(
                    {
                        "ID": (wt["targets"][i]),
                        "Stake": wt["stakes"][i] / self.ZicoDividor,
                    }
                )
            else:
                wtt.append(
                    {
                        "Name": self.cns.rlookup(wt["targets"][i]),
                        "ID": wt["targets"][i],
                        "Stake": wt["stakes"][i] / self.ZicoDividor,
                    }
                )
        wtt.sort(key=lambda x: x["Stake"], reverse=s_rev)
        wtt.sort(key=lambda x: x["ID"] in p_col, reverse=True)
        ter = self.contract_chargepod.call_decoded("getAllTerritoriesRaidStatus")
        tr = []
        for co in wtt:
            c = co["ID"]
            for t in ter:
                if t["controllingColony"] == c and t["canRaid"]:
                    if only_hex:
                        tr.append(
                            {
                                "ID": t["territoryId"],
                                "Colony": t["controllingColony"],
                                "damageLevel": t["damageLevel"],
                            }
                        )
                    else:
                        tr.append(
                            {
                                "ID": t["territoryId"],
                                "territoryName": t["territoryName"],
                                "Colony": self.cns.rlookup(t["controllingColony"]),
                                "damageLevel": t["damageLevel"],
                            }
                        )
        if not only_hex:
            for t in wtt:
                t["ID"] = self.bToHex(t["ID"])
        return (wtt, tr)

    def CWPrintAdvise(self):
        col = self.colony["Colony"]
        aa = self.contract_chargepod.call_decoded("getAdvisedCombatActions", col)
        if len(aa) > 0:
            print(f"{Colors.OKBLUE}Advised actions:{Colors.ENDC}")
            for a in aa:
                print(f"\U0001f534 {a}")

        tt = self.contract_chargepod.call_decoded("getTerritoriesForCapture", 100)
        if len(tt["territoryIds"]) > 0:
            print(f"{Colors.OKBLUE}Territories availabe to capture:{Colors.ENDC}")
            print(f"{tt['territoryIds']}")

        colonies, terrains = self.CWAdvisedTargets()
        if len(colonies) > 0:
            print(f"{Colors.OKBLUE}Recommended attack targets:{Colors.ENDC}")
            print(tabulate(colonies, headers="keys"))

        if len(terrains) > 0:
            print(f"{Colors.OKBLUE}Ideal for Siege or Raid:{Colors.ENDC}")
            print(tabulate(terrains, headers="keys"))
