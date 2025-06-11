
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def load_data():
    with open('data_absolwenci.json', encoding='utf-8') as f:
        return pd.DataFrame(json.load(f))


df = load_data()

# @app.route('/')
# @login_required
# def index():
#     search = request.args.get('search', '').lower()
#     sort_by = request.args.get('sort_by', 'Region')
#     top_only = request.args.get('top5', 'false') == 'true'

#     filtered_df = df.copy()

#     if search:
#         filtered_df = filtered_df[
#             filtered_df['Region'].str.lower().str.contains(search) |
#             filtered_df['Typ szkoły'].str.lower().str.contains(search)
#         ]

#     if sort_by in filtered_df.columns:
#         filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_by == 'Region'))

#     if top_only:
#         filtered_df = filtered_df.head(5)

#     avg_abs = round(filtered_df["Absolwenci"].mean(), 2)
#     data = filtered_df.to_dict(orient='records')

#     return render_template('index.html', data=data, avg_abs=avg_abs, search=search, sort_by=sort_by, top_only=top_only)

@app.route('/')
@login_required
def index():
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort_by', 'Region')
    top_only = request.args.get('top5', 'false') == 'true'
    filter_type = request.args.get('filter_type', '')  # NEW

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df['Region'].str.lower().str.contains(search) |
            filtered_df['Typ szkoły'].str.lower().str.contains(search)
        ]

    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_by == 'Region'))

    if top_only:
        filtered_df = filtered_df.head(5)

    if filter_type == 'max':
        max_value = filtered_df['Absolwenci'].max()
        filtered_df = filtered_df[filtered_df['Absolwenci'] == max_value]
    elif filter_type == 'min':
        min_value = filtered_df['Absolwenci'].min()
        filtered_df = filtered_df[filtered_df['Absolwenci'] == min_value]
    elif filter_type == 'avg':
        avg_val = round(filtered_df['Absolwenci'].mean())
        filtered_df['diff'] = (filtered_df['Absolwenci'] - avg_val).abs()
        filtered_df = filtered_df.sort_values(by='diff').head(1).drop(columns='diff')

    avg_abs = round(filtered_df["Absolwenci"].mean(), 2)
    data = filtered_df.to_dict(orient='records')

    return render_template('index.html', data=data, avg_abs=avg_abs, search=search, sort_by=sort_by, top_only=top_only, filter_type=filter_type)



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

