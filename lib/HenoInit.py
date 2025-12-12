import getpass
import os
import sys
from lib.Colors import Colors
from lib.ConfigSelector import GetConfig
from lib.Encryption import InvalidPasswordError
from lib.Henomorphs import Henomorphs


# Pasword input for daemon mode
# (Linux daemon process cannot get user input via stdin)
def daemon_get_passwd():
    password = ""
    try:
        import socket

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(("localhost", 4242))
        serversocket.listen(1)
        (clientsocket, _) = serversocket.accept()
        data = clientsocket.recv(1000)
        password = data.decode("utf-8")
        clientsocket.close()
        serversocket.close()
    except socket.error:
        print(f"{Colors.FAIL}Error receiving password{Colors.ENDC}")
        exit(3)
    return password


def init() -> Henomorphs:
    if not os.path.exists("userdata"):
        os.makedirs("userdata")

    daemon_mode = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "daemon" and len(sys.argv) == 5:
            daemon_mode = True
            if sys.argv[2] == "./":
                sys.argv[2] = ""
        else:
            print("Usage: main.py daemon <account> <henoConfig> <colonyConfig>")
            exit(99)

    if daemon_mode:
        (account, hConf, cConf) = (sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        (account, hConf, cConf) = GetConfig()

    if Henomorphs.IsKeySaved(account):
        password = daemon_get_passwd() if daemon_mode else getpass.getpass("Password: ")
        try:
            hen = Henomorphs(account, password, hConf, colonyConfFile=cConf)
        except InvalidPasswordError:
            print(
                f"{Colors.FAIL}Invalid password or privkey.bin corrupted{Colors.ENDC}"
            )
            exit(1)
    else:
        if daemon_mode:
            print(f"{Colors.FAIL}Key not saved{Colors.ENDC}")
            exit(1)

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

    if daemon_mode:
        hen.CWAIDefender()
        exit()

    return hen
