import random
import string

from flask import flash, redirect, render_template, url_for

from . import app, db
from .forms import URLMapForm, FileUploadForm
from .models import URLMap


ALLOWED_CHARS = string.ascii_letters + string.digits


def get_unique_short_id(length=6):
    while True:
        short_id = ''.join(random.choices(ALLOWED_CHARS, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    short_link = None
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        if custom_id:
            if custom_id == 'files' or URLMap.query.filter_by(
                short=custom_id
            ).first():
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('index.html', form=form)
        else:
            custom_id = get_unique_short_id()
        url_map = URLMap(
            original=form.original_link.data,
            short=custom_id
        )
        db.session.add(url_map)
        db.session.commit()
        short_link = url_for(
            'redirect_view',
            short_id=custom_id,
            _external=True
        )
    return render_template('index.html', form=form, short_link=short_link)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FileUploadForm()
    results = []
    if form.validate_on_submit():
        from .yandex_disk import async_upload_files
        files = form.files.data
        results = await async_upload_files(files)
    return render_template('files.html', form=form, results=results)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
