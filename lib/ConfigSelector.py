import os
import re
from lib.Colors import Colors


# Returns (account name (dir name, empty for default), heno config filename, (optional) colony config)
def GetConfig() -> tuple[str, str, str]:
    account = ""
    config = ""
    config_colony = None

    pattern = re.compile(r"^(?!logs).*")
    accounts = [d for d in os.listdir("userdata/") if os.path.isdir(f"userdata/{d}") and pattern.match(d)]
    if len(accounts) > 0:
        print(f"{Colors.HEADER}Multiple accounts detected:{Colors.ENDC}")
        print("1) Default account")
        i = 2
        for a in accounts:
            print(f"{i}) {a}")
            i += 1
        if 0 < (v := int(input("Select account: "))) < i:
            if v > 1:
                account = f"{accounts[v-2]}/"
        else:
            print(f"{Colors.FAIL}Selected non existing account!{Colors.ENDC}")
            exit()

    pattern = re.compile(r".*heno.*.json")
    configs = [d for d in os.listdir(f"userdata/{account}") if pattern.match(d)]
    if len(configs) <= 0:
        print(f"{Colors.WARNING}No heno config found!\n" + f"Selecting default 'heno.json'{Colors.ENDC}")
        config = "heno.json"
    elif len(configs) == 1:
        config = configs[0]
    else:
        print(f"{Colors.HEADER}Multiple configs detected:{Colors.ENDC}")
        i = 1
        for c in configs:
            print(f"{i}) {c}")
            i += 1
        if 0 < (v := int(input("Select config: "))) < i:
            config = configs[v - 1]
        else:
            print(f"{Colors.FAIL}Selected non existing config!{Colors.ENDC}")
            exit()

    pattern = re.compile(r".*colony.*.json")
    configs = [d for d in os.listdir(f"userdata/{account}") if pattern.match(d)]
    if len(configs) <= 0:
        pass
    elif len(configs) == 1:
        config_colony = configs[0]
    else:
        print(f"{Colors.HEADER}Multiple colony configs detected:{Colors.ENDC}")
        i = 1
        for c in configs:
            print(f"{i}) {c}")
            i += 1
        if 0 < (v := int(input("Select config: "))) < i:
            config_colony = configs[v - 1]
        else:
            print(f"{Colors.FAIL}Selected non existing config!{Colors.ENDC}")
            exit()

    return (account, config, config_colony)
