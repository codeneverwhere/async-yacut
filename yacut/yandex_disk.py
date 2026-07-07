import asyncio
import urllib.parse

import aiohttp

from . import app

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


def get_auth_headers():
    return {
        'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'
    }


async def upload_one_file(session, file):
    filename = file.filename
    file_data = file.read()
    disk_path = 'app:/' + filename

    # Шаг 1: получить URL для загрузки
    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=get_auth_headers(),
        params={'path': disk_path, 'overwrite': 'True'}
    ) as response:
        data = await response.json()
        upload_url = data['href']

    # Шаг 2: загрузить файл, получить путь из Location
    async with session.put(
        upload_url,
        data=file_data
    ) as response:
        location = response.headers.get('Location', '')
        location = urllib.parse.unquote(location)
        location = location.replace('/disk', '')

    # Шаг 3: получить ссылку на скачивание используя location
    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=get_auth_headers(),
        params={'path': location if location else disk_path}
    ) as response:
        data = await response.json()
        download_url = data['href']

    return filename, download_url


async def async_upload_files(files):
    results = []
    if not files:
        return results

    from .views import get_unique_short_id
    from .models import URLMap
    from . import db

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.ensure_future(upload_one_file(session, file))
            for file in files
            if file.filename
        ]
        uploads = await asyncio.gather(*tasks)

    for filename, download_url in uploads:
        short_id = get_unique_short_id()
        url_map = URLMap(
            original=download_url,
            short=short_id
        )
        db.session.add(url_map)
        db.session.commit()
        results.append((filename, short_id))

    return results
