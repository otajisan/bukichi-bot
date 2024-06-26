import os
import textwrap

import discord

from discord.ext import tasks
from datetime import datetime as dt

from components.image_creator import ImageCreator
from components.stage_image_creator import StageImageCreator
from components.fest_image_creator import FestStageImageCreator
from components.salmon_run_stage_image_creator import SalmonRunStageImageCreator
from components.splatoon3_api_client import Splatoon3ApiClient

DISCORD_APP_TOKEN = os.getenv('DISCORD_APP_TOKEN')
BOT_CHANNEL_ID = os.getenv('BOT_CHANNEL_ID')


class BukichiBotClient(discord.Client):
    DEBUG = False

    async def on_ready(self):
        print(f'Logged on as {self.user}! bot_channel: {BOT_CHANNEL_ID}')
        self.bot_channel = self.get_channel(int(BOT_CHANNEL_ID))
        self.batch_send_stage_image.start()
        self.batch_send_salmon_run_stage_image.start()

    async def on_message(self, message):
        if message.author.bot:
            return
        print(f'Message from {message.author}: {message.content}')
        if self.DEBUG:
            await self.debug_image(message)

    async def debug_image(self, message):
        member = message.author
        guild = member.guild

        image_creator = ImageCreator()

        names = [
            'foo',
            'テスト',
            'てすと',
            'テスト太郎',
            'Discordマン',
        ]
        for name in names:
            image = image_creator.greeting_by_name(name)
            if image != '':
                await guild.system_channel.send(file=discord.File(image))
            else:
                plain_greeting_message = await self.get_greeting_message(name)
                await guild.system_channel.send(plain_greeting_message)

    async def on_member_join(self, member):
        print(f'New member joined. {member}')

        guild = member.guild
        if guild.system_channel is not None:
            # to_send = f'Welcome {member.mention} to {guild.name}!'
            # await guild.system_channel.send(to_send)
            name = member.display_name
            print(f'member: {member}')
            image_creator = ImageCreator()
            image = image_creator.greeting_by_name(name)
            if image != '':
                await guild.system_channel.send(file=discord.File(image))
            else:
                plain_greeting_message = await self.get_greeting_message(name)
                await guild.system_channel.send(plain_greeting_message)

    async def get_greeting_message(self, name):
        return textwrap.dedent(f'''
                {name} さん、はじめましてでし！
                まずは #ルール をよんでね。
                ''')

    @tasks.loop(seconds=60)
    async def batch_send_stage_image(self):

        current_time = dt.now().strftime('%H:%M')
        # print(f'check time. current_time: {current_time}')
        if current_time == '09:00' or current_time == '17:00':
            print('start create stage image.')
            image_creator = StageImageCreator()
            image = image_creator.run()
            print(f'created image: {image}')

            if image is not None:
                await self.bot_channel.send(file=discord.File(image))
                os.remove(image)

            print('start create fest stage image.')
            fest_image_creator = FestStageImageCreator()
            fest_image = fest_image_creator.run()
            print(f'created fest image: {fest_image}')

            if fest_image is not None:
                await self.bot_channel.send(file=discord.File(fest_image))
                os.remove(fest_image)

            print('finish send stage image.')

    @tasks.loop(seconds=60)
    async def batch_send_salmon_run_stage_image(self):
        current_time = dt.now().strftime('%H:%M')
        # print(f'check time. current_time: {current_time}')
        if current_time == '09:01' or current_time == '17:01' or current_time == '01:01':
            print('start fetch salmon run stage info.')
            api_client = Splatoon3ApiClient()
            stages = api_client.fetch_salmon_run_stages()
            print('start create salmon run stage image.')
            image_creator = SalmonRunStageImageCreator()
            image = image_creator.run(stages)
            print(f'created image: {image}')

            if image is not None:
                await self.bot_channel.send(file=discord.File(image))
                os.remove(image)

            print('finish send stage image.')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = BukichiBotClient(intents=intents)
client.run(DISCORD_APP_TOKEN)
