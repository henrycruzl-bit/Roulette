import random

RED = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25}
BLACK = {2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24}

class UpgradeManager:
    BONUS_COSTS = {1: 100, 2: 250, 3: 400}
    REFUND_COSTS = {1: 100, 2: 250, 3: 500}
    LUCK_COSTS = {1: 100, 2: 250, 3: 400}

    BONUS_AMOUNTS = {0: 0, 1: 15, 2: 25, 3: 50}
    REFUND_RATES = {0: 0.0, 1: 0.10, 2: 0.25, 3: 0.45}
    LUCK_RATES = {0: 0.0, 1: 0.05, 2: 0.20, 3: 0.40}

    def __init__(self):
        self.bonus_level = 0
        self.refund_level = 0
        self.luck_level = 0

    def reset(self):
        self.bonus_level = 0
        self.refund_level = 0
        self.luck_level = 0

    def get_bonus_amount(self):
        return self.BONUS_AMOUNTS.get(self.bonus_level, 0)

    def get_refund_rate(self):
        return self.REFUND_RATES.get(self.refund_level, 0.0)

    def get_luck_rate(self):
        return self.LUCK_RATES.get(self.luck_level, 0.0)

    def get_bonus_cost(self, level):
        return self.BONUS_COSTS.get(level, 0)

    def get_refund_cost(self, level):
        return self.REFUND_COSTS.get(level, 0)

    def get_luck_cost(self, level):
        return self.LUCK_COSTS.get(level, 0)

    def can_purchase(self, category, level, balance):
        if level < 1 or level > 3:
            return False
        current_level = getattr(self, f"{category}_level", 0)
        if level != current_level + 1:
            return False
        cost = self._get_cost(category, level)
        return balance >= cost

    def purchase(self, category, level, balance):
        if not self.can_purchase(category, level, balance):
            return balance
        cost = self._get_cost(category, level)
        setattr(self, f"{category}_level", level)
        return balance - cost

    def _get_cost(self, category, level):
        if category == "bonus":
            return self.get_bonus_cost(level)
        if category == "refund":
            return self.get_refund_cost(level)
        if category == "luck":
            return self.get_luck_cost(level)
        return 0

    def get_effective_chance(self, bet_type):
        if not bet_type:
            return 0.0
        if bet_type in ["red", "black"]:
            base_chance = 12 / 26
        else:
            base_chance = 1 / 26
        return min(1.0, base_chance + self.get_luck_rate())