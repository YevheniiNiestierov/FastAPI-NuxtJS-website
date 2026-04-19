import os

import requests

TOKEN = os.environ['BOT_API_TOKEN']
CHAT_ID = os.environ['CHAT_ID']


def send_message(order):
    """Send formatted order message to Telegram"""
    products_text = "\n".join([
        f"  • {p['title']} x{p['quantity']} - {p['price']}₴"
        for p in order['products']
    ])

    message = f"""
    Нове замовлення:
    
👤 ПІБ: {order['name']}
📱 Телефон: {order['phone_number']}

📦 Доставка:
    Пошта: {order['delivery_type']}
    Місто: {order['city']}
    Номер відділення: {order['department_number']}

🛍 Продукти: 
    {products_text}

💰 Сума: {order['total_sum']}₴

📅 Створено: {order['created_at'].strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)

    return response.json()

