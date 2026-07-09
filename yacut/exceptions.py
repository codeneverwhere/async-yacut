class ShortIDGenerationError(Exception):
    """Не удалось сгенерировать уникальный короткий идентификатор."""
    pass


class ShortIDAlreadyExistsError(Exception):
    """Предложенный вариант короткой ссылки уже существует."""
    pass


class InvalidShortIDError(Exception):
    """Указано недопустимое имя для короткой ссылки."""
    pass
