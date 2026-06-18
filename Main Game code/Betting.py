import random

# ---------------- ROULETTE COLORS ----------------
RED = {1,3,5,7,9,11,13,15,17,19,21,23,25}
BLACK = {2,4,6,8,10,12,14,16,18,20,22,24}


class BettingSystem:
    def __init__(self, starting_balance=600):
        self.balance = starting_balance
        self.bet = None
        self.bets = []
        self.last_refund = 0

    def set_bet(self, bet_type, amount, deduct=True):
        self.last_refund = 0

        if amount <= 0 or (deduct and amount > self.balance):
            return False

        if bet_type not in ["red", "black"] and not bet_type.isdigit():
            return False

        if bet_type.isdigit():
            num = int(bet_type)
            if num < 0 or num > 25:
                return False

        bet_item = {
            "type": bet_type,
            "amount": amount
        }
        self.bet = bet_item
        self.bets.append(bet_item)

        if deduct:
            self.balance -= amount
        return True

    def resolve(self, result, refund_rate=0.0, bonus_amount=0):
        
        if not self.bets:
            return 0

        total_wager = sum(bet["amount"] for bet in self.bets)
        total_return = 0
        self.last_refund = 0

        for bet in self.bets:
            bet_type = bet["type"]
            amount = bet["amount"]
            payout = 0

            if bet_type == "red" and result in RED:
                payout = amount * 2
            elif bet_type == "black" and result in BLACK:
                payout = amount * 2
            elif bet_type.isdigit() and int(bet_type) == result:
                payout = amount * 4

            if payout > 0:
                payout += bonus_amount
                total_return += payout
            else:
                refund = int(amount * refund_rate)
                self.last_refund += refund
                total_return += refund

        self.balance += total_return
        self.bets = []
        self.bet = None
        
        return total_return

    def reset(self):
        self.balance = 600
        self.bet = None
        self.bets = []