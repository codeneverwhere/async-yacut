import random
import re
from datetime import datetime

from flask import url_for
from yacut import db

from .constants import (
    ALLOWED_CHARS,
    FORBIDDEN_SHORT_IDS,
    MAX_ATTEMPTS,
    ORIGINAL_LINK_MAX_LENGTH,
    SHORT_ID_LENGTH,
    SHORT_ID_MAX_LENGTH,
    SHORT_ID_PATTERN,
)
from .exceptions import (
    InvalidShortIDError,
    ShortIDAlreadyExistsError,
    ShortIDGenerationError,
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(ORIGINAL_LINK_MAX_LENGTH), nullable=False
    )
    short = db.Column(
        db.String(SHORT_ID_MAX_LENGTH), unique=True, nullable=False
    )
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )

    def to_dict(self):
        return dict(
            url=self.original,
            short_link=self.get_short_link()
        )

    def from_dict(self, data):
        self.original = data.get('url')
        self.short = data.get('custom_id')

    def get_short_link(self):
        return url_for(
            'redirect_view',
            short_id=self.short,
            _external=True
        )

    @staticmethod
    def get_by_short(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def get_unique_short_id():
        for _ in range(MAX_ATTEMPTS):
            short_id = ''.join(
                random.choices(ALLOWED_CHARS, k=SHORT_ID_LENGTH)
            )
            if not URLMap.get_by_short(short_id):
                return short_id
        raise ShortIDGenerationError(
            'Не удалось сгенерировать уникальный идентификатор'
        )

    @staticmethod
    def create(original, custom_id=None):
        if custom_id:
            if (
                len(custom_id) > SHORT_ID_MAX_LENGTH
                or not re.match(SHORT_ID_PATTERN, custom_id)
            ):
                raise InvalidShortIDError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if (
                custom_id in FORBIDDEN_SHORT_IDS
                or URLMap.get_by_short(custom_id)
            ):
                raise ShortIDAlreadyExistsError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
        else:
            custom_id = URLMap.get_unique_short_id()
        url_map = URLMap(original=original, short=custom_id)
        db.session.add(url_map)
        db.session.commit()
        return url_map
