import discord
from discord.ext import commands
from globalVars import reddit, tab
import prawcore.exceptions as pce

sorts = ['new', 'rising', 'hot', 'top', 'random']
times = ['hour', 'day', 'week', 'month', 'year', 'all']


class Reddit(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(description=('Fetches a post from Reddit.\n'
                                   'If the command is called by itself, it gets the hottest post on Reddit.\n'
                                   'If called with a Subreddit, it gets the hottest post from that Subreddit.\n'
                                   'If called with a Subreddit and sort, it gets the top post from the Subreddit using the sort.\n'
                                   'If the sort used is `all`, you can specify a timeframe like `day` or `year`.'),
                      category='Reddit Commands',
                      brief='Fetches a post from Reddit.')
    async def get(self, ctx, sub='all', sort='hot', time='day'):

        sort = sort.lower()
        time = time.lower()
        posts = None

        if sort in sorts and time in times:
            if sort == 'new':
                posts = reddit.subreddit(sub).new(limit=5)
            elif sort == 'rising':
                posts = reddit.subreddit(sub).rising(limit=5)
            elif sort == 'random':
                posts = reddit.subreddit(sub).random_rising(limit=5)
            elif sort == 'hot':
                posts = reddit.subreddit(sub).hot(limit=5)
            elif sort == 'top':
                posts = reddit.subreddit(sub).top(time_filter=time, limit=5)
        else:
            if not sort in sorts:
                await ctx.send(f'Invalid sort. Choose from `{", ".join(sorts)}`.')
            elif not time in times:
                await ctx.send(f'Invalid time. Choose from `{", ".join(times)}`.')
            else:
                await ctx.send('Something went wrong, and we don\'t know what!')
            return

        try:
            for post in posts:
                # Making sure NSFW posts can only be sent on NSFW channels
                if post.over_18:
                    if not ctx.channel.nsfw:
                        await ctx.send("This post is NSFW! To see it, use this command in a NSFW channel.")
                        return

                if post.stickied:
                    continue

                embed = discord.Embed(
                    colour=discord.Colour.from_rgb(255, 69, 0),
                    title=post.title if len(
                        post.title) <= 256 else post.title[:253] + '...',
                    description=post.selftext if len(
                        post.selftext) <= 2048 else '',
                    url=post.shortlink)

                if hasattr(post, 'post_hint'):
                    if post.post_hint != 'link':
                        if post.post_hint == 'image':
                            embed.set_image(url=post.url)
                        else:
                            embed.set_image(
                                url=post.preview['images'][0]['source']['url'])
                    else:
                        embed.set_image(
                            url=post.preview['images'][0]['source']['url'])

                if post.total_awards_received > 0:
                    embed.set_footer(text=(f'⬆️ {post.score}{tab}'
                                           f'💎 {post.total_awards_received}{tab}'
                                           f'📄 {post.num_comments}'))
                else:
                    embed.set_footer(
                        text=f'⬆️ {post.score}{tab}📄 {post.num_comments}')

                embed.add_field(name='Subreddit',
                                value=post.subreddit_name_prefixed)

                if post.subreddit.icon_img:
                    embed.set_thumbnail(url=post.subreddit.icon_img)

                embed.set_author(name=f'u/{post.author.name}',
                                 icon_url=post.author.icon_img)

                await ctx.send(embed=embed)
                return
            await ctx.send('No posts to show!')

        except (pce.NotFound, pce.Redirect):

            await ctx.send('No such subreddit!')


def setup(client):
    client.add_cog(Reddit(client))
