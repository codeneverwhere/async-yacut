from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .exceptions import (
    InvalidShortIDError,
    ShortIDAlreadyExistsError,
    ShortIDGenerationError,
)
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    try:
        url_map = URLMap.create(
            original=data['url'],
            custom_id=data.get('custom_id')
        )
    except (InvalidShortIDError, ShortIDAlreadyExistsError) as e:
        raise InvalidAPIUsage(str(e))
    except ShortIDGenerationError as e:
        raise InvalidAPIUsage(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.get_by_short(short_id)
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
