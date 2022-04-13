
import asyncio
import sys
import traceback

sys.path.insert(1, 'C:\\Users\\Jaeyoung\\dev\\incon_project')

from data.incon import Incon
from market.g2b import G2B
from bot.discord import Discord

settings_enable_pres = True
settings_enable_bids = True

def create_data_provider(account):
    # create incon object
    return Incon(account['id'], account['pw'])

def create_markets(account) -> dict:
    markets = dict()       
    markets['나라장터'] = G2B(account['pw'])
    return markets

def create_notifier(account):
    return DiscordLogger(account["token"], account['channel_id'])
    
def discord_get_char_emoji(ch):
    return ":regional_indicator_{}:".format(ch)

def discord_get_market_emoji(market):
    if market == "나라장터":
        return discord_get_char_emoji("n")
    elif market == "국방조달":
        return discord_get_char_emoji("k")
    elif market == "국방전자조달":
        return discord_get_char_emoji("k")
    elif market == "한국전력":
        return discord_get_char_emoji("h")
    else:
        return discord_get_char_emoji("e")

# common format for everything
def discord_format_item(x) -> str:
    complete_sign = ":small_blue_diamond:" if x.is_completed() else ":small_orange_diamond:"
    return f"{complete_sign} {discord_get_market_emoji(x.market)}" \
        f"`{ascii_only(x.number):20s}` :name_badge: `{x.title:.10s}`"


def discord_format_pre(pre) -> str:
    return discord_format_item(pre)
    
def discord_format_bid(bid) -> str:
    return f"{discord_format_item(bid)} :moneybag: {bid.price}"

def discord_format_pres(pres) -> str:
    ls = [discord_format_pre(pre) for pre in pres ]    
    return "\n".join(ls)

def discord_format_bids(bids) -> str:
    ls = [discord_format_bid(bid) for bid in bids ]    
    return "\n".join(ls)

def discord_format_title(title):
    return ":mega:  __**{}**__".format(title)

def discord_format_subtitle(sub):
    return ":triangular_flag_on_post: \t\t\t **{}**".format(sub)

def ascii_only(s):
    return "".join(ch for ch in s if ch.isascii())

async def print_line_break(notifier):
    await notifier.send("---------------------------------")


def iaa_get_accounts():
    import os, json
    path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(path, ".accounts.json")
    with open(filepath, 'r')  as f:
        return json.loads(f.read())


class DiscordLogger(Discord):
    def __init__(self, token, channel_id):
        self.__token = token
        self.__channel_id = channel_id

    async def start(self):
        await super().start(self.__token)

    async def send(self, message:str):
        await super().send(int(self.__channel_id), message)


async def main():
    accounts = iaa_get_accounts()

    try:
        notifier = create_notifier(accounts['discord'])
        await notifier.start()
        await notifier.send(discord_format_title("Start Incon Automatic Navigation Agent"))
        await print_line_break(notifier)     


        dp = create_data_provider(accounts['incon'])
        ms = create_markets(accounts['g2b'])

        if settings_enable_pres:            
            pres = dp.get_pre_data()        
            for pre in pres:
                market = ms.get(pre.market)
                if not market:                    
                    continue

                if market.register(pre):
                    pre.complete()
                    print(f"agent) Registered {pre.number} - {pre.title} ")

            # Report Current Status
            await notifier.send(discord_format_subtitle("Pre Stage"))
            await print_line_break(notifier)
            await notifier.send(discord_format_pres(pres))
            await print_line_break(notifier)

        if settings_enable_bids:                
            bids = dp.get_bid_data()
            for bid in bids:                
                market = ms.get(bid.market)
                if not market:
                    continue

                if not bid.is_ready:
                    continue

                success, message = market.participate(bid)
                if success:                    
                    bid.complete()
                    print(f"agent) Registered {bid.number} - {bid.title} ")
                else:
                    print(f"agent) Can not participate in {bid.number}, {bid.title} - {message}")
            
            # Report Current Status
            await notifier.send(discord_format_subtitle("Bid Stage"))
            await print_line_break(notifier)
            await notifier.send(discord_format_bids(bids))
            await print_line_break(notifier)

        
    except Exception as e:        
        await notifier.send(str(e))
        traceback.print_exception(*sys.exc_info())

    await notifier.exit()


if __name__ == "__main__":    
    # windows problem
    # RuntimeError: Event loop is closed
    # https://gmyankee.tistory.com/330    
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())

