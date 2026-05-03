class AppError(Exception):
    pass


class AdvertNotFoundError(AppError):
    pass


class NoParsedAdverts(AppError):
    pass


class JobNotFoundError(AppError):
    pass
