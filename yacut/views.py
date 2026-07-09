from flask import flash, redirect, render_template

from . import app
from .forms import URLMapForm, FileUploadForm
from .models import URLMap
from .yandex_disk import async_upload_files
from .error_handlers import InvalidAPIUsage


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    short_link = None
    if form.validate_on_submit():
        try:
            url_map = URLMap.create(
                original=form.original_link.data,
                custom_id=form.custom_id.data
            )
            short_link = url_map.get_short_link()
        except InvalidAPIUsage as e:
            flash(e.message)
            return render_template('index.html', form=form)
    return render_template('index.html', form=form, short_link=short_link)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FileUploadForm()
    results = []
    if form.validate_on_submit():
        files = form.files.data
        results = await async_upload_files(files)
    return render_template('files.html', form=form, results=results)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
