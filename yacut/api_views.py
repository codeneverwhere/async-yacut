import re

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if not data.get('url'):
        raise InvalidAPIUsage('"url" является обязательным полем!')
    custom_id = data.get('custom_id')
    if custom_id:
        if not isinstance(custom_id, str):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if len(custom_id) > 16 or not re.match(r'^[a-zA-Z0-9]+$', custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if custom_id == 'files' or URLMap.query.filter_by(
            short=custom_id
        ).first():
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
    else:
        custom_id = get_unique_short_id()
    url_map = URLMap()
    url_map.from_dict({'url': data['url'], 'custom_id': custom_id})
    db.session.add(url_map)
    db.session.commit()
    return jsonify(url_map.to_dict()), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200
