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


@app.route('/seller/home', methods=['GET'])
@fl.login_required
def seller_home():
    return render_template('seller_home.html')


@app.route('/seller/sell', methods=['POST', 'GET'])
@fl.login_required
def seller_sell():
    if request.method == 'GET':
        return render_template('seller_sell.html')

    elif request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        return json.dumps(sell_good(data, db))


@app.route('/seller/selling', methods=['POST', 'GET'])
@fl.login_required
def seller_selling():
    if request.method == 'GET':
        return render_template('seller_selling.html')

    elif request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        return json.dumps(selling_good(data, db))


@app.route('/seller/goodinfo', methods=['POST', 'GET'])
@fl.login_required
def seller_goodinfo():
    if request.method == 'GET':
        return render_template('seller_goodinfo.html')

    elif request.method == 'POST':
        data = request.get_json()
        info_message = find_info(data, db)

        return json.dumps(info_message)


@app.route('/seller/change', methods=['POST'])
@fl.login_required
def seller_change():
    data = request.get_json()
    return json.dumps(change_good(data, db))


@app.route('/seller/setting', methods=['GET'])
@fl.login_required
def seller_setting():
    return render_template('seller_setting.html')


@app.route('/seller/sold', methods=['GET', 'POST'])
@fl.login_required
def seller_sold():
    if request.method == 'GET':
        return render_template('seller_sold.html')

    elif request.method == 'POST':
        data = request.get_json()
        data['username'] = fl.current_user.username
        return json.dumps(sold_good(data, db))


@app.route('/admin/home', methods=['GET'])
@fl.login_required
def admin_home():
    return render_template('admin_home.html')


@app.route('/admin/request', methods=['GET', 'POST'])
@fl.login_required
def admin_request():
    if request.method == 'GET':
        return render_template('admin_request.html')

    elif request.method == 'POST':
        return json.dumps(get_request(db))


@app.route('/admin/manage', methods=['POST'])
@fl.login_required
def admin_agree():
    data = request.get_json()
    return json.dumps(req_manage(data, db))


@app.route('/admin/orders', methods=['GET', 'POST'])
@fl.login_required
def admin_orders():
    if request.method == 'GET':
        return render_template('admin_orders.html')

    elif request.method == 'POST':
        return json.dumps(get_orders(db))


@app.route('/admin/setting', methods=['GET', 'POST'])
@fl.login_required
def admin_setting():
    if request.method == 'GET':
        return render_template('admin_setting.html')


@app.route('/admin/goods', methods=['GET'])
@fl.login_required
def admin_goods():
    return render_template('admin_goods.html')


@app.route('/admin/goodinfo', methods=['GET'])
@fl.login_required
def admin_goodinfo():
    return render_template('admin_goodinfo.html')


@app.route('/admin/special', methods=['GET'])
@fl.login_required
def admin_special():
    return render_template('admin_special.html')


@app.route('/admin/manageusr', methods=['GET', 'POST'])
@fl.login_required
def admin_manageusr():
    if request.method == 'GET':
        return render_template('admin_manage.html')

    elif request.method == 'POST':
        return json.dumps(manage_usr(db))


@app.route('/cancel', methods=['POST'])
@fl.login_required
def seller_cancel():
    data = request.get_json()
    return json.dumps(cancel_good(data, db))


@app.route('/admin/delete', methods=['POST'])
@fl.login_required
def admin_delete():
    data = request.get_json()
    return json.dumps(delete_usr(data, db))


@app.route('/tuhao', methods=['POST'])
@fl.login_required
def special_tuhao():
    return json.dumps(tuhao_buyer(db))


@app.route('/similar', methods=['POST'])
@fl.login_required
def special_similar():
    data = request.get_json()
    return json.dumps(similar_buyer(data, db))


@app.route('/audience', methods=['POST'])
@fl.login_required
def special_audience():
    return json.dumps(get_audience(db))


@app.route('/hot', methods=['POST'])
@fl.login_required
def special_hot():
    return json.dumps(get_hot(db))


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

