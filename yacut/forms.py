from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from .constants import (
    ORIGINAL_LINK_MAX_LENGTH,
    SHORT_ID_MAX_LENGTH,
    SHORT_ID_PATTERN,
)


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            Length(max=ORIGINAL_LINK_MAX_LENGTH)
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=SHORT_ID_MAX_LENGTH),
            Regexp(
                SHORT_ID_PATTERN,
                message='Указано недопустимое имя для короткой ссылки'
            )
        ]
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        'Выбрать файлы',
        validators=[DataRequired(message='Обязательное поле')]
    )
    submit = SubmitField('Загрузить')
