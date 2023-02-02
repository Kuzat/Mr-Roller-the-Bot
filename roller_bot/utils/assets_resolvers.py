import enum

from discord import File


class Trophies(enum.Enum):
    first = 0
    second = 1
    third = 2
    fourth = 3
    fifth = 4


class AssetsResolvers:
    @staticmethod
    def resolve_trophy_asset(trophy_position: Trophies) -> File:
        return File(f'assets/trophy_{trophy_position.value + 1}.png', filename=f'trophy_{trophy_position.value + 1}.png')
