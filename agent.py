
import asyncio
import sys, time
import traceback
from data.incon import Incon
from market.g2b import G2B
from bot.discord import Discord

from res.resource_manager import resource_manager as resmgr

settings_enable_pres = True
settings_enable_bids = True

def create_data_provider():
    # create incon object
    id = resmgr.get_account("incon","id")
    pw = resmgr.get_account("incon","pw")
    return Incon(id, pw, headless=False)

def create_markets() -> dict:
    markets = dict()       
    pw = resmgr.get_account("g2b","pw")
    rn = resmgr.get_account("g2b","rn")
    markets['나라장터'] = G2B(pw, rn)
    return markets

def create_notifier():
    token = resmgr.get_account("discord","token")
    channel_id = resmgr.get_account("discord","channel_id")
    return DiscordLogger(token, channel_id)
    
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


class DiscordLogger(Discord):
    def __init__(self, token, channel_id):
        self.__token = token
        self.__channel_id = channel_id

    async def start(self):
        await super().start(self.__token)

    async def send(self, message:str):
        await super().send(int(self.__channel_id), message)


async def main():

    try:
        notifier = create_notifier()
        await notifier.start()
        await notifier.send(discord_format_title("Start Incon Automatic Navigation Agent"))
        await print_line_break(notifier)     

        dp = create_data_provider()
        ms = create_markets()

        if settings_enable_pres:
            await notifier.send(discord_format_subtitle("Pre Stage"))                  
            await print_line_break(notifier)
            pres = dp.get_pre_data()
            for pre in pres:
                market = ms.get(pre.market)
                if not market:                    
                    continue

                if pre.is_completed():
                    continue

                if market.register(pre):
                    pre.complete()
                    time.sleep(0.1)
                    if not pre.is_completed():
                        raise Exception(f"agent) Clicked But Not Completed {pre.number}")
                    await notifier.send(discord_format_pre(pre))      
                    print(f"agent) Registered {pre.number} - {pre.title} ")

            await print_line_break(notifier)
            # Report Current Status
            # 
            # await print_line_break(notifier)
            # await notifier.send(discord_format_pres(pres))
            # await print_line_break(notifier)

        if settings_enable_bids:     
            await notifier.send(discord_format_subtitle("Bid Stage"))
            await print_line_break(notifier)
                       
            bids = dp.get_bid_data()
            for bid in bids:                
                market = ms.get(bid.market)
                if not market:
                    continue

                if bid.is_completed():
                    continue

                if not bid.is_ready:
                    continue

                success, message = market.participate(bid)
                if success:                    
                    bid.complete()
                    await notifier.send(discord_format_bid(bid))
                    print(f"agent) Registered {bid.number} - {bid.title} ")
                else:
                    print(f"agent) Can not participate in {bid.number}, {bid.title} - {message}")

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

