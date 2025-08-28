import json
from lib.Colors import Colors


class HenoAutoGenConfig:
    @staticmethod
    def genConfig(hen):
        henCopy = hen.tokens
        hen.tokens = []

        data = hen.contract_staking.functions.getDetailedStakedTokensByAddress(
            hen.public_address
        ).call()

        for d in data:
            hen.tokens.append(
                {"CollectionID": int(d[1]), "TokenID": int(d[2]), "Action": 0}
            )

        for d in henCopy:
            r = next(
                (
                    obj
                    for obj in hen.json["Henomorphs"]
                    if obj["CollectionID"] == d["CollectionID"]
                    and obj["TokenID"] == d["TokenID"]
                ),
                None,
            )
            if r is not None:
                r["Action"] = d["Action"]

        hen.json["Henomorphs"] = sorted(
            hen.json["Henomorphs"], key=lambda h: (h["CollectionID"], h["TokenID"])
        )

        with open(hen.henoConfPath, "w") as file:
            file.write(json.dumps(hen.json, indent=2))

        print(
            f"{Colors.OKGREEN}Generated {hen.henoConfPath}\nPlease review the file and fill missing data (eg. actions){Colors.ENDC}"
        )
        exit()
