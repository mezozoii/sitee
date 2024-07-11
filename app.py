from flask import Flask, render_template, request, redirect, url_for, flash, session
# Импорт необходимых модулей из Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)  # Создание экземпляра Flask
app.config['SECRET_KEY'] = 'your_secret_key'  # Настройка секретного ключа для сессий
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Настройка URI базы данных
db = SQLAlchemy(app)  # Создание экземпляра SQLAlchemy


# Определение модели пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Идентификатор пользователя
    username = db.Column(db.String(150), nullable=False, unique=True)  # Имя пользователя
    password = db.Column(db.String(150), nullable=False)  # Хэшированный пароль


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')  # Отображение шаблона главной страницы


# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':  # Если метод POST, обработка данных формы
        username = request.form['username']  # Получение имени пользователя из формы
        password = request.form['password']  # Получение пароля из формы

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Хэширование пароля

        new_user = User(username=username, password=hashed_password)  # Создание нового пользователя

        try:
            db.session.add(new_user)  # Добавление пользователя в сессию
            db.session.commit()  # Сохранение изменений в базе данных
            return redirect(url_for('login'))  # Перенаправление на страницу входа
        except:
            return 'There was an issue adding your task'  # Сообщение об ошибке

    return render_template('register.html')  # Отображение шаблона регистрации


# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Если метод POST, обработка данных формы
        username = request.form['username']  # Получение имени пользователя из формы
        password = request.form['password']  # Получение пароля из формы

        user = User.query.filter_by(username=username).first()  # Поиск пользователя в базе данных

        if user and check_password_hash(user.password, password):  # Проверка пароля
            session['user_id'] = user.id  # Сохранение идентификатора пользователя в сессии
            return redirect(url_for('profile'))  # Перенаправление на страницу профиля
        else:
            flash('Invalid username or password', 'error')  # Сообщение об ошибке

    return render_template('login.html')  # Отображение шаблона входа


# Страница профиля
@app.route('/profile')
def profile():
    if 'user_id' not in session:  # Проверка, авторизован ли пользователь
        return redirect(url_for('login'))  # Перенаправление на страницу входа

    user = User.query.filter_by(id=session['user_id']).first()  # Получение текущего пользователя из базы данных
    return f"Hello, {user.username}!"  # Отображение приветствия с именем пользователя


if __name__ == '__main__':
    with app.app_context():  # Создание контекста приложения
        db.create_all()  # Создание всех таблиц в базе данных
    app.run(debug=True)  # Запуск приложения в режиме отладки
