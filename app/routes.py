from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.forms import LoginForm, RegistrationForm, EventForm
from app.models import User, Event
from urllib.parse import urlparse
from datetime import datetime, timedelta
from dateutil import parser
from zoneinfo import ZoneInfo

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    now = datetime.now(tz=ZoneInfo('UTC'))
    soon = now + timedelta(minutes=30)
    reminders = Event.query.filter(
        Event.user_id == current_user.id,
        Event.reminder != None,
    ).all()
    return render_template('index.html', title='Главная', reminders=reminders)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильное имя пользователя или пароль')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, вы зарегистрированы!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Регистрация', form=form)

@bp.route('/events')
@login_required
def events():
    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.date.asc(), Event.time.asc()).all()
    return render_template('events.html', events=events)

@bp.route('/event/add', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    if request.method == 'GET':
        date_str = request.args.get('date')
        if date_str:
            try:
                form.date.data = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
    if form.validate_on_submit():
        reminder_utc = None
        if form.reminder.data:
            local_dt = form.reminder.data
            local_dt = local_dt.replace(tzinfo=ZoneInfo('Europe/Moscow'))
            reminder_utc = local_dt.astimezone(ZoneInfo('UTC'))

        event = Event(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            time=form.time.data,
            color=form.color.data if form.color.data != 'default' else None,
            reminder=reminder_utc
        )
        db.session.add(event)
        db.session.commit()
        flash('Событие добавлено')
        return redirect(url_for('main.events'))
    return render_template('event_form.html', form=form, title='Добавить событие')

@bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        reminder_utc = None
        if form.reminder.data:
            local_dt = form.reminder.data
            local_dt = local_dt.replace(tzinfo=ZoneInfo('Europe/Moscow'))
            reminder_utc = local_dt.astimezone(ZoneInfo('UTC'))

        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.time = form.time.data
        event.color = form.color.data if form.color.data != 'default' else None
        event.reminder = reminder_utc
        db.session.commit()
        flash('Событие обновлено')
        return redirect(url_for('main.events'))
    return render_template('event_form.html', form=form, title='Редактировать событие')

@bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash('Событие удалено')
    return redirect(url_for('main.events'))

@bp.route('/api/events')
@login_required
def api_events():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    try:
        start = parser.isoparse(start_str) if start_str else None
        end = parser.isoparse(end_str) if end_str else None
    except Exception:
        return jsonify([])

    query = Event.query.filter(Event.user_id == current_user.id)
    if start:
        query = query.filter(Event.date >= start.date())
    if end:
        query = query.filter(Event.date <= end.date())

    events = query.all()

    events_json = []
    for e in events:
        if e.time:
            dt_start = datetime.combine(e.date, e.time).replace(tzinfo=ZoneInfo("Europe/Moscow"))
            dt_utc_start = dt_start.astimezone(ZoneInfo("UTC"))
            dt_utc_end = dt_utc_start + timedelta(minutes=30)

            events_json.append({
                'id': e.id,
                'title': e.title,
                'start': dt_utc_start.isoformat(),
                'end': dt_utc_end.isoformat(),
                'color': e.color if e.color else None,
                'allDay': False
            })
        else:

            dt_start = datetime.combine(e.date, datetime.min.time()).replace(tzinfo=ZoneInfo("Europe/Moscow"))
            dt_utc_start = dt_start.astimezone(ZoneInfo("UTC"))

            events_json.append({
                'id': e.id,
                'title': e.title,
                'start': dt_utc_start.isoformat(),
                'allDay': True,
                'color': e.color if e.color else None
            })

    return jsonify(events_json)

@bp.route('/api/reminders')
@login_required
def api_reminders():
    now = datetime.now(tz=ZoneInfo('UTC'))
    events = Event.query.filter(
        Event.user_id == current_user.id,
        Event.reminder != None,
        Event.reminder <= now,
        Event.reminder_seen == False
    ).all()

    reminders = [{
        'id': e.id,
        'title': e.title,
        'reminder': e.reminder.isoformat()
    } for e in events]

    return jsonify(reminders)


@bp.route('/api/reminders/<int:event_id>/seen', methods=['POST'])
@login_required
def mark_reminder_seen(event_id):
    event = Event.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()
    event.reminder_seen = True
    db.session.commit()
    return jsonify({'status': 'ok'})

