import math
from lib.Colors import Colors
from lib.HenoBase import HenoBase


class HenoZico(HenoBase):
    def ClaimAll(self, tokensCount):
        self.logger.log(f"Started rewards claim, {tokensCount} tokens")

        def _ClaimAll(_, p):
            print(f"Claiming rewards (Chunk {p[0]+1}/{p[1]}):", end=" ", flush=True)
            self.logger.log(f"Claiming rewards (Chunk {p[0]+1}/{p[1]})")
            self.Transaction(
                self.contract_staking.functions.claimBatchStakingRewards(30)
            )
            self.printSuccessMessage()

        if tokensCount <= 0:
            print(
                f"{Colors.FAIL}You need at least 1 staked token to claim rewards{Colors.ENDC}"
            )
            self.logger.log(f"Error: You need at least 1 staked token to claim rewards")
            return

        chunks = math.ceil(tokensCount / 30)
        for i in range(chunks):
            if not self.TryAction(_ClaimAll, (i, chunks)):
                print(f"{Colors.FAIL}Claiming failed!{Colors.ENDC}")
                self.logger.log("Claiming failed!")
                return

    def GetPendingRewards(self):
        data = self.contract_staking.call_decoded(
            "getUserStakingOverview", self.public_address
        )
        return data

    def printPendingRewards(self, rewards):
        print(
            f"Staked: {rewards["stakedCount"]}\n"
            f"Pending rewards: {rewards["pendingRewards"] / self.ZicoDividor} YLW\n"
            f"Lifetime earnings: {rewards["lifetimeEarnings"] / self.ZicoDividor} YLW\n"
            f"Estimated daily rate: {rewards["estimatedDailyRate"] / self.ZicoDividor} YLW\n"
        )

    def GetPol(self) -> float:
        return self.web3.eth.get_balance(self.public_address) / self.ZicoDividor

    def GetZico(self) -> float:
        return (
            self.contract_zico.functions.balanceOf(self.public_address).call()
            / self.ZicoDividor
        )

    def GetYlw(self) -> float:
        return (
            self.contract_ylw.functions.balanceOf(self.public_address).call()
            / self.ZicoDividor
        )

    def GetZicoApproval(self, spender) -> float:
        return (
            self.contract_zico.functions.allowance(self.public_address, spender).call()
            / self.ZicoDividor
        )

    def ApproveZico(self, spender, value):
        def _ApproveZico(*_):
            print(f"Approving ZICO ({spender}, {value}):", end=" ", flush=True)
            self.logger.log(f"Approving ZICO ({spender}, {value})")
            self.Transaction(
                self.contract_zico.functions.approve(spender, value * self.ZicoDividor)
            )
            self.printSuccessMessage()

        if value < 0:
            print(f"{Colors.FAIL}Value must be greater than zero{Colors.ENDC}")
            return

        self.TryAction(_ApproveZico, None)
