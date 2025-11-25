import time
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from comm_app.utils import send_telegram_message  # Импорт функции автоответа


class Command(BaseCommand):
    help = 'Poll Telegram for new messages every 5 seconds'

    def handle(self, *args, **options):
        self.stdout.write('Starting Telegram polling...')
        offset = 0  # ID последнего обработанного обновления
        bot_token = settings.TELEGRAM_BOT_TOKEN

        while True:  # Бесконечный цикл
            try:
                url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
                params = {
                    'offset': offset,
                    'timeout': 5,  # Long polling: ждёт до 5 сек
                    'allowed_updates': ['message']  # Только сообщения
                }
                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if data['ok']:
                    updates = data['result']
                    for update in updates:
                        self._handle_update(update)
                        offset = update['update_id'] + 1  # Следующий offset


                # Пауза 5 сек, если нет обновлений (long polling уже ждёт)
                if not updates:
                    time.sleep(5)
                else:
                    time.sleep(0.1)  # Короткая пауза при нагрузке

            except requests.RequestException as e:
                self.stdout.write(f'Polling error: {e}')
                time.sleep(5)  # Retry delay

    def _handle_update(self, update):
        """Обработка одного обновления (аналогично webhook)"""
        message = update.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        client_id = str(chat_id)
        text = message.get('text', '')

        if not text:
            return

        # Логируем
        from comm_app.models import Client, Ticket
        from comm_app.models import MessageIn

        # создание(если раньше не было сообщений)/выбор клиента
        client, created = Client.objects.get_or_create(tg_chat_id=client_id)
        # создание/выбор тикета
        ticket = client.tickets.order_by('-timestamp').first()
        if ticket is None or ticket.status == "close":
            ticket = Ticket.objects.create(
                chat=client,
                status="open",
                user=None  # или назначенный оператор, если есть
            )

        # назначение сообщения тикету
        MessageIn.objects.create(chat_id=client, text=text, ticket_id=ticket)

        # Автоответ
        auto_reply = "Ваше сообщение принято в работу. Ожидайте ответа от оператора."
        send_telegram_message(chat_id, auto_reply)
        self.stdout.write(f'Handled message from {client_id}: {text[:50]}')