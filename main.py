from pathlib import Path

from flask import Flask, render_template, redirect, request, url_for, Response, make_response, jsonify
import os
from data import db_session, users_api, accommodation_api
from data.accommodation import Accommodation
from data.db_session import create_session
from data.user import User
from forms import RegisterForm, LoginForm, AccommodationAddForm, ProfileForm, ChangeAccommodationForm
from flask_login import login_user, LoginManager, logout_user, current_user
from random import shuffle

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECr  et___k3y...:::EL_PSY_KONGROO::...yek_terces'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


def main():
    db_session.global_init("db/data.db")
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(accommodation_api.blueprint)
    app.run()


@app.route('/')
def main_page():
    db_sess = db_session.create_session()
    accommodations = db_sess.query(Accommodation).all()
    shuffle(accommodations)
    return render_template('main.html', accommodations=accommodations)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            username=form.login.data,
            email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/enter')
    return render_template('register.html', title='Регистрация', form=form, message='')


@app.route('/login')
def login_():
    return redirect('/enter')


@app.route('/enter', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('enter.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('enter.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/about')
def about():
    return 'О нас (пока пусто)'


@app.route('/add_accommodation', methods=['GET', 'POST'])
def add_accommodation():
    if not current_user.is_authenticated:
        return redirect('/')
    form = AccommodationAddForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        accommodation = Accommodation(
            name = form.name.data,
            cost = form.cost.data,
            description = form.description.data,
            address = form.address.data,
            accommodation_owner = current_user.id
        )
        db_sess.add(accommodation)
        db_sess.commit()
        photo_path = f'static/images/accommodation_images/{accommodation.id}_folder/'
        try:
            os.makedirs(photo_path)
        except FileExistsError:
            pass
        count = 0
        for file in form.photo.data:
            count += 1
            with open(photo_path + str(count) + '.jpg', 'wb') as photo:
                photo.write(file.read())
        photo_path = f'images/accommodation_images/{accommodation.id}_folder'
        accommodation.photo_path = photo_path
        db_sess.commit()
        return Response('Успешно! Перенаправляем через 3 секунды...', headers={'Refresh': '3; url=' + url_for('main_page')})
    return render_template('advertisement.html', form=form)


@app.route('/user_profile/<user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).where(User.id == user_id).first()
    if not user:
        return redirect('/#')
    date = '.'.join((str(user.registration_date)).split()[0].split('-'))
    rating = '★' * int(user.rating) + '☆' * (5 - int(user.rating))
    filename = f'images/users/{user_id}.jpg'
    form = ProfileForm()
    if form.validate_on_submit():
        photo_path = f'static/images/users/{user_id}.jpg'
        with open(photo_path, 'wb') as photo:
            photo.write(form.photo.data.read())
        photo_path = f'images/users/{user_id}.jpg'
        user.picture_path = photo_path
        db_sess.commit()
    return render_template('user_profile.html', user=user, date=date, rating=rating, form=form, filename=filename,
                           accommodations=user.housing)


@app.route('/accommodation_page/<accommodation_id>')
def accommodation_page(accommodation_id):
    db_sess = create_session()
    accommodation = db_sess.query(Accommodation).where(Accommodation.id == accommodation_id).first()
    if not accommodation:
        return redirect('/#')
    filename = accommodation.photo_path[6:]
    rating = '★' * int(accommodation.rating) + '☆' * (5 - int(accommodation.rating))
    date = '.'.join((str(accommodation.date)).split()[0].split('-'))
    owner = accommodation.owner
    number = False
    if owner.phone_number is not None:
        number = True
    path = Path(f'static/images/accommodation_images/{accommodation.id}_folder')
    pic_number = sum(1 for x in path.iterdir())
    images = [f'images/accommodation_images/{accommodation.id}_folder/{x}.jpg' for x in range(1, pic_number + 1)]
    return render_template('adver.html', accommodation=accommodation, filename=filename, rating=rating,
                           number=number, date=date, images=images)


@app.route('/delete/<accommodation_id>')
def delete_accommodation(accommodation_id):
    db_sess = create_session()
    accommodation = db_sess.query(Accommodation).where(Accommodation.id == accommodation_id).first()
    if not accommodation:
        return redirect('/#')
    user_id = accommodation.owner.id
    if current_user.id == accommodation.owner.id:
        db_sess.delete(db_sess.query(Accommodation).filter(Accommodation.id == accommodation_id).first())
        db_sess.commit()
    return redirect(f'/user_profile/{user_id}')


@app.route('/change/<accommodation_id>', methods=['GET', 'POST'])
def change_accommodation(accommodation_id):
    db_sess = create_session()
    accommodation = db_sess.query(Accommodation).where(Accommodation.id == accommodation_id).first()
    form = ChangeAccommodationForm()
    if form.validate_on_submit():
        accommodation.name = form.name.data
        accommodation.cost = form.cost.data
        accommodation.description = form.description.data
        with open('static/' + accommodation.photo_path, 'wb') as photo:
            photo.write(form.photo.data.read())
        return redirect('/')
    if not accommodation:
        return redirect('/#')
    if current_user.id == accommodation.owner.id:
        return render_template('advertisement.html', form=form)
    else:
        return redirect('/#')


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    main()
