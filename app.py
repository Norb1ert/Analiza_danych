# from flask import Flask, render_template, request
# import pandas as pd

# app = Flask(__name__)

# # Dane
# data = {
#     "Urząd wojewódzki": [
#         "Mazowiecki UW w Warszawie", "Opolski UW w Opolu", "Warmińsko-Mazurski UW w Olsztynie",
#         "Śląski UW w Katowicach", "Podlaski UW w Białymstoku", "Dolnośląski UW we Wrocławiu",
#         "Wielkopolski UW w Poznaniu", "Małopolski UW w Krakowie", "Podkarpacki UW w Rzeszowie",
#         "Zachodniopomorski UW w Szczecinie", "Kujawsko-pomorski UW w Bydgoszczy",
#         "Lubuski UW w Gorzowie Wlkp.", "Lubelski UW w Lublinie", "Pomorski UW w Gdańsku",
#         "Świętokrzyski UW w Kielcach", "Łódzki UW w Łodzi", "Ogółem"
#     ],
#     "Wynagrodzenie zasadnicze (brutto)": [
#         4587, 4120, 3896, 4299, 4037, 3876, 4228, 4299, 3956, 3913, 4056,
#         3998, 3669, 3967, 3727, 3928, 4091
#     ],
#     "Wynagrodzenie całkowite (brutto)": [
#         6631, 6444, 6420, 6319, 6274, 6230, 6169, 6121, 6074, 5877, 5851,
#         5753, 5715, 5706, 5650, 5514, 6085
#     ]
# }

# # Utwórz DataFrame i przetwórz
# df = pd.DataFrame(data)
# df.columns = df.columns.str.strip().str.replace('\xa0', ' ', regex=False)
# df['Różnica'] = df['Wynagrodzenie całkowite (brutto)'] - df['Wynagrodzenie zasadnicze (brutto)']

# @app.route('/')
# def index():
#     search = request.args.get('search', '').lower()
#     sort_by = request.args.get('sort_by', 'Urząd wojewódzki')
#     top_only = request.args.get('top5', 'false') == 'true'

#     filtered_df = df.copy()

#     # Filtrowanie
#     if search:
#         filtered_df = filtered_df[filtered_df['Urząd wojewódzki'].str.lower().str.contains(search)]

#     # Sortowanie
#     if sort_by in filtered_df.columns:
#         filtered_df = filtered_df.sort_values(by=sort_by, ascending=False if sort_by == 'Różnica' else True)

#     # Top 5
#     if top_only:
#         filtered_df = filtered_df.head(5)

#     # Średnie
#     avg_basic = filtered_df["Wynagrodzenie zasadnicze (brutto)"].mean()
#     avg_total = filtered_df["Wynagrodzenie całkowite (brutto)"].mean()

#     tabela_html = filtered_df.to_html(index=False, classes='table table-striped table-bordered')

#     return render_template(
#         'index.html',
#         tabela=tabela_html,
#         avg_basic=round(avg_basic, 2),
#         avg_total=round(avg_total, 2),
#         search=search,
#         sort_by=sort_by,
#         top_only=top_only
#     )

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Config & DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load Data
def load_data():
    with open('data.json', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f))
        df['Różnica'] = df['Wynagrodzenie całkowite (brutto)'] - df['Wynagrodzenie zasadnicze (brutto)']
        return df

df = load_data()

@app.route('/')
@login_required
def index():
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort_by', 'Urząd wojewódzki')
    top_only = request.args.get('top5', 'false') == 'true'

    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['Urząd wojewódzki'].str.lower().str.contains(search)]
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=False if sort_by == 'Różnica' else True)
    if top_only:
        filtered_df = filtered_df.head(5)

    avg_basic = filtered_df["Wynagrodzenie zasadnicze (brutto)"].mean()
    avg_total = filtered_df["Wynagrodzenie całkowite (brutto)"].mean()
    tabela_html = filtered_df.to_html(index=False, classes='table table-bordered')

    return render_template('index.html', tabela=tabela_html, avg_basic=round(avg_basic, 2), avg_total=round(avg_total, 2))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(email=request.form['email'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

