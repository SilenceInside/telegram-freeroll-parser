import configparser

from telethon.sync import TelegramClient, events

URL = "https://t.me/uapoker_passwords"

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, int(api_id), api_hash)
print("Test version\n")


@client.on(events.NewMessage(chats=URL))
async def get_new_msg(event):
    """Создает событие при появлении нового сообщения в чате"""

    # Если рум не в белом списке, сообщение отмечается прочитанным
    if not check_room(event.message):
        await event.message.mark_read()  # пометить сообщение прочитанным

    print(event.message.to_dict()['message'])


def check_room(message):
    """Проверяет находится ли рум в белом списке"""
    white_list = config['Telegram']['white_list'].split(", ")
    message: str = message.to_dict()['message']

    for room in white_list:
        index: int = message.find(room, 0, 20)

        if index != -1:
            return True

    return False


client.start()
client.run_until_disconnected()
