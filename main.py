from lib.Henomorphs import Henomorphs
from lib.Encryption import InvalidPasswordError
from lib.Colors import Colors
import getpass
import sys
import traceback
import os


def except_hook(exctype, value, t):
    if exctype == KeyboardInterrupt:
        print(f"{Colors.HEADER}Good Bye{Colors.ENDC}")
    else:
        print(Colors.FAIL)
        traceback.print_exception(value)
        print(Colors.ENDC)
    exit()


sys.excepthook = except_hook
Colors.WindowsEnableColors()
if not os.path.exists("userdata"):
    os.makedirs("userdata")

if Henomorphs.IsKeySaved():
    try:
        hen = Henomorphs(getpass.getpass("Password: "))
    except InvalidPasswordError:
        print(f"{Colors.FAIL}Invalid password or privkey.bin corrupted{Colors.ENDC}")
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
    print("1) Display info")
    print("2) Inspect")
    print("3) Perform Action")
    print("4) Repair Wear")
    print("5) Repair Charge")
    print("6) Check rewards / claim")
    print("7) Exit")
    match (input("Select function: ")):
        case "1":
            hen.PrintInfo()
        case "2":
            hen.Inspect()
        case "3":
            hen.PerformColonyAction()
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
            exit()
        case "0":
            exit()
