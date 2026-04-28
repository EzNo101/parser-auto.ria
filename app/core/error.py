class AppError(Exception):
    pass


class AdvertNotFoundErorr(AppError):
    pass


class NoParsedAdverts(AppError):
    pass
