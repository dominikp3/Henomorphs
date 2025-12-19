# Henomorphs Python. Unofficial interface for interacting with Henomorphs NFT collection
# Copyright (C) 2025  Dominik Piestrzyński

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from pathlib import Path
from lib import HenoInit
from lib.FileLogger import FileLogger
from lib.HenoAutoGenConfig import HenoAutoGenConfig
from lib.Henomorphs import Henomorphs
from lib.Colors import Colors
import sys
import traceback
from lib.Summarizer import Summarizer


def except_hook(exctype, value, _):
    if exctype == KeyboardInterrupt:
        print(f"{Colors.HEADER}Good Bye{Colors.ENDC}")
    else:
        e = "".join(traceback.format_exception(value))
        print(f"{Colors.FAIL}{e}{Colors.ENDC}")
        try:
            FileLogger().log(f"The script crashed:\n{e}")
        except:
            pass
        exit(42)


def main():
    sys.excepthook = except_hook
    Colors.WindowsEnableColors()
    print(
        f"{Colors.OKBLUE}Henomorphs Python  Copyright (C) 2025  Dominik Piestrzyński\n"
        + f"This program comes with ABSOLUTELY NO WARRANTY;\n"
        + f"This is free software, and you are welcome to redistribute it\n"
        + f"under certain conditions; See LICENSE.md file for details\n{Colors.ENDC}"
    )

    hen = HenoInit.init()
    hConf = Path(hen.henoConfPath).name

    summarizer = Summarizer(hen.GetPol(), hen.GetZico(), hen.GetYlw())
    while True:
        print(f"{Colors.HEADER}Henomorphs Python{Colors.ENDC}{Colors.OKCYAN}")
        print("-" * 50)
        summarizer.printBalances()
        print("-" * 50, end=f"\n{Colors.ENDC}")
        # checkApproval(hen)
        print("1) Display info")
        print("2) Inspect")
        print("3) Perform Action")
        print("4) Repair Wear")
        print("5) Repair Charge")
        print("6) Check rewards / claim")
        print("7) Check ZICO/YLW approval")
        print("8) Change specializations")
        print("9) Colony Wars \U0001f3ae\U00002694")
        print(f"42) Auto update {hConf} (add / remove tokens)")
        if hen.experimental:
            print("101) Custom Read")
            print("102) Custom Write")
        print("0) Exit")
        match (input("Select function: ")):
            case "1":
                hen.PrintInfo()
            case "2":
                hen.Inspect()
            case "3":
                PerformAction(hen)
            case "4":
                RepairWear(hen)
            case "5":
                hen.RepairChargeSequence()
            case "6":
                rewards = hen.GetPendingRewards()
                hen.printPendingRewards(rewards)
                if input("Claim? [y/n]: ") == "y":
                    hen.ClaimAll(rewards["stakedCount"])
            case "7":
                ApproveZico(hen)
            case "8":
                hen.ChangeSpecializations()
            case "9":
                ColonyWars(hen, summarizer)
            case "42":
                print(
                    f"{Colors.WARNING}WARNING: This function gets staked tokens from blockchain and add/remove tokens to your {hConf} file\n{Colors.ENDC}"
                    + f"{Colors.WARNING}Is highly recommended to backup your current {hConf} file before use.{Colors.ENDC}"
                )
                if input("Are you sure? [y/n]: ") == "y":
                    HenoAutoGenConfig.genConfig(hen)
            case "101":
                if hen.experimental:
                    hen.TestCustomRead(
                        hen.SelectContract(),
                        input("Function: "),
                        hen.InputMultipleArgs(),
                    )
            case "102":
                if hen.experimental:
                    hen.TestCustomWrite(
                        hen.SelectContract(),
                        input("Function: "),
                        hen.InputMultipleArgs(),
                    )
            case "0":
                exit()
        summarizer.printSummary(hen.GetPol(), hen.GetZico(), hen.GetYlw())


def PerformAction(hen):
    def _match(x):
        match (x):
            case "1":
                hen.PerformColonyActionSequence()
                return True
            case "2":
                hen.PerformColonyActionBatch()
                return True
            case "0":
                return True
        return False

    if (a := hen.GetConfigAlgorithm("actions")) > 0:
        _match(str(a))
        return

    while True:
        print(f"{Colors.HEADER}Select alghorithm{Colors.ENDC}")
        print(f"{Colors.OKCYAN}1) SingleChickSequence")
        print(
            f"{Colors.OKBLUE}Iterate through all of chicks and performAction()\n"
            + f"If action fails, it can reattempt action or try choosing a random action (depending on configuration)\n"
            + f"[{hen.ChickChar}], [{hen.ChickChar}], [{hen.ChickChar}], ...{Colors.ENDC}"
        )
        print(f"{Colors.OKCYAN}2) MultiBatch [BETA]{Colors.ENDC}")
        print(
            f"{Colors.OKBLUE}Automatically group your chicks with same collection and action\n"
            + f"perform action on MULTIPLE chicks in single transaction, saving gas fee.\n"
            + f"{Colors.BOLD}This is experimental function, there is no warranty that action will be succesfull for everychick\n"
            f"Note that if random_action_on_fail feature will no work with this mode\n{Colors.ENDC}"
            + f"{Colors.OKBLUE}[{hen.ChickChar}, {hen.ChickChar}, {hen.ChickChar}, ...], ...{Colors.ENDC}"
        )
        print(f"{Colors.OKCYAN}0) Exit{Colors.ENDC}")
        if _match(input("Select function: ")):
            return


def RepairWear(hen: Henomorphs):
    def _match(x):
        match (x):
            case "1":
                hen.RepairWearSequence()
                return True
            case "2":
                hen.RepairWearBatch()
                return True
            case "0":
                return True
        return False

    if (a := hen.GetConfigAlgorithm("repair_wear")) > 0:
        _match(str(a))
        return

    while True:
        print(f"{Colors.HEADER}Select alghorithm{Colors.ENDC}")
        print(
            f"{Colors.OKCYAN}1) Sequence {Colors.OKBLUE}(Repair them one by one){Colors.ENDC}"
        )
        print(
            f"{Colors.OKCYAN}2) Batch {Colors.OKBLUE}(Repair all at once){Colors.ENDC}"
        )
        print(f"{Colors.OKCYAN}0) Exit{Colors.ENDC}")
        if _match(input("Select function: ")):
            return


def ApproveZico(hen: Henomorphs):
    while True:
        print(f"{Colors.HEADER}Select contract & Currency{Colors.ENDC}")
        print(f"{Colors.WARNING}ZICO Approval{Colors.ENDC}")
        print(
            f"{Colors.OKCYAN}1) NFT (0xCEaA...D61f) ({hen.GetZicoApproval(hen.contract_nft_address)})"
        )
        print(
            f"{Colors.OKCYAN}2) HenomorphsChargepod (0xA899...Db76) ({hen.GetZicoApproval(hen.contract_chargepod_address)})"
        )
        print(
            f"{Colors.OKCYAN}3) HenomorphsStaking (0xA16C...97BE) ({hen.GetZicoApproval(hen.contract_staking_address)})"
        )
        print(f"{Colors.OKGREEN}YLW Approval{Colors.ENDC}")
        print(
            f"{Colors.OKCYAN}4) NFT (0xCEaA...D61f) ({hen.GetYlwApproval(hen.contract_nft_address)})"
        )
        print(
            f"{Colors.OKCYAN}5) HenomorphsChargepod (0xA899...Db76) ({hen.GetYlwApproval(hen.contract_chargepod_address)})"
        )
        print(
            f"{Colors.OKCYAN}6) HenomorphsStaking (0xA16C...97BE) ({hen.GetYlwApproval(hen.contract_staking_address)})"
        )
        print(f"{Colors.OKCYAN}0) Exit{Colors.ENDC}")
        match (input("Select function: ")):
            case "1":
                hen.ApproveZico(hen.contract_nft_address, int(input("Value: ")))
            case "2":
                hen.ApproveZico(hen.contract_chargepod_address, int(input("Value: ")))
            case "3":
                hen.ApproveZico(hen.contract_staking_address, int(input("Value: ")))
            case "4":
                hen.ApproveYLW(hen.contract_nft_address, int(input("Value: ")))
            case "5":
                hen.ApproveYLW(hen.contract_chargepod_address, int(input("Value: ")))
            case "6":
                hen.ApproveYLW(hen.contract_staking_address, int(input("Value: ")))
            case "0":
                return


# def checkApproval(hen):
#     if (
#         hen.GetZicoApproval(hen.contract_nft_address) <= 50
#         or hen.GetZicoApproval(hen.contract_chargepod_address) <= 50
#         or hen.GetZicoApproval(hen.contract_staking_address) <= 50
#     ):
#         print(
#             f"{Colors.WARNING}WARNING: Low ZICO approval. Please check approval to avoid errors."
#         )
#         print(f"-" * 50, end=f"\n{Colors.ENDC}")


def ColonyWars(hen: Henomorphs, summarizer: Summarizer):
    if not hen.CWIsConfigured():
        print(f"{Colors.FAIL}Colony Wars is not configured !{Colors.ENDC}")
        return

    while True:
        print(f"{Colors.HEADER}Select option{Colors.ENDC}")
        print(f"{Colors.OKCYAN}1) Check status \U0001f4c3")
        print(f"{Colors.OKCYAN}2) Check Battle History \U0001f4d6")
        print(f"{Colors.OKCYAN}3) Attack \U00002694")
        print(f"{Colors.OKCYAN}4) Defense \U0001f6e1")
        print(f"{Colors.OKCYAN}5) Resolve Battle \U0001f4dc")
        print(f"{Colors.OKCYAN}6) Compare colony battle power \U0001f94a")
        print(f"{Colors.OKCYAN}7) Ranking \U0001f396")
        print(f"{Colors.OKCYAN}8) Check Current Battles \U0001f4d6")
        print(f"{Colors.OKCYAN}9) Check Weather Forecast \U000026c5")
        print(f"{Colors.OKCYAN}10) Check Colony Health \U00002764")
        print(f"{Colors.OKCYAN}11) Check My Teritories \U0001f50e\U0001f5fa")
        print(f"{Colors.OKCYAN}12) Check Current sieges \U0001f4d6")
        print(f"{Colors.OKCYAN}13) Siege \U0001f3c7")
        print(f"{Colors.OKCYAN}14) Defense siege \U0001f6e1")
        print(f"{Colors.OKCYAN}15) Resolve siege \U0001f4dc")
        print(f"{Colors.OKCYAN}16) Raid teritory \U0001f3c7")
        print(f"{Colors.OKCYAN}17) Check All teritories \U0001f30d")
        print(
            f"{Colors.OKCYAN}18) Check Alliance \U0001f9d1\U0000200d\U0001f91d\U0000200d\U0001f9d1"
        )
        print(f"{Colors.OKCYAN}19) Tactical Advisor \U0001f9ed")
        if hen.experimental:
            print(f"{Colors.OKCYAN}20) Tactical Bot \U0001f916 [EXPERIMENTAL]")
        print(f"{Colors.OKCYAN}0) Exit{Colors.ENDC}")
        match (input("Select function: ")):
            case "1":
                hen.CWPrintStatus()
            case "2":
                hen.CWPrintBattleHistory()
            case "3":
                hen.CWAttack(
                    input("Victim collony ID: "), float(input("Stake amount [ZICO]: "))
                )
            case "4":
                hen.CWDefend()
            case "5":
                hen.CWResolveBattle()
            case "6":
                hen.CWCompareWithColony(input("Potential victim collony ID: "))
            case "7":
                hen.CWRanking(
                    input("Show addresses [y/n]: ") == "y",
                    input("Show defensive stake [y/n]: ") == "y",
                )
            case "8":
                hen.CWPrintCurrentBattles()
            case "9":
                hen.CWPrintWeatherForecast()
            case "10":
                hen.CWColonyHealth()
            case "11":
                hen.CWGetMyTeritoriesStstus()
            case "12":
                hen.CWPrintCurrentSieges()
            case "13":
                hen.CWSiege(
                    int(input("Teritory ID: ")), float(input("Stake amount [ZICO]: "))
                )
            case "14":
                hen.CWDefendSiege()
            case "15":
                hen.CWResolveSiege()
            case "16":
                hen.CWRaidTeritory(
                    int(input("Teritory ID: ")), float(input("Stake amount [ZICO]: "))
                )
            case "17":
                hen.CWPrintTeritories(input("Show addresses [y/n]: ") == "y")
            case "18":
                hen.alliance.PrintAlliance()
            case "19":
                hen.CWPrintAdvise()
            case "20":
                if hen.experimental:
                    from lib.CWAI import CWAI

                    CWAI(hen)
            case "0":
                return
        summarizer.printSummary(hen.GetPol(), hen.GetZico(), hen.GetYlw())


if __name__ == "__main__":
    main()
