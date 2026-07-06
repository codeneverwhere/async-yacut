from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=16),
            Regexp(
                r'^[a-zA-Z0-9]+$',
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
