import discord
from OsuTracker import OsuTracker

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!osu'):
        msg = app.exec(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name="Farming Sotarks map"))
    client.loop.create_task(app.checkTracked(client))

if __name__ == '__main__':

    with open('./.secret', 'r') as t:
        TOKEN = t.readline().split(' ')[0]
    app = OsuTracker()
    
    client.run(TOKEN)

