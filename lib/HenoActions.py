import random
import time
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoActions(HenoBase):
    def PerformColonyAction(self):
        def _PerformColonyAction(attempt, t):
            if t["Action"] <= 0:
                print(f"{Colors.WARNING}Token without action, skipping.{Colors.ENDC}")
                return
            data = self.contract_chargepod.functions.getLastTokenAction(
                t["CollectionID"], t["TokenID"]
            ).call()
            if int(time.time()) <= int(data[2]):
                tr = int(data[2]) - int(time.time())
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), token in cooldown preiod. Next action possible in: {int(tr / 60 / 60):02d}:{int((int(tr / 60)) - 60 * int(tr / 60 / 60)):02d}{Colors.ENDC}"
                )
            elif int(time.time()) - int(data[1]) <= 60 * 60:
                print(
                    f"{Colors.WARNING}Skipped token ({t['CollectionID']}, {t['TokenID']}), was performed action recently.{Colors.ENDC}"
                )
            else:
                action = t["Action"]
                if (
                    self.config["max_transaction_attempts"] - attempt
                    >= self.config["random_action_on_fail"]
                    and self.config["random_action_on_fail"] > 0
                ):
                    action = random.randint(1, 5)
                print(
                    f"Performing action: ({t['CollectionID']}, {t['TokenID']}), {action}",
                    end=" ",
                    flush=True,
                )
                self.Transaction(
                    self.contract_chargepod.functions.performAction(
                        int(t["CollectionID"]), int(t["TokenID"]), int(action)
                    )
                )
                print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")
                time.sleep(self.config["delay"])

        for t in self.tokens:
            self.TryAction(_PerformColonyAction, t)
