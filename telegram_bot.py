import asyncio
from telegram import Bot

messages = []


async def main(message):
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot = Bot(token='5989087240:AAHPIS0qpEwx_UGQvfDMgll4pIfOVisqaVI')

    # Replace 'CHAT_ID' with the ID of the chat you want to send the message to
    # If you want to send the message to yourself, you can use your own user ID
    chat_id = '-1001649181082'

    # Send a message
    await bot.send_message(chat_id=chat_id, text=message)


# Run the main coroutine
def send_message(message):
    if len(messages) > 5:
        m_ = ""
        for idx, m in enumerate(messages):
            m_ = m_ + """
            {}){}""".format(idx + 1, m)
        asyncio.run(main(m_))
        messages.clear()
    else:
        messages.append(message)
