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


from lib.FileLogger import FileLogger
from lib.HenoAutoGenConfig import HenoAutoGenConfig
from lib.Henomorphs import Henomorphs
from lib.Encryption import InvalidPasswordError
from lib.Colors import Colors
import getpass
import sys
import traceback
import os
from lib.ConfigSelector import GetConfig
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
    exit()


def main():
    sys.excepthook = except_hook
    Colors.WindowsEnableColors()
    print(
        f"{Colors.OKBLUE}Henomorphs Python  Copyright (C) 2025  Dominik Piestrzyński\n"
        + f"This program comes with ABSOLUTELY NO WARRANTY;\n"
        + f"This is free software, and you are welcome to redistribute it\n"
        + f"under certain conditions; See LICENSE.md file for details\n{Colors.ENDC}"
    )

    if not os.path.exists("userdata"):
        os.makedirs("userdata")

    (account, hConf, cConf) = GetConfig()

    if Henomorphs.IsKeySaved(account):
        try:
            hen = Henomorphs(account, getpass.getpass("Password: "), hConf, colonyConfFile=cConf)
        except InvalidPasswordError:
            print(f"{Colors.FAIL}Invalid password or privkey.bin corrupted{Colors.ENDC}")
            exit(2)
    else:
        print(
            f"{Colors.HEADER}Welcome{Colors.ENDC}\n"
            + f"It looks like you use the script for first time. You need to import wallet (with Henomorphs tokens) and select a password.\n"
            + f"Your wallet will be stored in {Colors.BOLD}privkey.bin{Colors.ENDC} file using secure AES 256 bit encryption.\n"
            + f"{Colors.WARNING}WARNING: DO NOT SHARE YOUR PRIVATE KEY, {Colors.BOLD}privkey.bin{Colors.ENDC}{Colors.WARNING} FILE AND PASSWORD WITH ANYONE.\n"
            + f"For better security, use strong password.{Colors.ENDC}\n"
        )
        prvkey = input("Enter private key: ")
        password = input("Enter password: ")
        Henomorphs.SaveKey(account, prvkey, password)
        print(f"{Colors.OKGREEN}Succesfully stored key{Colors.ENDC}")
        if os.path.isfile(f"userdata/{account}{hConf}"):
            print(f"{Colors.OKGREEN}Please restart script{Colors.ENDC}")
        else:
            Henomorphs(account, password, hConf, True)
        exit()

    summarizer = Summarizer(hen.GetPol(), hen.GetZico())
    while True:
        print(f"{Colors.HEADER}Henomorphs Python{Colors.ENDC}{Colors.OKCYAN}")
        print("-" * 50)
        summarizer.printBalances()
        print("-" * 50, end=f"\n{Colors.ENDC}")
        checkApproval(hen)
        print("1) Display info")
        print("2) Inspect")
        print("3) Perform Action")
        print("4) Repair Wear")
        print("5) Repair Charge")
        print("6) Check rewards / claim")
        print("7) Check ZICO approval")
        print("8) Change specializations")
        print("9) Colony Wars \U0001f3ae\U00002694")
        print(f"42) Auto update {hConf} (add / remove tokens)")
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
                print(f"Pending rewards: {rewards[0]}, tokens: {rewards[1]}")
                if input("Claim? [y/n]: ") == "y":
                    hen.ClaimAll(rewards[1])
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
            case "0":
                exit()
        summarizer.printSummary(hen.GetPol(), hen.GetZico())


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


def RepairWear(hen):
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
        print(f"{Colors.OKCYAN}1) Sequence {Colors.OKBLUE}(Repair them one by one){Colors.ENDC}")
        print(f"{Colors.OKCYAN}2) Batch {Colors.OKBLUE}(Repair all at once){Colors.ENDC}")
        print(f"{Colors.OKCYAN}0) Exit{Colors.ENDC}")
        if _match(input("Select function: ")):
            return


def ApproveZico(hen):
    while True:
        print(f"{Colors.HEADER}Select contract address{Colors.ENDC}")
        print(f"{Colors.OKCYAN}1) NFT (0xCEaA...D61f) - Inspection ({hen.GetZicoApproval(hen.contract_nft_address)})")
        print(f"{Colors.OKCYAN}2) HenomorphsChargepod (0xA899...Db76) - Actions, Repair charge ({hen.GetZicoApproval(hen.contract_chargepod_address)})")
        print(f"{Colors.OKCYAN}3) HenomorphsStaking (0xA16C...97BE) - Repair Wear ({hen.GetZicoApproval(hen.contract_staking_address)})")
        print(f"{Colors.OKCYAN}0) Exit{Colors.ENDC}")
        match (input("Select function: ")):
            case "1":
                hen.ApproveZico(hen.contract_nft_address, int(input("Value: ")))
            case "2":
                hen.ApproveZico(hen.contract_chargepod_address, int(input("Value: ")))
            case "3":
                hen.ApproveZico(hen.contract_staking_address, int(input("Value: ")))
            case "0":
                return


def checkApproval(hen):
    if (
        hen.GetZicoApproval(hen.contract_nft_address) <= 50
        or hen.GetZicoApproval(hen.contract_chargepod_address) <= 50
        or hen.GetZicoApproval(hen.contract_staking_address) <= 50
    ):
        print(f"{Colors.WARNING}WARNING: Low ZICO approval. Please check approval to avoid errors.")
        print(f"-" * 50, end=f"\n{Colors.ENDC}")


def ColonyWars(hen, summarizer):
    if not hen.CWIsConfigured():
        print(f"{Colors.FAIL}Colony Wars is not configured !{Colors.ENDC}")
        return

    while True:
        print(f"{Colors.HEADER}Select option{Colors.ENDC}")
        print(f"{Colors.OKCYAN}1) Check status \U0001F4C3")
        print(f"{Colors.OKCYAN}2) Check Battle History \U0001F4D6")
        print(f"{Colors.OKCYAN}3) Attack \U00002694")
        print(f"{Colors.OKCYAN}4) Defense \U0001f6e1")
        print(f"{Colors.OKCYAN}5) Resolve Battle \U0001f4dc")
        print(f"{Colors.OKCYAN}6) Compare colony battle power \U0001F94A")
        print(f"{Colors.OKCYAN}7) Ranking \U0001F396")
        print(f"{Colors.OKCYAN}0) Exit{Colors.ENDC}")
        match (input("Select function: ")):
            case "1":
                hen.CWPrintStatus()
            case "2":
                hen.CWPrintBattleHistory()
            case "3":
                hen.CWAttack(input("Victim collony ID: "), float(input("Stake amount [ZICO]: ")))
            case "4":
                hen.CWDefend()
            case "5":
                hen.CWResolveBattle()
            case "6":
                hen.CWCompareWithColony(input("Potential victim collony ID: "))
            case "7":
                hen.CWRanking(input("Show full addresses [y/n]: ") == "y")
            case "0":
                return
        summarizer.printSummary(hen.GetPol(), hen.GetZico())


if __name__ == "__main__":
    main()
