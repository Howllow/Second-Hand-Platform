from db.dbgmm import *
from db.config import *
from flask import *
import json
import flask_login as fl
import user

app = Flask(__name__)
login_manager = fl.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'please login!'
login_manager.session_protection = 'strong'

app.config['SECRET_KEY'] = 'gimmemoney'

password = ""
db = pymysql.connect(**config)

@app.route('/')
def homepage():
    return redirect(url_for('index'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        data = request.get_json()
        log_message = login_user(data, db)
        res = dict()

        if log_message['state'] == 0:
            usr = user.User()
            usr.username = data['username']
            usr.id = data['username']
            fl.login_user(usr)
            flash('Login Success')
            res['response_code'] = 0
            res['ident'] = log_message['ident']

        else:
            res['response_code'] = log_message['state']

        return json.dumps(res)

@app.route('register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':
        data = request.get_json()
        if data['gender'] == 'M':
            data['gender'] = 0
        else:
            data['gender'] = 1
        if data['ident'] == 'B':
            data['ident'] = 0
        else:
            data['ident'] = 1
        res = dict()
        reg_message = register_user(data, db)
