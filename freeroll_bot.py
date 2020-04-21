import configparser
import json
# для корректного переноса времени сообщений в json
from datetime import date, datetime

from telethon.sync import TelegramClient, events

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, int(api_id), api_hash)
client.start()


@client.on(events.NewMessage(chats='UAPOKER - пароли на фрироллы'))
async def got_new_msg(event):
    event.message.mark_read()  # пометить сообщение прочитанным
    print(event.message.to_dict()['message'])


async def dump_messages(channel):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    offset_msg = 0  # номер записи, с которой начинается считывание
    limit_msg = 2  # максимальное число записей, передаваемых за один раз

    all_messages = []  # список всех сообщений
    total_messages = 0
    total_count_limit = 2  # поменяйте это значение, если вам нужны не все сообщения

    class DateTimeEncoder(json.JSONEncoder):
        """Класс для сериализации записи дат в JSON"""

        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())

        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    with open('channel_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)


async def get_last_msg(channel):
    """Возвращает сущность последнего сообщения из канала/чата"""
    history = await client(GetHistoryRequest(
        peer=channel,
        offset_id=0,
        offset_date=None, add_offset=0,
        limit=1, max_id=0, min_id=0,
        hash=0))
    return history.messages[0]


def check_room(message):
    """Проверяет находится ли рум в белом списке"""
    white_list = config['Telegram']['white_list']
    room_name = message.to_dict()['message'][:20]
    room_name = room_name.split()[0]
    if room_name in white_list:
        return True
    else:
        return False


async def main():
    url = "https://t.me/uapoker_passwords"
    channel = await client.get_entity(url)

    message = await get_last_msg(channel)
    if check_room(message):
        await client.send_message(username, message)


with client:
    client.loop.run_until_complete(main())
