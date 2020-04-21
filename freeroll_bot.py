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


@client.on(events.NewMessage(chats=URL))
async def get_new_msg(event):
    """Создает событие при появлении нового сообщения в чате"""
    await event.message.mark_read()  # пометить сообщение прочитанным

    # Если рум находится в белом списке, отправляет message пользователю
    if check_room(event.message):
        await client.send_message(username, event.message)

    print(event.message.to_dict()['message'])


def check_room(message):
    """Проверяет находится ли рум в белом списке"""
    white_list = config['Telegram']['white_list']
    room_name = message.to_dict()['message'][:20]
    room_name = room_name.split()[0]
    if room_name in white_list:
        return True
    else:
        return False


client.start()
client.run_until_disconnected()
