import pickle
import os
import uuid
from datetime import datetime

class User:
    def __init__(self, login, password, lastname, firstname, middlename, phone):
        self.id = str(uuid.uuid4())
        self.login = login
        self.password = password  # В реальном проекте хэшировать, но по заданию пока так
        self.lastname = lastname
        self.firstname = firstname
        self.middlename = middlename
        self.phone = phone
        self.is_admin = False
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            'id': self.id,
            'login': self.login,
            'lastname': self.lastname,
            'firstname': self.firstname,
            'middlename': self.middlename,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }

class Order:
    def __init__(self, user_id, order_id, pickup_address, delivery_address, courier_date, recipient_phone, distance,
                 tariff, promo_code, price):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.order_id = order_id
        self.pickup_address = pickup_address
        self.delivery_address = delivery_address
        self.courier_date = courier_date
        self.recipient_phone = recipient_phone
        self.distance = distance
        self.tariff = tariff
        self.promo_code = promo_code
        self.price = price
        self.status = 'active'  # active, delivered, cancelled
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'pickup_address': self.pickup_address,
            'delivery_address': self.delivery_address,
            'courier_date': self.courier_date,
            'recipient_phone': self.recipient_phone,
            'distance': self.distance,
            'tariff': self.tariff,
            'promo_code': self.promo_code,
            'price': self.price,
            'status': self.status,
            'created_at': self.created_at
        }

class DataStorage:
    def __init__(self, filename='data.dat'):
        self.filename = filename
        self.users = []
        self.orders = []
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as f:
                    data = pickle.load(f)
                    self.users = data.get('users', [])
                    self.orders = data.get('orders', [])
            except:
                self.users = []
                self.orders = []

    def save(self):
        with open(self.filename, 'wb') as f:
            pickle.dump({'users': self.users, 'orders': self.orders}, f)

    def set_filename(self, filename):
        self.filename = filename
        self.load()

    def get_user_by_login(self, login):
        for user in self.users:
            if user.login == login:
                return user
        return None

    def get_user_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def get_orders_by_user(self, user_id):
        return [order for order in self.orders if order.user_id == user_id]

    def get_order_by_number(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def generate_unique_order_id(self):
        existing_ids = [order.order_id for order in self.orders]
        while True:
            import random
            order_id = f"ORD-{random.randint(1000, 9999)}"
            if order_id not in existing_ids:
                return order_id

    def add_user(self, user):
        self.users.append(user)
        self.save()

    def update_user(self, user_id, **kwargs):
        for user in self.users:
            if user.id == user_id:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                self.save()
                return True
        return False

    def delete_user(self, user_id):
        self.orders = [order for order in self.orders if order.user_id != user_id]
        self.users = [user for user in self.users if user.id != user_id]
        self.save()

    def add_order(self, order):
        self.orders.append(order)
        self.save()

    def update_order(self, order_id, **kwargs):
        for order in self.orders:
            if order.id == order_id:
                for key, value in kwargs.items():
                    if hasattr(order, key):
                        setattr(order, key, value)
                self.save()
                return True
        return False

    def delete_order(self, order_id):
        self.orders = [order for order in self.orders if order.id != order_id]
        self.save()

    def get_all_users_with_orders(self):
        result = []
        for user in self.users:
            user_orders = self.get_orders_by_user(user.id)
            result.append({
                'user': user,
                'orders': user_orders
            })
        return result

storage = DataStorage()

if not storage.users:
    admin = User('laloni', '382401Ni', 'Администратор', 'Системы', '', '+70000000000')
    admin.is_admin = True
    storage.add_user(admin)