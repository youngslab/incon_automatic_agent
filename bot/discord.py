

from nextcord.ext import commands
import asyncio 

class Discord:
    bot = commands.Bot(command_prefix='$')
    ready = asyncio.Event()

    async def start(self, token:str):
        self.discord_task = asyncio.create_task(Discord.bot.start(token))
        await Discord.ready.wait()

    async def exit(self):
        await Discord.bot.close()

    async def send(self, channel_id:int, message:str):
        channel = Discord.bot.get_channel(channel_id)
        if channel is None:
            raise Exception(f"discord) Can not find channel: {channel_id}")
        await channel.send(message)
        await asyncio.sleep(0.1)

    @bot.event
    async def on_ready():
        print(f"Discord bot logged in as name={Discord.bot.user.name}, id={Discord.bot.user.id}")
        Discord.ready.set()

    # @bot.event
    # async def on_message(message):
    #     if message.author == client.user:
    #         return
        # if message.content.startswith('$'): # 만약 $hello로 시작하는 채팅이 올라오면
        #     await message.channel.send('Hello!') # Hello!라고 보내기

    # @client.command()
    # async def foo(ctx, arg):
    #     await ctx.send("foo command recieved with argument={}.".format(arg))


def load_settings(file):
    import json
    with open(file, 'r') as j:
        return json.loads(j.read())
        

async def main():
    import os
    path = os.path.dirname(os.path.abspath(__file__))
    settings = os.path.join(path, ".bot.json")

    token, channel = load_settings(settings)    
    print(f"bot information: token={token}, channel={channel}")
    
    bot = Discord()

    await bot.start(token)
    await bot.send(channel, "Hello, ")
    await bot.send(channel, "Discord Bot!")
    await bot.exit()


if __name__ == '__main__':

    # windows problem
    # RuntimeError: Event loop is closed
    # https://gmyankee.tistory.com/330    
    import sys
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
 
    asyncio.run(main())





