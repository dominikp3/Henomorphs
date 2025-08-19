import math
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoZico(HenoBase):
    def ClaimAll(self, tokensCount):
        def _ClaimAll(_, p):
            print(f"Claiming rewards (Chunk {p[0]+1}/{p[1]}):", end=" ", flush=True)
            self.Transaction(
                self.contract_staking.functions.claimRewardsBatchWithProgress(
                    p[0] * 30, 30
                )
            )
            print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")

        if tokensCount <= 0:
            print(
                f"{Colors.FAIL}You need at least 1 staked token to claim rewards{Colors.ENDC}"
            )
            return

        chunks = math.ceil(tokensCount / 30)
        for i in range(math.ceil(tokensCount / 30)):
            if not self.TryAction(_ClaimAll, (i, chunks)):
                print(f"{Colors.FAIL}Claiming failed!{Colors.ENDC}")
                return

    def GetPendingRewards(self) -> tuple[float, int]:
        data = self.contract_staking.functions.getTotalPendingRewardsForAddress(
            self.public_address
        ).call()
        return (data[0] / 1000000000000000000, data[1])

    def GetPol(self) -> float:
        return self.web3.eth.get_balance(self.public_address) / 1000000000000000000

    def GetZico(self) -> float:
        return (
            self.contract_zico.functions.balanceOf(self.public_address).call()
            / 1000000000000000000
        )

    def GetZicoApproval(self, spender) -> float:
        return (
            self.contract_zico.functions.allowance(self.public_address, spender).call()
            / 1000000000000000000
        )

    def ApproveZico(self, spender, value):
        def _ApproveZico(*_):
            print(f"Approving ZICO ({spender}, {value}):", end=" ", flush=True)
            self.Transaction(
                self.contract_zico.functions.approve(
                    spender, value * 1000000000000000000
                )
            )
            print(f"{Colors.OKGREEN}[OK]{Colors.ENDC}")

        if value < 0:
            print(f"{Colors.FAIL}Value must be greater than zero{Colors.ENDC}")
            return

        self.TryAction(_ApproveZico, None)
