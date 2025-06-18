class Common:
    pass


class Sso:
    pass


class Profile:
    pass


class Toys:
    TOY_BY_ID: int = 24 * 60 * 60  # 24 hours
    TOYS_CATALOG: int = 5 * 60  # 5 min


class Test:
    ONE_MINUTE: int = 1 * 60


class CacheTTL:
    COMMON = Common()
    SSO = Sso()
    PROFILE = Profile()
    TOYS = Toys()
    TEST = Test()
    DEFAULT: int = 5 * 60  # 5 min
