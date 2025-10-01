from dataclasses import dataclass


@dataclass
class Common:
    pass


@dataclass
class Sso:
    pass


@dataclass
class Profile:
    pass


@dataclass
class Toys:
    TOY_BY_ID: int = 24 * 60 * 60  # 24 hours
    TOYS_CATALOG: int = 5 * 60  # 5 min


@dataclass
class Masters:
    MASTERS_CATALOG: int = 5 * 60


@dataclass
class Test:
    ONE_MINUTE: int = 1 * 60


@dataclass
class CacheTTL:
    COMMON = Common()
    SSO = Sso()
    PROFILE = Profile()
    TOYS = Toys()
    MASTERS = Masters()
    TEST = Test()
    DEFAULT: int = 5 * 60  # 5 min
