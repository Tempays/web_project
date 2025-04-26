from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = 'special_secret_key_kyoma'


def main():
    app.run()


@app.route('/')
def main_page():
    return 'ЭТО ВЫБОР ВРАТ ШТЕЙНА'


if __name__ == '__main__':
    main()