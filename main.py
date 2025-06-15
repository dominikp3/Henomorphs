from lib.Henomorphs import Henomorphs
import getpass

if Henomorphs.IsKeySaved():
    hen = Henomorphs(getpass.getpass("Password: "))
else:
    Henomorphs.SaveKey(input("Enter private key: "), input("Enter password: "))
    exit()

while True:
    print("Henomorphs Python")
    print("1) Display info")
    print("2) Inspect")
    print("3) Perform Action")
    print("4) Repair")
    print("5) Check rewards / claim")
    print("6) Exit")
    match (input("Select function: ")):
        case "1":
            hen.PrintInfo()
        case "2":
            hen.Inspect()
        case "3":
            hen.PerformColonyAction()
        case "4":
            hen.RepairWear(int(input("Threshold: ")), int(input("Wear reduction: ")))
        case "5":
            print("Pending rewards: " + str(hen.GetPendingRewards()))
            if input("Claim? [y/n]: ") == "y":
                hen.ClaimAll()
        case default:
            exit()
