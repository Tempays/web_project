from flask import Flask, render_template, redirect

from data import db_session
from data.accommodation import Accommodation
from data.db_session import create_session
from data.user import User
from forms import RegisterForm, LoginForm, AccommodationAddForm
from flask_login import login_user, LoginManager, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'special_secret_key_kyoma'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


def main():
    db_session.global_init("db/data.db")
    app.run()


@app.route('/')
def main_page():
    return render_template('main.html')


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
        return redirect('/login')
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
        return render_template('login.html',
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
            accommodation_owner = current_user.id
        )
        db_sess.add(accommodation)
        db_sess.commit()
        photo_path = f'static/images/accommodation_images/{accommodation.id}.jpg'
        with open(photo_path, 'wb') as photo:
            photo.write(form.photo.data.read())
        accommodation.photo_path = photo_path
        db_sess.commit()
        return 'Успешно'
    return render_template('advertisement.html', form=form)


@app.route('/aa')
def ff():
    return render_template('user_profile.html')




if __name__ == '__main__':
    main()