import discord, praw, json, logging
from datetime import datetime
from discord.ext import commands

tab = ' ' * 4

with open('config.json') as config:
    prefix, token, reddit_oauth = json.load(config).values()

reddit = praw.Reddit('SubredditBot')

sorts = ['new', 'rising', 'hot', 'top', 'random']
times = ['hour', 'day', 'week', 'month', 'year', 'all']

bot = commands.Bot(command_prefix=prefix)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@bot.command()
async def get(ctx, sub='all', sort='hot', time='day'):
    sort = sort.lower()
    time = time.lower()
    posts = None
    if sort in sorts and time in times:
        if   sort == 'new':
            posts = reddit.subreddit(sub).new(limit = 5)
        elif sort == 'rising':
            posts = reddit.subreddit(sub).rising(limit = 5)
        elif sort == 'random':
            posts = reddit.subreddit(sub).random_rising(limit = 5)
        elif sort == 'hot':
            posts = reddit.subreddit(sub).hot(limit = 5)
        elif sort == 'top':
            posts = reddit.subreddit(sub).top(time_filter=time, limit = 5)
    else:
        if not sort in sorts:
            await ctx.send(f'Invalid sort. Choose from `{", ".join(sorts)}`.')
        elif not time in times:
            await ctx.send(f'Invalid time. Choose from `{", ".join(times)}`.')
        else:
            await ctx.send('Something went wrong, and we don\'t know what!')
        return

    for post in posts:
        if post.stickied:
            continue

        embed = discord.Embed(
            colour = discord.Colour.from_rgb(255, 69, 0),
            title = post.title,
            description = post.selftext if len(post.selftext) <= 2048 else '',
            url = post.shortlink,
            video = post.url if post.is_video else '')

        if hasattr(post, 'post_hint'):
            if not post.is_video:
                if post.post_hint == 'image':
                    embed.set_image(url=post.url)
                elif post.post_hint == 'link':
                    if post.url.endswith('.gifv'):
                        embed.set_image(url=post.thumbnail)
                    else:
                        embed.set_image(url=post.url)
            else:
                embed.set_image(url=post.thumbnail)
        if post.total_awards_received > 0:
            embed.set_footer(text=(#f'{post.subreddit_name_prefixed}{tab}'
                                   f'⬆️ {post.score}{tab}'
                                   f'💎 {post.total_awards_received}{tab}'
                                   f'📄 {post.num_comments}'))
        else:
            embed.set_footer(text=f'⬆️ {post.score}{tab}📄 {post.num_comments}')
        embed.add_field(name='Subreddit', value=post.subreddit_name_prefixed)
        await ctx.send(embed=embed)
        break

@bot.event
async def on_message(message):
    if message.content.startswith(prefix):
        print(f'[{datetime.now()}] {message.author.name}: {message.content}')
        await bot.process_commands(message)

@bot.event
async def on_ready():
    helpMsg = discord.CustomActivity('Use r/help')
    await bot.change_presence(activity=helpMsg)
    print(f'Logged in as {bot.user.name}')

bot.run(token)
