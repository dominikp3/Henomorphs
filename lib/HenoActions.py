import random
import time

from tabulate import tabulate
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoActions(HenoBase):
    def PerformColonyActionSequence(self):
        self.logger.log("Started perform actions (Sequence)")
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
                    self.max_transaction_attempts - attempt
                    >= self.random_action_on_fail
                    and self.random_action_on_fail > 0
                ):
                    action = random.randint(1, 5)
                print(
                    f"Performing action: ({t['CollectionID']}, {t['TokenID']}), {action}",
                    end=" ",
                    flush=True,
                )
                self.logger.log(f"Performing action: ({t['CollectionID']}, {t['TokenID']}), {action}")
                self.Transaction(
                    self.contract_chargepod.functions.performAction(
                        int(t["CollectionID"]), int(t["TokenID"]), int(action)
                    )
                )
                self.printSuccessMessage()
                self.delay()

        for t in self.tokens:
            self.TryAction(_PerformColonyAction, t)

    def PerformColonyActionBatch(self):
        self.logger.log("Started performing actions (Batch)")
        tokens = {}  # (collection, action): [token, ...]

        def _prepare_data(t):
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
                key = (int(t["CollectionID"]), int(t["Action"]))
                if key not in tokens:
                    tokens[key] = []
                tokens[key].append(int(t["TokenID"]))
                print(f"{self.ChickChar}", end=" ", flush=True)

        def _print_data():
            h = ["Collection", "Action", "Tokens"]
            d = []
            for key, value in tokens.items():
                d.append([key[0], key[1], str(value)])
            table = tabulate(d, headers=h)
            print(table)
            self.logger.log(f"Actions table:\n{table}")

        def _perform_batch_action(_, k):
            print(
                f"Performing actions: (Collection: {k[0]}, Action: {k[1]})",
                end=" ",
                flush=True,
            )
            self.logger.log(f"Performing actions: (Collection: {k[0]}, Action: {k[1]})")
            self.Transaction(
                self.contract_chargepod.functions.batchPerformAction(
                    int(k[0]), tokens[k], int(k[1])
                )
            )
            self.printSuccessMessage()
            self.delay()

        print("Preparing chicks ...")
        for t in self.tokens:
            _prepare_data(t)

        if len(tokens) == 0:
            print(f"{Colors.WARNING}No tokens availabe to perform action!{Colors.ENDC}")
            self.logger.log("No tokens availabe to perform action!")
            return

        print("\nHeno Groups:")
        _print_data()

        for k in tokens.keys():
            self.TryAction(_perform_batch_action, k)
