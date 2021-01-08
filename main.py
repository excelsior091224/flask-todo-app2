from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.datastructures import MultiDict

app = Flask(__name__)

app.config.from_object('config')
crsf = CSRFProtect(app)

db = SQLAlchemy(app)

JST = timezone(timedelta(hours=+9), 'JST')

class Tasks(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text)
    status = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.now(JST))
    updated = db.Column(db.DateTime, default=datetime.now(JST))

    def __repr__(self):
        return '<Task %r, %r, %r, %r, %r>' % (
            self.id, 
            self.title, 
            self.text, 
            self.status, 
            self.created, 
            self.updated
            )

class Insert(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired(message='入力必須項目です'), 
    Length(max=200, message='200文字以下にしてください')])
    text = TextAreaField('詳細')
    status = SelectField('状態', choices=[(0, '未実行'), (1, '実行中')])
    submit = SubmitField('作成')

class Edit(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired(message='入力必須項目です'), 
    Length(max=200, message='200文字以下にしてください')])
    text = TextAreaField('詳細')
    status = SelectField('状態', choices=[(0, '未実行'), (1, '実行中'), (2, '完了')])
    submit = SubmitField('作成')

@app.route('/', methods=['GET', 'POST'])
def index():
    form_i = Insert()
    if request.method == 'POST' and form_i.validate_on_submit:
        new_task = Tasks(
            title=form_i.title.data,
            text=form_i.text.data,
            status=form_i.status.data,
            created=datetime.now(JST),
            updated=datetime.now(JST)
        )
       
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        tasks = Tasks.query.order_by(Tasks.updated.desc()).all()
        return render_template('index.html', tasks=tasks, form_i=form_i)

@app.route('/tasks/<int:id>')
def detail(id):
    task = Tasks.query.filter_by(id=id).first()
    return render_template('detail.html', task=task)

@app.route('/tasks/<int:id>/delete')
def delete(id):
    task_to_delete = Tasks.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    task_to_edit = Tasks.query.get_or_404(id)
    form_e = Edit()
    if request.method == 'POST' and form_e.validate_on_submit:
        task_to_edit.title = form_e.title.data
        task_to_edit.text = form_e.text.data
        task_to_edit.status = form_e.status.data
        task_to_edit.updated = datetime.now(JST)
        db.session.commit()
        return redirect(url_for('detail', id=id))
    else:
        form_e = Edit(formdata=MultiDict({'title': task_to_edit.title, 'text': task_to_edit.text, 'status': task_to_edit.status}))
        return render_template('edit.html', task=task_to_edit, form_e=form_e)

if __name__ == "__main__":
    db.create_all()
    app.run(port=8080)