from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple([(elem.value, elem.name) for elem in cls])

    @classmethod
    def from_value(cls, value, allow_none=False):
        for elem in cls:
            if elem.value == value:
                return elem

        if allow_none:
            return None
        else:
            assert False

    @classmethod
    def from_name(cls, name, allow_none=False):
        for elem in cls:
            if elem.name == name:
                return elem

        if allow_none:
            return None
        else:
            assert False

    @classmethod
    def names(cls):
        return [elem.name for elem in cls]


class WalletLogOperationChoices(ChoiceEnum):
    refill = 1
    transfer = 2


class CurrencyChoices(ChoiceEnum):
    USD = 'USD'
    EUR = 'EUR'
    CAD = 'CAD'
    CNY = 'CNY'

    @staticmethod
    def default_currency():
        return 'USD'

    @classmethod
    def rate_choices(cls):
        return tuple([(elem.value, elem.name) for elem in cls if elem.value != cls.default_currency()])
