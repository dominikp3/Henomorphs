from lib.Henomorphs import Henomorphs
from lib.XorEncryption import InvalidKeyException
from lib.Colors import Colors
import getpass
import sys
import traceback

def except_hook(exctype, value, t):
    if exctype == KeyboardInterrupt:
        print(f"{Colors.HEADER}Good Bye{Colors.ENDC}")
    else:
        print(Colors.FAIL)
        traceback.print_exception(value)
        print(Colors.ENDC)
    exit()

sys.excepthook = except_hook

if Henomorphs.IsKeySaved():
    try:
        hen = Henomorphs(getpass.getpass("Password: "))
    except InvalidKeyException:
        print(f"{Colors.FAIL}Invalid password{Colors.ENDC}")
        exit()
else:
    Henomorphs.SaveKey(input("Enter private key: "), input("Enter password: "))
    exit()

while True:
    print(f"{Colors.HEADER}Henomorphs Python{Colors.ENDC}")
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
            hen.RepairWear(int(input("Threshold: ")), int(input("Max Wear reduction: ")))
        case "5":
            hen.RepairCharge(int(input("Threshold: ")), int(input("Max charge to add: ")))
        case "6":
            print("Pending rewards: " + str(hen.GetPendingRewards()))
            if input("Claim? [y/n]: ") == "y":
                hen.ClaimAll()
        case "7":
            exit()
        case "0":
            exit()
