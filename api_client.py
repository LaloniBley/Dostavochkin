import requests
import json
import os
import re
from datetime import datetime

BASE_URL = "http://127.0.0.1:5002/api"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_success(message):
    print(f"\n✅ {message}")


def print_error(message):
    print(f"\n❌ {message}")


def print_info(message):
    print(f"\nℹ️  {message}")


def print_user(user):
    print(f"\n  🧑‍💼 ПОЛЬЗОВАТЕЛЬ")
    print(f"  {'─' * 40}")
    print(f"  ID:       {user['id']}")
    print(f"  Логин:    {user['login']}")
    print(f"  ФИО:      {user['lastname']} {user['firstname']} {user['middlename']}")
    print(f"  Телефон:  {user['phone']}")
    print(f"  Админ:    {'Да' if user['is_admin'] else 'Нет'}")
    print(f"  Создан:   {user['created_at']}")


def print_users(users):
    if not users:
        print_info("Пользователей не найдено")
        return

    print(f"\n  👥 СПИСОК ПОЛЬЗОВАТЕЛЕЙ")
    print(f"  {'─' * 50}")

    for i, user in enumerate(users, 1):
        fio = f"{user['lastname']} {user['firstname']} {user['middlename']}"
        print(f"\n  {i}. {fio}")
        print(f"     🆔 {user['id']}")
        print(f"     📧 {user['login']}")
        print(f"     📱 {user['phone']}")

    print(f"\n  {'─' * 50}")
    print(f"  📊 Всего пользователей: {len(users)}")


def print_order(order):
    print(f"\n  📦 ЗАКАЗ #{order['order_id']}")
    print(f"  {'─' * 40}")
    print(f"  Клиент:     {order.get('user_name', 'Неизвестный')}")
    print(f"  Откуда:     {order['pickup_address']}")
    print(f"  Куда:       {order['delivery_address']}")
    print(f"  Дата:       {order['courier_date']}")
    print(f"  Телефон:    {order['recipient_phone']}")
    print(f"  Расстояние: {order['distance']} км")
    print(f"  Тариф:      {order['tariff']}")
    print(f"  Цена:       {order['price']} ₽")

    status_icon = "🟢" if order['status'] == 'active' else ("✅" if order['status'] == 'delivered' else "🔴")
    status_text = "Активен" if order['status'] == 'active' else ("Доставлен" if order['status'] == 'delivered' else "Отменён")
    print(f"  Статус:     {status_icon} {status_text}")


def print_orders(orders):
    """Красивый вывод списка заказов"""
    if not orders:
        print_info("Заказов не найдено")
        return

    print(f"\n  📦 СПИСОК ЗАКАЗОВ")
    print(f"  {'─' * 50}")

    for i, order in enumerate(orders, 1):
        status_icon = "🟢" if order['status'] == 'active' else ("✅" if order['status'] == 'delivered' else "🔴")
        print(f"\n  {i}. Заказ #{order['order_id']} {status_icon}")
        print(f"     📍 {order['pickup_address']} → {order['delivery_address']}")
        print(f"     💰 {order['price']} ₽")

    print(f"\n  {'─' * 50}")
    print(f"  📊 Всего заказов: {len(orders)}")


def print_stats(stats):
    """Красивый вывод статистики"""
    print(f"\n  📊 СТАТИСТИКА")
    print(f"  {'─' * 40}")
    print(f"  👥 Пользователей:           {stats['total_users']}")
    print(f"  📦 Всего заказов:           {stats['total_orders']}")
    print(f"  🟢 Активных заказов:        {stats['active_orders']}")
    print(f"  ✅ Доставленных заказов:    {stats['delivered_orders']}")
    print(f"  🔴 Отменённых заказов:      {stats['cancelled_orders']}")
    print(f"  💰 Общая выручка:           {stats['total_revenue']} ₽")


def wait_for_enter():
    input("\n⏎ Нажмите Enter для продолжения...")


def validate_login(login):
    if not login:
        return False, "Логин обязателен для заполнения"
    if len(login) < 4 or len(login) > 16:
        return False, "Логин должен быть от 4 до 16 символов"
    if not re.match(r'^[a-zA-Z0-9]+$', login):
        return False, "Логин должен содержать только латинские буквы и цифры"
    return True, ""


def validate_password(password):
    if not password:
        return False, "Пароль обязателен для заполнения"
    if len(password) < 8 or len(password) > 32:
        return False, "Пароль должен быть от 8 до 32 символов"
    if not re.search(r'[0-9]', password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not re.search(r'[a-z]', password):
        return False, "Пароль должен содержать хотя бы одну строчную латинскую букву"
    if not re.search(r'[A-Z]', password):
        return False, "Пароль должен содержать хотя бы одну заглавную латинскую букву"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Пароль должен содержать хотя бы один спецсимвол"
    return True, ""


def validate_name(name, field_name):
    if not name:
        return False, f"{field_name} обязателен для заполнения"
    if not re.match(r'^[а-яА-Яa-zA-Z]+$', name):
        return False, f"{field_name} должен содержать только буквы"
    if len(name) < 2:
        return False, f"{field_name} должен быть не короче 2 символов"
    return True, ""


def validate_phone(phone):
    if not phone:
        return False, "Телефон обязателен для заполнения"
    if not re.match(r'^(\+7|8)[0-9]{10}$', phone):
        return False, "Введите корректный номер телефона (например: +78005553535 или 88005553535)"
    return True, ""


def validate_address(address, field_name):
    if not address:
        return False, f"{field_name} обязателен для заполнения"
    if len(address) < 5:
        return False, f"{field_name} должен быть не менее 5 символов"
    return True, ""


def validate_distance(distance):
    try:
        distance = float(distance)
        if distance <= 0:
            return False, "Расстояние должно быть больше 0 км"
        if distance > 70:
            return False, "Расстояние не может превышать 70 км"
        return True, distance
    except ValueError:
        return False, "Введите корректное расстояние"


def validate_weight(weight, tariff):
    try:
        weight = float(weight)
        if weight < 0:
            return False, "Вес не может быть отрицательным"

        if tariff == 'dohodyaga':
            if weight < 5:
                return False, "Тариф 'Доходяга' доступен для веса от 5 кг"
            if weight > 10:
                return False, "Тариф 'Доходяга' доступен для веса до 10 кг"
        elif tariff == 'busik' and weight > 200:
            return False, "Тариф 'Бусик' доступен для веса до 200 кг"

        return True, weight
    except ValueError:
        return False, "Введите корректный вес"


def validate_date(date_str):
    if not date_str:
        return False, "Дата обязательна для заполнения"
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        if date_obj < datetime.now().date():
            return False, "Дата не может быть в прошлом"
        return True, date_str
    except ValueError:
        return False, "Введите корректную дату в формате ГГГГ-ММ-ДД"


def validate_tariff(tariff):
    if not tariff:
        return False, "Выберите тариф"
    if tariff not in ['dohodyaga', 'busik', 'skorohod']:
        return False, "Некорректный тариф. Доступны: dohodyaga, busik, skorohod"
    return True, tariff


def create_user():
    print_header("СОЗДАНИЕ НОВОГО ПОЛЬЗОВАТЕЛЯ")

    while True:
        login = input("📧 Логин (4-16 символов, латиница и цифры): ")
        valid, msg = validate_login(login)
        if valid:
            break
        print_error(msg)

    while True:
        print("\n📋 Требования к паролю:")
        print("   • от 8 до 32 символов")
        print("   • хотя бы одна цифра")
        print("   • хотя бы одна строчная буква")
        print("   • хотя бы одна заглавная буква")
        print("   • хотя бы один спецсимвол (!@#$%^&*()")
        password = input("🔐 Пароль: ")
        valid, msg = validate_password(password)
        if valid:
            break
        print_error(msg)

    while True:
        lastname = input("👤 Фамилия (только буквы): ")
        valid, msg = validate_name(lastname, "Фамилия")
        if valid:
            break
        print_error(msg)

    while True:
        firstname = input("👤 Имя (только буквы): ")
        valid, msg = validate_name(firstname, "Имя")
        if valid:
            break
        print_error(msg)

    middlename = input("👤 Отчество (Enter - пропустить): ")
    if middlename:
        if not re.match(r'^[а-яА-Яa-zA-Z]*$', middlename):
            print_error("Отчество должно содержать только буквы")
            middlename = ""

    while True:
        phone = input("📱 Телефон (+7XXXXXXXXXX или 8XXXXXXXXXX): ")
        valid, msg = validate_phone(phone)
        if valid:
            break
        print_error(msg)

    data = {
        "login": login,
        "password": password,
        "lastname": lastname,
        "firstname": firstname,
        "phone": phone
    }

    if middlename:
        data["middlename"] = middlename

    try:
        response = requests.post(f"{BASE_URL}/users", json=data)
        result = response.json()

        if result.get('success'):
            print_success(f"Пользователь '{login}' успешно создан!")
            print(f"\n🆔 ID пользователя: {result['user']['id']}")
        else:
            print_error(result.get('error', 'Ошибка при создании пользователя'))
    except Exception as e:
        print_error(f"Ошибка подключения: {e}")

    wait_for_enter()


def create_order():
    print_header("ОФОРМЛЕНИЕ НОВОГО ЗАКАЗА")

    user_id = input("🆔 ID пользователя: ")
    if not user_id:
        print_error("ID пользователя обязателен")
        wait_for_enter()
        return

    while True:
        pickup = input("📍 Откуда забрать (не менее 5 символов): ")
        valid, msg = validate_address(pickup, "Адрес отправления")
        if valid:
            break
        print_error(msg)

    while True:
        delivery = input("📍 Куда доставить (не менее 5 символов): ")
        valid, msg = validate_address(delivery, "Адрес доставки")
        if valid:
            break
        print_error(msg)

    while True:
        date = input("📅 Дата (ГГГГ-ММ-ДД): ")
        valid, msg = validate_date(date)
        if valid:
            break
        print_error(msg)

    while True:
        phone = input("📱 Телефон получателя (+7XXXXXXXXXX или 8XXXXXXXXXX): ")
        valid, msg = validate_phone(phone)
        if valid:
            break
        print_error(msg)

    while True:
        distance_input = input("📏 Расстояние (км, от 0.001 до 70): ")
        valid, result = validate_distance(distance_input)
        if valid:
            distance = result
            break
        print_error(msg)

    while True:
        print("\n📋 Доступные тарифы:")
        print("   • dohodyaga (Доходяга, 29 ₽/км, вес 5-10 кг)")
        print("   • busik (Бусик, 59 ₽/км, вес до 200 кг)")
        print("   • skorohod (Скороход, 129 ₽/км, любой вес)")
        tariff = input("💰 Тариф: ").lower()
        valid, msg = validate_tariff(tariff)
        if valid:
            break
        print_error(msg)

    while True:
        weight_input = input("⚖️  Вес (кг): ")
        valid, result = validate_weight(weight_input, tariff)
        if valid:
            weight = result
            break
        print_error(msg)

    promo = input("🎫 Промокод (Enter - пропустить): ")

    data = {
        "user_id": user_id,
        "pickup_address": pickup,
        "delivery_address": delivery,
        "courier_date": date,
        "recipient_phone": phone,
        "distance": distance,
        "tariff": tariff,
        "weight": weight
    }

    if promo:
        data["promo_code"] = promo

    try:
        response = requests.post(f"{BASE_URL}/orders", json=data)
        result = response.json()

        if result.get('success'):
            print_success(f"Заказ успешно создан!")
            print(f"\n📦 Номер заказа: {result['order']['order_id']}")
            print(f"💰 Сумма: {result['order']['price']} ₽")
        else:
            print_error(result.get('error', 'Ошибка при создании заказа'))
    except Exception as e:
        print_error(f"Ошибка подключения: {e}")

    wait_for_enter()


def delete_user():
    """Удаление пользователя"""
    print_header("УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ")

    user_id = input("🆔 Введите ID пользователя для удаления: ")

    confirm = input(f"⚠️  Вы уверены, что хотите удалить пользователя {user_id}? (да/нет): ").lower()
    if confirm != 'да':
        print_info("Удаление отменено")
        wait_for_enter()
        return

    try:
        response = requests.delete(f"{BASE_URL}/users/{user_id}")
        result = response.json()

        if result.get('success'):
            print_success(f"Пользователь {user_id} успешно удалён!")
        else:
            print_error(result.get('error', 'Ошибка при удалении пользователя'))
    except Exception as e:
        print_error(f"Ошибка подключения: {e}")

    wait_for_enter()


def delete_order():
    """Удаление заказа"""
    print_header("УДАЛЕНИЕ ЗАКАЗА")

    order_id = input("📦 Введите ID или номер заказа для удаления: ")

    confirm = input(f"⚠️  Вы уверены, что хотите удалить заказ {order_id}? (да/нет): ").lower()
    if confirm != 'да':
        print_info("Удаление отменено")
        wait_for_enter()
        return

    try:
        response = requests.delete(f"{BASE_URL}/orders/{order_id}")
        result = response.json()

        if result.get('success'):
            print_success(f"Заказ {order_id} успешно удалён!")
        else:
            print_error(result.get('error', 'Ошибка при удалении заказа'))
    except Exception as e:
        print_error(f"Ошибка подключения: {e}")

    wait_for_enter()


def update_order_status():
    """Обновление статуса заказа"""
    print_header("ОБНОВЛЕНИЕ СТАТУСА ЗАКАЗА")

    order_id = input("📦 Введите ID или номер заказа: ")

    print("\n📋 Доступные статусы:")
    print("   1. 🟢 active - Активен")
    print("   2. ✅ delivered - Доставлен")
    print("   3. 🔴 cancelled - Отменён")

    status_choice = input("\n🔽 Выберите статус (1-3): ")

    status_map = {
        "1": "active",
        "2": "delivered",
        "3": "cancelled"
    }

    if status_choice not in status_map:
        print_error("Неверный выбор статуса")
        wait_for_enter()
        return

    new_status = status_map[status_choice]

    try:
        response = requests.post(f"{BASE_URL}/orders/{order_id}/status", json={"status": new_status})
        result = response.json()

        if result.get('success'):
            print_success(f"Статус заказа {order_id} изменён на '{new_status}'!")
        else:
            print_error(result.get('error', 'Ошибка при обновлении статуса'))
    except Exception as e:
        print_error(f"Ошибка подключения: {e}")

    wait_for_enter()


def main():
    while True:
        clear_screen()

        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚚   Д О С Т А В О Ч К И Н   -   A P I   К Л И Е Н Т       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)

        print("  📋 ГЛАВНОЕ МЕНЮ")
        print("  " + "─" * 50)
        print()
        print("  👥 ПОЛЬЗОВАТЕЛИ")
        print("     1. 👀  Показать всех пользователей")
        print("     2. 🔍  Найти пользователя по ID")
        print("     3. ➕  Создать нового пользователя")
        print("     4. 🗑️   Удалить пользователя")
        print()
        print("  📦 ЗАКАЗЫ")
        print("     5. 👀  Показать все заказы")
        print("     6. 🔍  Найти заказ по ID")
        print("     7. ➕  Создать новый заказ")
        print("     8. 🗑️   Удалить заказ")
        print("     9. 🔄  Обновить статус заказа")
        print("    10. 👤  Показать заказы пользователя")
        print()
        print("  📊 СТАТИСТИКА")
        print("    11. 📈  Показать статистику")
        print()
        print("     0. 🚪  Выход")
        print()
        print("  " + "─" * 50)

        choice = input("\n👉 Выберите пункт меню: ")

        if choice == "0":
            print_header("ДО СВИДАНИЯ!")
            print("👋 Спасибо за использование API клиента 'Доставочкин'!")
            break

        elif choice == "1":
            try:
                response = requests.get(f"{BASE_URL}/users")
                result = response.json()
                if result.get('success'):
                    print_users(result['users'])
                else:
                    print_error(result.get('error', 'Ошибка получения данных'))
            except Exception as e:
                print_error(f"Ошибка подключения к серверу: {e}")
            wait_for_enter()

        elif choice == "2":
            user_id = input("\n🆔 Введите ID пользователя: ")
            try:
                response = requests.get(f"{BASE_URL}/users/{user_id}")
                result = response.json()
                if result.get('success'):
                    print_user(result['user'])
                else:
                    print_error(result.get('error', 'Пользователь не найден'))
            except Exception as e:
                print_error(f"Ошибка подключения к серверу: {e}")
            wait_for_enter()

        elif choice == "3":
            create_user()

        elif choice == "4":
            delete_user()

        elif choice == "5":
            try:
                response = requests.get(f"{BASE_URL}/orders")
                result = response.json()
                if result.get('success'):
                    print_orders(result['orders'])
                else:
                    print_error(result.get('error', 'Ошибка получения данных'))
            except Exception as e:
                print_error(f"Ошибка подключения к серверу: {e}")
            wait_for_enter()

        elif choice == "6":
            order_id = input("\n📦 Введите ID или номер заказа: ")
            try:
                response = requests.get(f"{BASE_URL}/orders/{order_id}")
                result = response.json()
                if result.get('success'):
                    print_order(result['order'])
                else:
                    print_error(result.get('error', 'Заказ не найден'))
            except Exception as e:
                print_error(f"Ошибка подключения к серверу: {e}")
            wait_for_enter()

        elif choice == "7":
            create_order()

        elif choice == "8":
            delete_order()

        elif choice == "9":
            update_order_status()

        elif choice == "10":
            user_id = input("\n🆔 Введите ID пользователя: ")
            try:
                response = requests.get(f"{BASE_URL}/users/{user_id}/orders")
                result = response.json()
                if result.get('success'):
                    print_orders(result['orders'])
                else:
                    print_error(result.get('error', 'Ошибка получения данных'))
            except Exception as e:
                print_error(f"Ошибка подключения к серверу: {e}")
            wait_for_enter()

        elif choice == "11":
            try:
                response = requests.get(f"{BASE_URL}/stats")
                result = response.json()
                if result.get('success'):
                    print_stats(result['stats'])
                else:
                    print_error(result.get('error', 'Ошибка получения статистики'))
            except Exception as e:
                print_error(f"Ошибка подключения к серверу: {e}")
            wait_for_enter()

        else:
            print_error("Неверный выбор! Пожалуйста, выберите пункт от 0 до 11.")
            wait_for_enter()


if __name__ == "__main__":
    main()