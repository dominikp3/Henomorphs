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


import socket
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
    exit(42)


def main():
    sys.excepthook = except_hook
    Colors.WindowsEnableColors()

    if len(sys.argv) == 4:
        (account, hConf, cConf) = (sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: main.py <account> <henoConfig> <colonyConfig>")
        exit(99)

    if Henomorphs.IsKeySaved(account):
        try:
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind(("localhost", 4242))
            serversocket.listen(1)
            (clientsocket, address) = serversocket.accept()
            data = clientsocket.recv(1000)
            password = data.decode("utf-8")
            clientsocket.close()
            serversocket.close()
        except socket.error:
            print(f"{Colors.FAIL}Error receiving password{Colors.ENDC}")
            exit(2)

        try:
            hen = Henomorphs(account, password, hConf, colonyConfFile=cConf)
        except InvalidPasswordError:
            print(f"{Colors.FAIL}Invalid password or privkey.bin corrupted{Colors.ENDC}")
            exit(3)
    else:
        print(f"{Colors.FAIL}Key not saved{Colors.ENDC}")
        exit(1)

    hen.CWAIDefender()


if __name__ == "__main__":
    main()
