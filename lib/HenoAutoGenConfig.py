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
                {
                    "CollectionID": int(d[1]),
                    "TokenID": int(d[2]),
                    "Action": 0,
                    "Spec": hen.GetSpec2(d[1], d[2]),
                }
            )

        for d in henCopy:
            r = next(
                (
                    obj
                    for obj in hen.tokens
                    if obj["CollectionID"] == d["CollectionID"]
                    and obj["TokenID"] == d["TokenID"]
                ),
                None,
            )
            if r is not None:
                r["Action"] = d["Action"]
                # if d.get("Spec", -1) > -1:
                #     r["Spec"] = d["Spec"]

        hen.tokens = sorted(hen.tokens, key=lambda h: (h["CollectionID"], h["TokenID"]))

        with open(hen.henoConfPath, "w") as file:
            file.write(json.dumps(hen.tokens, indent=2))

        print(
            f"{Colors.OKGREEN}Generated {hen.henoConfPath}\nPlease review the file and fill missing data (eg. actions){Colors.ENDC}"
        )
        exit()
