import random
import time
from lib.Colors import Colors
from lib.Henomorphs import Henomorphs


def CWAI(hen: Henomorphs):
    col = hen.colony["Colony"]

    ai_interval = hen.config.get("ai_interval", 900)

    ai_ofn = hen.colony.get("ai_offensive", False)
    ai_ofn_stake = hen.colony.get("ai_offensive_stake", 500)
    ai_ofn_max_ds = hen.colony.get("ai_offensive_max_ds", 100)
    ai_ofn_prefer_weak = hen.colony.get("ai_offensive_prefer_weak", False)
    ai_ofn_excl = hen.colony.get("ai_offensive_excluded", [])
    ai_ofn_excl = [hen.hexToB(e) for e in ai_ofn_excl]
    ai_ofn_pref_target = hen.colony.get("ai_offensive_pref_target", [])
    ai_ofn_pref_target = [hen.hexToB(e) for e in ai_ofn_pref_target]
    random.shuffle(ai_ofn_pref_target)

    print(
        f"{Colors.WARNING}Activated AI defender. Use CTRL-C to terminate{Colors.ENDC}"
    )
    hen.logger.log("[AI Defender] Activated AI defender.")

    def _bot_defend_battle(battle):
        kits = hen.colony["WarKits"]
        for kit in kits:
            if hen.CWDefend(battle, kit):
                print(
                    f"{Colors.OKGREEN}Succesfully defended battle: {hen.bToHex(battle["battleId"])}{Colors.ENDC}"
                )
                hen.logger.log(
                    f"[AI Defender] Succesfully defended battle: {hen.bToHex(battle["battleId"])}"
                )
                return True
        print(
            f"{Colors.FAIL}Failed to defended battle: {hen.bToHex(battle["battleId"])}{Colors.ENDC}"
        )
        hen.logger.log(
            f"[AI Defender] Failed to defended battle: {hen.bToHex(battle["battleId"])}"
        )
        return False

    def _bot_defend_siege(siege):
        kits = hen.colony["WarKits"]
        for kit in kits:
            if hen.CWDefendSiege(siege, kit):
                print(
                    f"{Colors.OKGREEN}Succesfully defended siege: {hen.bToHex(siege["siegeId"])}{Colors.ENDC}"
                )
                hen.logger.log(
                    f"[AI Defender] Succesfully defended siege: {hen.bToHex(siege["siegeId"])}"
                )
                return True
        print(
            f"{Colors.FAIL}Failed to defended siege: {hen.bToHex(siege["siegeId"])}{Colors.ENDC}"
        )
        hen.logger.log(
            f"[AI Defender] Failed to defended siege: {hen.bToHex(siege["siegeId"])}"
        )
        return False

    def _bot_attack(victim):
        kits = hen.colony["WarKits"]
        for kit in kits:
            if hen.CWAttack(victim, ai_ofn_stake, kit):
                print(
                    f"{Colors.OKGREEN}Succesfully attacked: {hen.bToHex(victim)}{Colors.ENDC}"
                )
                hen.logger.log(
                    f"[AI Defender] Succesfully attacked: {hen.bToHex(victim)}"
                )
                return True
        print(f"{Colors.FAIL}Failed to attack: {hen.bToHex(victim)}{Colors.ENDC}")
        hen.logger.log(f"[AI Defender] Failed to attack: {hen.bToHex(victim)}")
        return False

    def _bot_siege(victimT):
        kits = hen.colony["WarKits"]
        for kit in kits:
            if hen.CWSiege(victimT, ai_ofn_stake, kit):
                print(f"{Colors.OKGREEN}Succesfully sieged: {victimT}{Colors.ENDC}")
                hen.logger.log(f"[AI Defender] Succesfully sieged: {victimT}")
                return True
        print(f"{Colors.FAIL}Failed to siege: {victimT}{Colors.ENDC}")
        hen.logger.log(f"[AI Defender] Failed to siege: {victimT}")
        return False

    def _bot_main_loop(_):
        print("Checking for threats... ")

        battles = hen.CWGetAvailabeForDefend()
        sieges = hen.CWGetSiegesAvailabeForDefend()
        threats = len(battles) + len(sieges)

        if threats == 0:
            print("No threats found")
        else:
            print(f"{Colors.WARNING}Found {threats} threats!!!{Colors.ENDC}")
            hen.logger.log(f"[AI Defender] Found {threats} threats!!!")

            if len(battles) > 0:
                for b in battles:
                    hen.CallWithoutCrash(_bot_defend_battle, b)

            if len(sieges) > 0:
                for s in sieges:
                    hen.CallWithoutCrash(_bot_defend_siege, s)

        if ai_ofn:  # Attack mode enabled
            cd = hen.contract_chargepod.call_decoded("getCombatCooldowns", col)

            if cd[0] == 0:  # No cooldowns
                colonies, terrains = hen.CWAdvisedTargets(True)
                colonies.sort(key=lambda x: x["Stake"], reverse=not ai_ofn_prefer_weak)
                colonies = [c for c in colonies if c["Stake"] <= ai_ofn_max_ds]
                colonies_ids = ai_ofn_pref_target + [c["ID"] for c in colonies]
                colonies_ids = [c for c in colonies_ids if c not in ai_ofn_excl]
                terrains_ids = []
                for c in colonies_ids:
                    for t in terrains:
                        if t["Colony"] == c:
                            terrains_ids.append(t["ID"])
                for t in terrains_ids[:3]:
                    if hen.CallWithoutCrash(_bot_siege, t):
                        break
                for c in colonies_ids[:3]:
                    if hen.CallWithoutCrash(_bot_attack, c):
                        break
            else:
                print(f"Cooldown! {hen.secondsToHMS(max(cd))}")

    while True:
        hen.CallWithoutCrash(_bot_main_loop)
        time.sleep(ai_interval)
