import json
from lib.Colors import Colors


class HenoAutoGenConfig:
    @staticmethod
    def genConfig(hen):
        henCopy = hen.tokens
        hen.tokens = []
        print("Getting tokens...", end=" ", flush=True)
        data = hen.contract_staking.functions.getDetailedStakedTokensByAddress(hen.public_address).call()
        print(f"\U0001F4DC{hen.ChickChar}")

        for d in data:
            hen.tokens.append(
                {
                    "CollectionID": int(d[1]),
                    "TokenID": int(d[2]),
                    "Action": 0,
                    "Spec": hen.GetSpec2(d[1], d[2]),
                }
            )
            print(f"{hen.ChickChar}", end=" ", flush=True)

        for d in henCopy:
            r = next(
                (obj for obj in hen.tokens if obj["CollectionID"] == d["CollectionID"] and obj["TokenID"] == d["TokenID"]),
                None,
            )
            if r is not None:
                r["Action"] = d["Action"]

        hen.tokens = sorted(hen.tokens, key=lambda h: (h["CollectionID"], h["TokenID"]))

        with open(hen.henoConfPath, "w") as file:
            file.write(json.dumps(hen.tokens, indent=2))

        print(f"\n{Colors.OKGREEN}Generated {hen.henoConfPath}\nPlease review the file and fill missing data (eg. actions){Colors.ENDC}")
        hen.logger.log(f"Generated config file: {hen.henoConfPath}")
        exit()
