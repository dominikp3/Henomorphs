import json
from lib.Colors import Colors


class HenoAutoGenConfig:
    @staticmethod
    def genConfig(hen):
        if "Config" not in hen.json:
            hen.json["Config"] = {}
        if "Henomorphs" not in hen.json:
            hen.json["Henomorphs"] = []
        if "max_transaction_attempts" not in hen.json["Config"]:
            hen.json["Config"]["max_transaction_attempts"] = 5
        if "random_action_on_fail" not in hen.json["Config"]:
            hen.json["Config"]["random_action_on_fail"] = 2
        if "delay" not in hen.json["Config"]:
            hen.json["Config"]["delay"] = 3

        henCopy = hen.json["Henomorphs"]
        hen.json["Henomorphs"] = []

        data = hen.contract_staking.functions.getDetailedStakedTokensByAddress(
            hen.public_address
        ).call()
        for d in data:
            hen.json["Henomorphs"].append(
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

        with open("userdata/config.json", "w") as file:
            file.write(json.dumps(hen.json, indent=2))

        print(
            f"{Colors.OKGREEN}Generated config.json\nPlease review the file and fill missing data (eg. actions){Colors.ENDC}"
        )
        exit()
