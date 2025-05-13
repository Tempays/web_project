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


@app.template_filter("split")
def split(value: str, separator=" ", maxsplit: int = -1):
    return value.split(separator, maxsplit)


def main():
    try:
        os.makedirs('db')
    except FileExistsError:
        pass
    db_session.global_init("db/data.db")
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(accommodation_api.blueprint)
    app.run()


@app.route('/')
def main_page():
    query = request.args.get("query")
    db_sess = db_session.create_session()
    if query:
        accommodations = db_sess.query(Accommodation).filter(Accommodation.address.ilike(f'%{query}%')).all()
    else:
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
        if db_sess.query(User).filter(User.username == form.login.data).first():
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
    show_rate = True
    db_sess = db_session.create_session()
    user = db_sess.query(User).where(User.id == user_id).first()
    if not user:
        return redirect('/#')
    date = '.'.join((str(user.registration_date)).split()[0].split('-'))
    filename = f'images/users/{user_id}.jpg'
    rating = str(user.rating)
    if not rating:
        rating = 0
    else:
        rating = sum([float(x) for x in rating.split(', ')]) / len([x for x in rating.split(', ')])
    rating = '★' * int(rating) + '☆' * (5 - int(rating))
    form = ProfileForm()
    if form.validate_on_submit():
        photo_path = f'static/images/users/{user_id}.jpg'
        with open(photo_path, 'wb') as photo:
            photo.write(form.photo.data.read())
        photo_path = f'images/users/{user_id}.jpg'
        user.picture_path = photo_path
        db_sess.commit()
    if current_user.is_authenticated:
        if current_user.rated_users != '':
            current_user_rated = [int(x) for x in current_user.rated_users.split(', ') if x != '']
            if int(user_id) in current_user_rated:
                show_rate = False
    else:
        show_rate = False
    return render_template('user_profile.html', user=user, date=date, rating=rating, form=form, filename=filename,
                           accommodations=user.housing, show_rate=show_rate)


@app.route('/accommodation_page/<accommodation_id>', methods=["GET", "POST"])
def accommodation_page(accommodation_id):
    show_rate = True
    db_sess = create_session()
    accommodation = db_sess.query(Accommodation).where(Accommodation.id == accommodation_id).first()
    if not accommodation:
        return redirect('/#')
    filename = accommodation.photo_path[6:]
    rating = accommodation.rating
    if not rating:
        rating = 0
    else:
        rating = sum([float(x) for x in rating.split(', ')]) / len([x for x in rating.split(', ')])
    rating = '★' * int(rating) + '☆' * (5 - int(rating))
    date = '.'.join((str(accommodation.date)).split()[0].split('-'))
    owner = accommodation.owner
    number = False
    if owner.phone_number is not None:
        number = True
    path = Path(f'static/images/accommodation_images/{accommodation.id}_folder')
    pic_number = sum(1 for x in path.iterdir())
    images = [f'images/accommodation_images/{accommodation.id}_folder/{x}.jpg' for x in range(1, pic_number + 1)]
    if current_user.is_authenticated:
        if current_user.rated_accommodations != '':
            current_user_rated = [int(x) for x in current_user.rated_accommodations.split(', ') if x != '']
            if int(accommodation_id) in current_user_rated:
                show_rate = False
    else:
        show_rate = False
    return render_template('adver.html', accommodation=accommodation, filename=filename, rating=rating,
                           number=number, date=date, images=images, show_rate=show_rate)


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


@app.route('/set_city')
def test():
    db_sess = db_session.create_session()
    accommodations = db_sess.query(Accommodation).all()
    return render_template('search.html', accommodations=accommodations)


@app.route('/accommodation_page/rate/<int:accommodation_id>', methods=['POST'])
def accommodation_rate(accommodation_id):
    new_rating = request.form.get("rating")
    db_sess = db_session.create_session()
    accommodation = db_sess.query(Accommodation).where(Accommodation.id == accommodation_id).first()
    if accommodation.rating == '':
        accommodation.rating = str(new_rating)
    else:
        accommodation.rating = str(accommodation.rating) + f', {new_rating}'
    db_sess.commit()
    user = db_sess.query(User).where(User.id == current_user.id).first()
    user.rated_accommodations += f'{accommodation_id}, '
    db_sess.commit()
    return redirect(f'/accommodation_page/{accommodation_id}')


@app.route('/user_profile/rate/<int:user_id>', methods=['POST'])
def user_rate(user_id):
    if not current_user.is_authenticated:
        return make_response(jsonify({"error": 'Forbiddeb'}), 403)
    new_rating = request.form.get("rating")
    db_sess = db_session.create_session()
    user = db_sess.query(User).where(User.id == user_id).first()
    if user.rating == '' or user.rating == 0:
        user.rating = str(new_rating)
    else:
        user.rating = str(user.rating) + f', {new_rating}'
    db_sess.commit()
    user_now = db_sess.query(User).where(User.id == current_user.id).first()
    user_now.rated_users += f'{user_id}, '
    db_sess.commit()
    return redirect(f'/user_profile/{user_id}')


if __name__ == '__main__':
    main()
