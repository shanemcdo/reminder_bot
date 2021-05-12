import discord, os
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

def convert_time(time_string: str) -> int:
    """Returns time in seconds"""
    try:
        return float(time_string)
    except:
        pass
    if len(time_string) < 2:
        raise ValueError(f'\'{time_string}\' is not a valid timestring. e.g. 5h\n\tThe valid units are s, m, h, d, and w')
    unit = time_string[-1].lower()
    try:
        time = float(time_string[:-1])
    except ValueError:
        raise ValueError(f'\'{time_string}\' is not a valid timestring. e.g. 5h\n\tThe valid units are s, m, h, d, and w')
    if unit == 's':
        return time
    elif unit == 'm':
        return time * 60
    elif unit == 'h':
        return time * 60 * 60
    elif unit == 'd':
        return time * 60 * 60 * 24
    elif unit == 'w':
        return time * 60 * 60 * 24 * 7
    else:
        raise ValueError(f'{unit} is not a valid unit\n\tThe valid units are s, m, h, d, and w')

if __name__ == "__main__":
    load_dotenv()
    bot.run(os.environ['TOKEN'])
