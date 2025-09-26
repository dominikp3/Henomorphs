#!/bin/python3

import getpass
import socket

password = getpass.getpass("Password: ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 4242))
s.send(password.encode("utf-8"))
