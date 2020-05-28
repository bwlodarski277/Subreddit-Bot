import discord
from discord.ext import commands
from globalVars import reddit, tab
import prawcore.exceptions as pce

sorts = ['new', 'rising', 'hot', 'top', 'random']
times = ['hour', 'day', 'week', 'month', 'year', 'all']

description = ''
with open('cogs/get.txt', 'r') as file:
    description = file.read()


class Reddit(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(description=description, brief='Fetches a post from Reddit.')
    async def get(self, ctx, sub='all', sort='hot', time='day'):

        sort = sort.lower()
        time = time.lower()
        posts = None

        sub = reddit.subreddit(sub)  # Getting the subreddit

        options = {'new': sub.new(limit=5), 'rising': sub.rising(limit=5),
                   'random': sub.random_rising(limit=5), 'hot': sub.hot(limit=5),
                   'top': sub.top(time_filter=time, limit=5)}

        if sort in sorts:  # Checking if the user chose a valid sort
            if sort == 'top' and not time in times:  # If 'top' used as sort, check if time is valid
                await ctx.send(f'Invalid time. Choose from `{", ".join(times)}`.')
                return
            posts = options.get(sort)
        else:
            await ctx.send(f'Invalid sort. Choose from `{", ".join(sorts)}`.')
            return

        try:
            for post in posts:  # This only goes through one post as we only want one
                if post.over_18 and not ctx.channel.nsfw:
                    await ctx.send("This post is NSFW! To see it, use this command in a NSFW channel.")
                    return

                if post.stickied:  # Don't want stickied posts
                    continue

                title = post.title
                if len(title) > 256:
                    title = title[:253] + '...'

                description = post.selftext
                if len(description) > 2048:
                    description = ''

                embed = discord.Embed(  # Creating the embed
                    colour=discord.Colour.from_rgb(255, 69, 0),
                    title=title,
                    description=description,
                    url=post.shortlink)

                if hasattr(post, 'post_hint'):  # If the post contains media
                    if post.post_hint == 'image':  # If it's an image we can get the URL
                        embed.set_image(url=post.url)
                    else:  # If not, we need to use the media preview
                        img = post.preview['images'][0]['source']['url']
                        embed.set_image(url=img)

                footer = f'⬆️ {post.score}{tab}📄 {post.num_comments}'
                if post.total_awards_received > 0:
                    footer = f'⬆️ {post.score}{tab}💎 {post.total_awards_received}{tab}📄 {post.num_comments}'

                embed.set_footer(text=footer)

                embed.add_field(name='Subreddit',
                                value=post.subreddit_name_prefixed)

                if post.subreddit.icon_img:  # If the subreddit has a custom icon
                    embed.set_thumbnail(url=post.subreddit.icon_img)

                embed.set_author(name=f'u/{post.author.name}',
                                 icon_url=post.author.icon_img)

                await ctx.send(embed=embed)
                return

            # Happens if 'posts' is empty
            await ctx.send('No posts to show!')

        except Exception:
            # When the sub doesn't exist, too many exceptions happen so just catch 'em all
            await ctx.send('No such subreddit!')


def setup(client):
    client.add_cog(Reddit(client))
