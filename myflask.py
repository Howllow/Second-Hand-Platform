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
db = pymysql.connect(**myconfig)


@app.route('/')
def homepage():
    return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        data = request.get_json()
        log_message = login_user(data, db)

        if log_message['response_code'] == 0:
            usr = user.User()
            usr.username = data['username']
            usr.id = data['username']
            fl.login_user(usr)
            flash('Login Success')

        return json.dumps(log_message)


@app.route('/register', methods=['POST', 'GET'])
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

        reg_message = register_user(data, db)

        return json.dumps(reg_message)


@app.route('/setting', methods=['POST'])
@fl.login_required
def setting():
    if request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        if data['type'] == "gender":
            if data['content'] == 'F':
                data['content'] = 1
            else:
                data['content'] = 0
        setting_message = change_setting(data, db)
        return json.dumps(setting_message)


@app.route('/buyer/home', methods=['POST', 'GET'])
@fl.login_required
def buyer_home():
    if request.method == 'GET':
        return render_template('buyer_home.html')


@app.route('/buyer/goods', methods=['POST', 'GET'])
@fl.login_required
def buyer_goods():
    if request.method == 'GET':
        return render_template('buyer_goods.html')

    elif request.method == 'POST':
        data = request.get_json()
        good_message = find_goods(data, db)

        return json.dumps(good_message)


@app.route('/buyer/cart', methods=['POST', 'GET'])
@fl.login_required
def buyer_cart():
    if request.method == 'GET':
        return render_template('buyer_car.html')

    elif request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        cart_message = find_cart(data, db)
        return json.dumps(cart_message)


@app.route('/buyer/add', methods=['POST'])
@fl.login_required
def buyer_add():
    if request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        add_message = add_cart(data, db)
        return json.dumps(add_message)


@app.route('/buyer/buy', methods=['POST'])
@fl.login_required
def buyer_buy():
    if request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        buy_message = buy_good(data, db)
        return json.dumps(buy_message)


@app.route('/buyer/remove', methods=['POST'])
@fl.login_required
def buyer_remove():
    if request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        remove_message = remove_cart(data, db)
        return json.dumps(remove_message)


@app.route('/buyer/return', methods=['POST'])
@fl.login_required
def buyer_return():
    if request.method == 'POST':
        data = request.get_json()
        return_message = good_return(data, db)
        return json.dumps(return_message)


@app.route('/buyer/comment', methods=['POST'])
@fl.login_required
def buyer_comment():
    data = request.get_json()
    return json.dumps(good_comment(data, db))


@app.route('/buyer/goodinfo', methods=['POST', 'GET'])
@fl.login_required
def good_info():
    if request.method == 'GET':
        return render_template('buyer_goodinfo.html')

    elif request.method == 'POST':
        data = request.get_json()
        info_message = find_info(data, db)

        return json.dumps(info_message)


@app.route('/buyer/bought', methods=['POST', 'GET'])
@fl.login_required
def bought():
    if request.method == 'GET':
        return render_template('buyer_bought.html')

    elif request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        bought_message = find_bought(data, db)

        return json.dumps(bought_message)


@app.route('/buyer/setting', methods=['GET'])
@fl.login_required
def buyer_setting():
    return render_template('buyer_setting.html')


@app.route('/user/logout', methods=['POST', 'GET'])
@fl.login_required
def logout():
    fl.logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    return user.UserManager.get(user_id)


if __name__ == '__main__':
    app.run(host='localhost', port='5000')

