from pydantic.main import BaseModel


class DiceRoll(BaseModel):
    base: int
    bonus: int = 0
    can_roll_again: bool = False

    @property
    def total(self) -> int:
        return self.base + self.bonus

    def __repr__(self) -> str:
        if self.bonus > 0:
            return f'{self.base} + {self.bonus} bonus = {self.total}'
        return f'{self.total}'

    def __str__(self) -> str:
        if self.bonus > 0:
            return f'{self.base} + {self.bonus} bonus = {self.total}'
        return f'{self.total}'
