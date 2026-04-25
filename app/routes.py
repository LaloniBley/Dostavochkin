from app import app
from flask import render_template, request, redirect, session, jsonify, flash
from app.models import storage, User, Order
from app.forms import RegistrationForm, LoginForm, OrderForm, ChangeDataForm
from datetime import datetime
import re

RATES = {
    'dohodyaga': 29,
    'busik': 59,
    'skorohod': 129
}

def calculate_price(distance, tariff, promo_code=None):
    price = distance * RATES.get(tariff, 0)
    if promo_code and promo_code.upper() == 'START20':
        price = price * 0.8
    return round(price)

@app.route("/")
@app.route("/main")
def index():
    if 'user_id' in session:
        return render_template("index.html")
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('/profile')
    form = RegistrationForm()
    if form.validate_on_submit():
        if storage.get_user_by_login(form.login.data):
            flash('Пользователь с таким логином уже существует', 'error')
            return render_template("register.html", form=form)
        user = User(
            login=form.login.data,
            password=form.password.data,
            lastname=form.lastname.data,
            firstname=form.firstname.data,
            middlename=form.middlename.data,
            phone=form.phone.data
        )
        storage.add_user(user)
        session['user_id'] = user.id
        session['user_login'] = user.login
        session['is_admin'] = user.is_admin
        flash('Регистрация успешно завершена!', 'success')
        return redirect('/profile')
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/profile')
    form = LoginForm()
    if form.validate_on_submit():
        user = storage.get_user_by_login(form.login.data)
        if user and user.password == form.password.data:
            session['user_id'] = user.id
            session['user_login'] = user.login
            session['is_admin'] = user.is_admin
            flash('Добро пожаловать!', 'success')
            return redirect('/profile')
        else:
            flash('Неверный логин или пароль', 'error')
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect('/')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    user = storage.get_user_by_id(session['user_id'])
    orders = storage.get_orders_by_user(session['user_id'])
    active_orders = [order for order in orders if order.status == 'active']
    active_orders_count = len(active_orders)
    return render_template("profile.html", user=user, orders=orders, active_orders_count=active_orders_count)

@app.route('/change-data', methods=['GET', 'POST'])
def change_data():
    if 'user_id' not in session:
        return redirect('/login')
    user = storage.get_user_by_id(session['user_id'])
    form = ChangeDataForm()
    if request.method == 'POST':
        updates = {}
        has_changes = False
        if form.lastname.data and form.lastname.data != user.lastname:
            updates['lastname'] = form.lastname.data
            has_changes = True
        elif form.lastname.data is not None and form.lastname.data == '':
            flash('Фамилия не может быть пустой', 'error')
            return render_template("change-data.html", form=form, user=user)
        if form.firstname.data and form.firstname.data != user.firstname:
            updates['firstname'] = form.firstname.data
            has_changes = True
        elif form.firstname.data is not None and form.firstname.data == '':
            flash('Имя не может быть пустым', 'error')
            return render_template("change-data.html", form=form, user=user)
        if form.middlename.data is not None and form.middlename.data != user.middlename:
            updates['middlename'] = form.middlename.data if form.middlename.data else ''
            has_changes = True
        if form.phone.data and form.phone.data != user.phone:
            updates['phone'] = form.phone.data
            has_changes = True
        elif form.phone.data is not None and form.phone.data == '':
            flash('Телефон не может быть пустым', 'error')
            return render_template("change-data.html", form=form, user=user)
        if form.login.data and form.login.data != user.login:
            if storage.get_user_by_login(form.login.data):
                flash('Пользователь с таким логином уже существует', 'error')
                return render_template("change-data.html", form=form, user=user)
            updates['login'] = form.login.data
            session['user_login'] = form.login.data
            has_changes = True
        elif form.login.data is not None and form.login.data == '':
            flash('Логин не может быть пустым', 'error')
            return render_template("change-data.html", form=form, user=user)
        if form.password.data:
            updates['password'] = form.password.data
            has_changes = True
        if has_changes:
            storage.update_user(user.id, **updates)
            flash('Данные успешно обновлены!', 'success')
            return redirect('/profile')
    form.lastname.data = user.lastname
    form.firstname.data = user.firstname
    form.middlename.data = user.middlename if user.middlename else ''
    form.phone.data = user.phone
    form.login.data = user.login
    return render_template("change-data.html", form=form, user=user)

@app.route('/order', methods=['GET', 'POST'])
def orders():
    if 'user_id' not in session:
        return redirect('/login')
    form = OrderForm()
    if form.validate_on_submit():
        weight = float(request.form.get('weight', 0)) if request.form.get('weight') else 0
        if form.tariff.data == 'dohodyaga' and (weight < 5 or weight > 10):
            flash('Тариф "Доходяга" доступен для веса от 5 до 10 кг', 'error')
            return render_template("order.html", form=form)

        if form.tariff.data == 'busik' and weight > 200:
            flash('Тариф "Бусик" доступен для веса до 200 кг', 'error')
            return render_template("order.html", form=form)
        order_id = storage.generate_unique_order_id()
        price = calculate_price(form.distance.data, form.tariff.data, form.promo_code.data)
        order = Order(
            user_id=session['user_id'],
            order_id=order_id,
            pickup_address=form.pickup_address.data,
            delivery_address=form.delivery_address.data,
            courier_date=form.courier_date.data.strftime('%Y-%m-%d'),
            recipient_phone=form.recipient_phone.data,
            distance=form.distance.data,
            tariff=form.tariff.data,
            promo_code=form.promo_code.data,
            price=price
        )
        storage.add_order(order)
        flash(f'Заказ #{order_id} успешно создан! Сумма: {price} ₽', 'success')
        return redirect('/profile')
    return render_template("order.html", form=form)

@app.route('/order-management', methods=['GET', 'POST'])
def order_management():
    if 'user_id' not in session:
        return redirect('/login')
    order = None
    if request.method == 'POST':
        order_number = request.form.get('order_number')
        order = storage.get_order_by_number(order_number)
        if not order:
            flash('Заказ с таким номером не найден', 'error')
    return render_template("order-management.html", order=order)

@app.route('/api/find-order/<order_number>', methods=['GET'])
def api_find_order(order_number):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Не авторизован'}), 401
    order = storage.get_order_by_number(order_number)
    if not order:
        return jsonify({'success': False, 'message': 'Заказ не найден'}), 404
    if order.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'У вас нет доступа к этому заказу'}), 403
    return jsonify({
        'success': True,
        'order': {
            'id': order.id,
            'order_id': order.order_id,
            'pickup_address': order.pickup_address,
            'delivery_address': order.delivery_address,
            'courier_date': order.courier_date,
            'recipient_phone': order.recipient_phone,
            'distance': order.distance,
            'tariff': order.tariff,
            'price': order.price,
            'status': order.status
        }
    }), 200

@app.route('/update-order/<order_id>', methods=['POST'])
def update_order(order_id):
    if 'user_id' not in session:
        flash('Не авторизован', 'error')
        return redirect('/login')
    order = None
    for o in storage.orders:
        if o.id == order_id:
            order = o
            break
    if not order:
        flash('Заказ не найден', 'error')
        return redirect('/order-management')
    if order.user_id != session['user_id'] and not session.get('is_admin', False):
        flash('Нет доступа к этому заказу', 'error')
        return redirect('/profile')
    action = request.form.get('action')
    if action == 'cancel':
        if order.status == 'active':
            storage.update_order(order.id, status='cancelled')
            flash(f'Заказ #{order.order_id} отменён', 'success')
        else:
            flash('Заказ нельзя отменить', 'error')
    elif action == 'update':
        pickup_address = request.form.get('pickup_address', '').strip()
        delivery_address = request.form.get('delivery_address', '').strip()
        recipient_phone = request.form.get('recipient_phone', '').strip()
        distance_str = request.form.get('distance', '')
        tariff = request.form.get('tariff', '')
        courier_date = request.form.get('courier_date', '')
        errors = []
        if not pickup_address or len(pickup_address) < 5:
            errors.append('Адрес отправления должен быть не менее 5 символов')
        if not delivery_address or len(delivery_address) < 5:
            errors.append('Адрес доставки должен быть не менее 5 символов')
        phone_pattern = r'^(\+7|8)[0-9]{10}$'
        if not re.match(phone_pattern, recipient_phone):
            errors.append('Введите корректный номер телефона')
        try:
            distance = float(distance_str)
            if distance <= 0 or distance > 70:
                errors.append('Расстояние должно быть от 0.001 до 70 км')
        except ValueError:
            errors.append('Введите корректное расстояние')
        if tariff not in ['dohodyaga', 'busik', 'skorohod']:
            errors.append('Выберите корректный тариф')
        try:
            courier_date_obj = datetime.strptime(courier_date, '%Y-%m-%d').date()
            if courier_date_obj < datetime.now().date():
                errors.append('Дата не может быть в прошлом')
        except ValueError:
            errors.append('Введите корректную дату')
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect('/order-management')
        updates = {
            'pickup_address': pickup_address,
            'delivery_address': delivery_address,
            'courier_date': courier_date,
            'recipient_phone': recipient_phone,
            'distance': distance,
            'tariff': tariff
        }
        price = calculate_price(distance, tariff, order.promo_code)
        updates['price'] = price
        storage.update_order(order.id, **updates)
        flash(f'Заказ #{order.order_id} обновлён. Новая сумма: {price} ₽', 'success')
    return redirect('/order-management')

@app.route('/calculator')
def calculator():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template("calculator.html")

@app.route('/api/users', methods=['GET'])
def api_get_users():
    users_data = []
    for user in storage.users:
        users_data.append({
            'id': user.id,
            'login': user.login,
            'lastname': user.lastname,
            'firstname': user.firstname,
            'middlename': user.middlename,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'created_at': user.created_at
        })
    return jsonify({'success': True, 'users': users_data}), 200

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    user = storage.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'login': user.login,
            'lastname': user.lastname,
            'firstname': user.firstname,
            'middlename': user.middlename,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'created_at': user.created_at
        }
    }), 200

@app.route('/api/users', methods=['POST'])
def api_create_user():
    data = request.json
    required_fields = ['login', 'password', 'lastname', 'firstname', 'phone']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Поле {field} обязательно'}), 400
    if storage.get_user_by_login(data['login']):
        return jsonify({'success': False, 'error': 'Пользователь с таким логином уже существует'}), 409
    user = User(
        login=data['login'],
        password=data['password'],
        lastname=data['lastname'],
        firstname=data['firstname'],
        middlename=data.get('middlename', ''),
        phone=data['phone']
    )
    if data.get('is_admin'):
        user.is_admin = True
    storage.add_user(user)
    return jsonify({
        'success': True,
        'message': 'Пользователь создан',
        'user': {
            'id': user.id,
            'login': user.login
        }
    }), 201

@app.route('/api/users/<user_id>', methods=['PUT'])
def api_update_user_full(user_id):
    user = storage.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404
    data = request.json
    required_fields = ['login', 'lastname', 'firstname', 'phone']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Поле {field} обязательно'}), 400
    if data['login'] != user.login and storage.get_user_by_login(data['login']):
        return jsonify({'success': False, 'error': 'Пользователь с таким логином уже существует'}), 409
    updates = {
        'login': data['login'],
        'lastname': data['lastname'],
        'firstname': data['firstname'],
        'middlename': data.get('middlename', ''),
        'phone': data['phone']
    }
    if data.get('password'):
        updates['password'] = data['password']
    if 'is_admin' in data:
        updates['is_admin'] = data['is_admin']
    storage.update_user(user_id, **updates)
    return jsonify({'success': True, 'message': 'Пользователь полностью обновлён'}), 200

@app.route('/api/users/<user_id>', methods=['PATCH'])
def api_patch_user(user_id):
    user = storage.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404
    data = request.json
    updates = {}
    if 'login' in data and data['login'] != user.login:
        if storage.get_user_by_login(data['login']):
            return jsonify({'success': False, 'error': 'Пользователь с таким логином уже существует'}), 409
        updates['login'] = data['login']
    if 'lastname' in data:
        updates['lastname'] = data['lastname']
    if 'firstname' in data:
        updates['firstname'] = data['firstname']
    if 'middlename' in data:
        updates['middlename'] = data['middlename']
    if 'phone' in data:
        updates['phone'] = data['phone']
    if 'password' in data and data['password']:
        updates['password'] = data['password']
    if 'is_admin' in data:
        updates['is_admin'] = data['is_admin']
    if updates:
        storage.update_user(user_id, **updates)
        return jsonify({'success': True, 'message': 'Пользователь частично обновлён'}), 200

    return jsonify({'success': True, 'message': 'Нет изменений'}), 200

@app.route('/api/users/<user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    user = storage.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404

    storage.delete_user(user_id)
    return jsonify({'success': True, 'message': 'Пользователь удалён'}), 200

@app.route('/api/orders', methods=['GET'])
def api_get_orders():
    orders_data = []
    for order in storage.orders:
        user = storage.get_user_by_id(order.user_id)
        orders_data.append({
            'id': order.id,
            'order_id': order.order_id,
            'user_id': order.user_id,
            'user_name': f"{user.lastname} {user.firstname}" if user else "Неизвестный",
            'pickup_address': order.pickup_address,
            'delivery_address': order.delivery_address,
            'courier_date': order.courier_date,
            'recipient_phone': order.recipient_phone,
            'distance': order.distance,
            'tariff': order.tariff,
            'promo_code': order.promo_code,
            'price': order.price,
            'status': order.status,
            'created_at': order.created_at
        })
    return jsonify({'success': True, 'orders': orders_data}), 200

@app.route('/api/orders/<order_id>', methods=['GET'])
def api_get_order(order_id):
    order = None
    for o in storage.orders:
        if o.id == order_id or o.order_id == order_id:
            order = o
            break
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404
    user = storage.get_user_by_id(order.user_id)
    return jsonify({
        'success': True,
        'order': {
            'id': order.id,
            'order_id': order.order_id,
            'user_id': order.user_id,
            'user_name': f"{user.lastname} {user.firstname}" if user else "Неизвестный",
            'pickup_address': order.pickup_address,
            'delivery_address': order.delivery_address,
            'courier_date': order.courier_date,
            'recipient_phone': order.recipient_phone,
            'distance': order.distance,
            'tariff': order.tariff,
            'promo_code': order.promo_code,
            'price': order.price,
            'status': order.status,
            'created_at': order.created_at
        }
    }), 200

@app.route('/api/users/<user_id>/orders', methods=['GET'])
def api_get_user_orders(user_id):
    user = storage.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404
    orders = storage.get_orders_by_user(user_id)
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'order_id': order.order_id,
            'pickup_address': order.pickup_address,
            'delivery_address': order.delivery_address,
            'courier_date': order.courier_date,
            'distance': order.distance,
            'tariff': order.tariff,
            'price': order.price,
            'status': order.status,
            'created_at': order.created_at
        })

    return jsonify({'success': True, 'orders': orders_data}), 200

@app.route('/api/orders', methods=['POST'])
def api_create_order():
    data = request.json
    required_fields = ['user_id', 'pickup_address', 'delivery_address', 'courier_date',
                       'recipient_phone', 'distance', 'tariff']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Поле {field} обязательно'}), 400
    user = storage.get_user_by_id(data['user_id'])
    if not user:
        return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404
    weight = float(data.get('weight', 0))
    tariff = data['tariff']
    if tariff == 'dohodyaga' and (weight < 5 or weight > 10):
        return jsonify({'success': False, 'error': 'Тариф "Доходяга" доступен для веса от 5 до 10 кг'}), 400
    if tariff == 'busik' and weight > 200:
        return jsonify({'success': False, 'error': 'Тариф "Бусик" доступен для веса до 200 кг'}), 400

    order_id = storage.generate_unique_order_id()
    price = calculate_price(data['distance'], tariff, data.get('promo_code'))
    order = Order(
        user_id=data['user_id'],
        order_id=order_id,
        pickup_address=data['pickup_address'],
        delivery_address=data['delivery_address'],
        courier_date=data['courier_date'],
        recipient_phone=data['recipient_phone'],
        distance=data['distance'],
        tariff=tariff,
        promo_code=data.get('promo_code'),
        price=price
    )
    storage.add_order(order)
    return jsonify({
        'success': True,
        'message': 'Заказ создан',
        'order': {
            'id': order.id,
            'order_id': order.order_id,
            'price': price
        }
    }), 201

@app.route('/api/orders/<order_id>', methods=['PUT'])
def api_update_order_full(order_id):
    order = None
    for o in storage.orders:
        if o.id == order_id or o.order_id == order_id:
            order = o
            break
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404
    data = request.json
    required_fields = ['pickup_address', 'delivery_address', 'courier_date',
                       'recipient_phone', 'distance', 'tariff']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Поле {field} обязательно'}), 400
    weight = float(data.get('weight', 0))
    tariff = data['tariff']
    if tariff == 'dohodyaga' and (weight < 5 or weight > 10):
        return jsonify({'success': False, 'error': 'Тариф "Доходяга" доступен для веса от 5 до 10 кг'}), 400
    if tariff == 'busik' and weight > 200:
        return jsonify({'success': False, 'error': 'Тариф "Бусик" доступен для веса до 200 кг'}), 400
    price = calculate_price(data['distance'], tariff, order.promo_code)
    updates = {
        'pickup_address': data['pickup_address'],
        'delivery_address': data['delivery_address'],
        'courier_date': data['courier_date'],
        'recipient_phone': data['recipient_phone'],
        'distance': data['distance'],
        'tariff': tariff,
        'price': price
    }
    if 'status' in data:
        updates['status'] = data['status']
    storage.update_order(order.id, **updates)
    return jsonify({'success': True, 'message': 'Заказ полностью обновлён', 'price': price}), 200

@app.route('/api/orders/<order_id>', methods=['PATCH'])
def api_patch_order(order_id):
    order = None
    for o in storage.orders:
        if o.id == order_id or o.order_id == order_id:
            order = o
            break
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404
    data = request.json
    updates = {}
    if 'pickup_address' in data:
        updates['pickup_address'] = data['pickup_address']
    if 'delivery_address' in data:
        updates['delivery_address'] = data['delivery_address']
    if 'courier_date' in data:
        updates['courier_date'] = data['courier_date']
    if 'recipient_phone' in data:
        updates['recipient_phone'] = data['recipient_phone']
    if 'distance' in data:
        updates['distance'] = data['distance']
    if 'tariff' in data:
        updates['tariff'] = data['tariff']
    if 'status' in data:
        updates['status'] = data['status']
    if 'distance' in updates or 'tariff' in updates:
        distance = updates.get('distance', order.distance)
        tariff = updates.get('tariff', order.tariff)
        updates['price'] = calculate_price(distance, tariff, order.promo_code)
    if updates:
        storage.update_order(order.id, **updates)
        return jsonify({'success': True, 'message': 'Заказ частично обновлён'}), 200
    return jsonify({'success': True, 'message': 'Нет изменений'}), 200

@app.route('/api/orders/<order_id>', methods=['DELETE'])
def api_delete_order(order_id):
    order = None
    for o in storage.orders:
        if o.id == order_id or o.order_id == order_id:
            order = o
            break
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404
    storage.delete_order(order.id)
    return jsonify({'success': True, 'message': 'Заказ удалён'}), 200

@app.route('/api/orders/<order_id>/status', methods=['PATCH'])
def api_update_order_status(order_id):
    order = None
    for o in storage.orders:
        if o.id == order_id or o.order_id == order_id:
            order = o
            break
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404
    data = request.json
    new_status = data.get('status')

    if new_status not in ['active', 'delivered', 'cancelled']:
        return jsonify({'success': False, 'error': 'Некорректный статус'}), 400
    storage.update_order(order.id, status=new_status)
    return jsonify({'success': True, 'message': f'Статус заказа изменён на {new_status}'}), 200

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    total_users = len(storage.users)
    total_orders = len(storage.orders)
    active_orders = len([o for o in storage.orders if o.status == 'active'])
    delivered_orders = len([o for o in storage.orders if o.status == 'delivered'])
    cancelled_orders = len([o for o in storage.orders if o.status == 'cancelled'])
    total_revenue = sum([o.price for o in storage.orders if o.status == 'delivered'])
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'total_orders': total_orders,
            'active_orders': active_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'success': True,
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/admin/users')
def admin_users():
    users_data = []
    for user in storage.users:
        users_data.append({
            'id': user.id,
            'login': user.login,
            'lastname': user.lastname,
            'firstname': user.firstname,
            'middlename': user.middlename,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'created_at': user.created_at
        })
    return jsonify({'users': users_data})

@app.route('/admin/orders')
def admin_orders():
    orders_data = []
    for order in storage.orders:
        user = storage.get_user_by_id(order.user_id)
        orders_data.append({
            'id': order.id,
            'order_id': order.order_id,
            'user_name': f"{user.lastname} {user.firstname}" if user else "Неизвестный",
            'user_login': user.login if user else "unknown",
            'pickup_address': order.pickup_address,
            'delivery_address': order.delivery_address,
            'distance': order.distance,
            'tariff': order.tariff,
            'price': order.price,
            'status': order.status,
            'created_at': order.created_at
        })
    return jsonify({'orders': orders_data})

@app.route('/admin/delete_user/<user_id>', methods=['POST'])
def admin_delete_user(user_id):
    storage.delete_user(user_id)
    return jsonify({'success': True})

@app.route('/admin/update_user/<user_id>', methods=['POST'])
def admin_update_user(user_id):
    data = request.json
    updates = {}
    if 'lastname' in data:
        updates['lastname'] = data['lastname']
    if 'firstname' in data:
        updates['firstname'] = data['firstname']
    if 'middlename' in data:
        updates['middlename'] = data['middlename']
    if 'phone' in data:
        updates['phone'] = data['phone']
    if 'login' in data:
        existing = storage.get_user_by_login(data['login'])
        if existing and existing.id != user_id:
            return jsonify({'error': 'Логин уже занят'}), 400
        updates['login'] = data['login']
    storage.update_user(user_id, **updates)
    return jsonify({'success': True})

@app.route('/admin/delete_order/<order_id>', methods=['POST'])
def admin_delete_order(order_id):
    storage.delete_order(order_id)
    return jsonify({'success': True})

@app.route('/admin/update_order/<order_id>', methods=['POST'])
def admin_update_order(order_id):
    data = request.json
    updates = {}
    if 'status' in data:
        updates['status'] = data['status']
    if 'price' in data:
        updates['price'] = float(data['price'])
    storage.update_order(order_id, **updates)
    return jsonify({'success': True})

@app.route('/admin/set_data_file', methods=['POST'])
def admin_set_data_file():
    filename = request.json.get('filename', 'data.dat')
    storage.set_filename(filename)
    return jsonify({'success': True, 'filename': filename})

@app.route('/admin/load_data', methods=['POST'])
def admin_load_data():
    storage.load()
    return jsonify({'success': True, 'users_count': len(storage.users), 'orders_count': len(storage.orders)})