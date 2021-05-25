import discord, os, datetime, json
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
FILE_NAME = 'data.json'

def save_lists():
    with open(FILE_NAME, 'w+') as f:
        json.dump(lists, f)

def load_lists():
    global lists
    try:
        with open(FILE_NAME, 'r') as f:
            lists = json.load(f)
    except FileNotFoundError:
        pass

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
    auth = str(ctx.author)
    if lists.get(auth) is None:
        lists[auth] = []
    for item in items.split(','):
        lists[auth].append(item.strip())
    await ctx.send('items added')
    save_lists()

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
    auth = str(ctx.author)
    if lists.get(auth) is None:
        lists[auth] = []
        return
    indicies = list(map(int, indicies.split(',')))
    lists[auth] = [item for i, item in enumerate(lists[auth]) if i + 1 not in indicies]
    await ctx.send('items removed')
    save_lists()

@slash.slash(
        name='show',
        description='Show the todo list',
        guild_ids=guild_ids,
        )
async def show(ctx):
    auth = str(ctx.author)
    if lists.get(auth) is None:
        lists[auth] = []
    result = '```Heres ur list lol\n'
    for i, item in enumerate(lists[auth]):
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
        hr, mn = divmod(time, 100)
        return get_secs_till_next(datetime.time(int(hr + 12 * ((unit == 'pm') ^ (hr == 12))) % 24, int(mn)))
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
    load_lists()
    bot.run(os.environ['TOKEN'])
