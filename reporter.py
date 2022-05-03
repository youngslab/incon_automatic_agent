
from bot.discord import Discord
from res.resource_manager import resource_manager as resmgr

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


def create_notifier():
    token = resmgr.get_account("discord","token")
    channel_id = resmgr.get_account("discord","channel_id")
    return DiscordLogger(token, channel_id)
    