import discord, os, datetime
from asyncio import sleep
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

bot = commands.Bot(command_prefix='&')
slash = SlashCommand(bot, sync_commands=True)
guild_ids = [
        658961897969942529, # test server
        841274945148420106, # timothy server
        ]

lists = {}

@bot.event
async def on_ready():
    print('ready')

@bot.event
async def on_raw_reaction_add(payload):
    ...

@slash.slash(
        name="add",
        description="Add items to todo list",
        guild_ids=guild_ids,
        options=[
            create_option(
                name="items",
                description="Items to include in the todo list in a comma seperated list",
                option_type=3,
                required=True,
                ),
            ],
        )
async def add(ctx, items: str):
    if lists.get(ctx.author) is None:
        lists[ctx.author] = []
    for item in items.split(','):
        lists[ctx.author].append(item.strip())
    await ctx.send('items added')

@slash.slash(
        name="remove",
        description="remove items from list",
        guild_ids=guild_ids,
        options=[
            create_option(
                name="indicies",
                description="numbers in coma seperated list to be removed from list",
                option_type=3,
                required=True,
                ),
            ],
        )
async def remove(ctx, indicies: str):
    if lists.get(ctx.author) is None:
        lists[ctx.author] = []
        return
    indicies = list(map(int, indicies.split(',')))
    lists[ctx.author] = [item for i, item in enumerate(lists[ctx.author]) if i + 1 not in indicies]
    await ctx.send('items removed')

@slash.slash(
        name='show',
        description='Show the todo list',
        guild_ids=guild_ids,
        )
async def show(ctx):
    if lists.get(ctx.author) is None:
        lists[ctx.author] = []
    result = '```Heres ur list lol\n'
    for i, item in enumerate(lists[ctx.author]):
        result += f'{i + 1}: {item.strip()}\n'
    result += '```'
    msg = await ctx.send(result)

@slash.slash(
        name='remindme',
        description='remind the user in a specified time',
        guild_ids=guild_ids,
        )
async def remindme(ctx, message: str, time: str):
    try:
        converted_time = convert_time(time)
    except ValueError as e:
        await ctx.send(f'ValueError: {e}')
        return
    await ctx.send('Ok i\'ll remind you')
    await sleep(converted_time)
    await ctx.channel.send(f'{ctx.author.mention} you wanted me to remind you: ```{message}```')

def convert_time(time_string: str) -> float:
    """Returns time in seconds"""
    time, unit = split_num_alpha(time_string)
    unit = unit.lower()
    if unit == 's' or unit == 'sec' or unit == 'second' or unit == 'seconds':
        return time
    elif unit == 'm' or unit == 'min' or unit == 'minute' or unit == 'minutes':
        return time * 60
    elif unit == 'h' or unit =='hr' or unit == 'hour' or unit == 'hours':
        return time * 60 * 60
    elif unit == 'd' or unit == 'day' or unit == 'days':
        return time * 60 * 60 * 24
    elif unit == 'w' or unit == 'week' or unit == 'weeks':
        return time * 60 * 60 * 24 * 7
    elif unit == 'am' or unit == 'pm':
        return get_secs_till_next(datetime.time(int(time // 100 + 12 * (unit == 'pm')), int(time % 100)))
    else:
        raise ValueError(f'{unit} is not a valid unit\n\tThe valid units are s, m, h, d, and w')

def split_num_alpha(s: str) -> (float, str):
    index = -1
    complete = True
    for i, ch in enumerate(s):
        if ch == '.' or ch.isnumeric():
            index = i
        else:
            complete = False
            break
    if index == -1:
        return 0.0, s
    if complete:
        return float(s), ''
    return float(s[:i]), s[i:]

def get_secs_till_next(time: datetime.time) -> float:
    now = datetime.datetime.today()
    new = datetime.datetime(
            now.year,
            now.month,
            now.day,
            time.hour,
            time.minute,
            time.second
            )
    if new < now:
        new.replace(day=new.day + 1)
    delta = new - now
    return delta.seconds

if __name__ == "__main__":
    load_dotenv()
    bot.run(os.environ['TOKEN'])
