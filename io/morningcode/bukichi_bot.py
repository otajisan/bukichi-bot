import os
import discord

from components.image_creator import ImageCreator

DISCORD_APP_TOKEN = os.getenv('DISCORD_APP_TOKEN')


class BukichiBotClient(discord.Client):

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author.bot:
            return
        print(f'Message from {message.author}: {message.content}')

    async def on_member_join(self, member):
        print(f'New member joined. {member}')

        guild = member.guild
        if guild.system_channel is not None:
            # to_send = f'Welcome {member.mention} to {guild.name}!'
            # await guild.system_channel.send(to_send)
            image_creator = ImageCreator()
            greeting_message = 'さん、はじめましてでし！'
            image = image_creator.from_text(member.name, greeting_message)
            await guild.system_channel.send(file=discord.File(image))


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = BukichiBotClient(intents=intents)
client.run(DISCORD_APP_TOKEN)
