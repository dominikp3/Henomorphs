from lib.Henomorphs import Henomorphs
from lib.Encryption import InvalidPasswordError
from lib.Colors import Colors
import getpass
import sys
import traceback
import os


def except_hook(exctype, value, _):
    if exctype == KeyboardInterrupt:
        print(f"{Colors.HEADER}Good Bye{Colors.ENDC}")
    else:
        print(Colors.FAIL)
        traceback.print_exception(value)
        print(Colors.ENDC)
    exit()


def main():
    sys.excepthook = except_hook
    Colors.WindowsEnableColors()
    if not os.path.exists("userdata"):
        os.makedirs("userdata")

    if Henomorphs.IsKeySaved():
        try:
            hen = Henomorphs(getpass.getpass("Password: "))
        except InvalidPasswordError:
            print(
                f"{Colors.FAIL}Invalid password or privkey.bin corrupted{Colors.ENDC}"
            )
            exit()
    else:
        print(
            f"{Colors.HEADER}Welcome{Colors.ENDC}\n"
            + f"It looks like you use the script for first time. You need to import wallet (with Henomorphs tokens) and select a password.\n"
            + f"Your wallet will be stored in {Colors.BOLD}privkey.bin{Colors.ENDC} file using secure AES 256bit encryption.\n"
            + f"{Colors.WARNING}WARNING: DO NOT SHARE YOUR PRIVATE KEY, {Colors.BOLD}privkey.bin{Colors.ENDC}{Colors.WARNING} FILE AND PASSWORD WITH ANYONE."
            + f"For better security, use strong password.{Colors.ENDC}\n"
        )
        Henomorphs.SaveKey(input("Enter private key: "), input("Enter password: "))
        print(
            f"{Colors.OKGREEN}Succesfully stored key{Colors.ENDC}\n"
            + f"Please create configuration file (if You don't do it yet) and restart the script."
        )
        exit()

    while True:
        print(f"{Colors.HEADER}Henomorphs Python{Colors.ENDC}{Colors.OKCYAN}")
        print(f"-" * 50)
        print(f"$POL: {hen.GetPol()}\n$ZICO: {hen.GetZico()}")
        print(f"-" * 50, end=f"\n{Colors.ENDC}")
        checkApproval(hen)
        print("1) Display info")
        print("2) Inspect")
        print("3) Perform Action")
        print("4) Repair Wear")
        print("5) Repair Charge")
        print("6) Check rewards / claim")
        print("7) Check ZICO approval")
        print("0) Exit")
        match (input("Select function: ")):
            case "1":
                hen.PrintInfo()
            case "2":
                hen.Inspect()
            case "3":
                PerformAction(hen)
            case "4":
                hen.RepairWear(
                    int(input("Threshold: ")), int(input("Max Wear reduction: "))
                )
            case "5":
                hen.RepairCharge(
                    int(input("Threshold: ")), int(input("Max charge to add: "))
                )
            case "6":
                rewards = hen.GetPendingRewards()
                print(f"Pending rewards: {rewards[0]}, tokens: {rewards[1]}")
                if input("Claim? [y/n]: ") == "y":
                    hen.ClaimAll(rewards[1])
            case "7":
                ApproveZico(hen)
            case "0":
                exit()


def PerformAction(hen):
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
        match (input("Select function: ")):
            case "1":
                hen.PerformColonyActionSequence()
                return
            case "2":
                hen.PerformColonyActionBatch()
                return
            case "0":
                return


def ApproveZico(hen):
    while True:
        print(f"{Colors.HEADER}Select contract address{Colors.ENDC}")
        print(
            f"{Colors.OKCYAN}1) NFT (0xCEaA...D61f) - Inspection ({hen.GetZicoApproval(hen.contract_nft_address)})"
        )
        print(
            f"{Colors.OKCYAN}2) HenomorphsChargepod (0xA899...Db76) - Actions, Repair charge ({hen.GetZicoApproval(hen.contract_chargepod_address)})"
        )
        print(
            f"{Colors.OKCYAN}3) HenomorphsStaking (0xA16C...97BE) - Repair Wear ({hen.GetZicoApproval(hen.contract_staking_address)})"
        )
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
        print(
            f"{Colors.WARNING}WARNING: Low ZICO approval. Please check approval to avoid errors.",
            end="",
        )
        print(f"-" * 50, end=f"\n{Colors.ENDC}")


if __name__ == "__main__":
    main()
