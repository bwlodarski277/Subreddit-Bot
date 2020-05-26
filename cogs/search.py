import discord
from discord.ext import commands
from globalVars import reddit, tab
import prawcore.exceptions as pce

sorts = ['relevance', 'hot', 'top', 'new', 'comments']
times = ['hour', 'day', 'week', 'month', 'year', 'all']


class Reddit(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(description=('Searches Reddit using a provided string.\n'
                                   'Search strings must be surrounded by quotes.\n'
                                   'By default, the command will get the most relevant posts of all time.\n'
                                   'You can specify a sort after the string, as well as timeframe to search.\n'
                                   'You can also specify a subreddit to search.'),
                      category='Reddit Commands',
                      brief='Searches Reddit using query.')
    async def search(self, ctx, query=None, sort='relevance', time='all', sub='all'):

        sort = sort.lower()
        time = time.lower()

        if not query:
            await ctx.send('Please enter a search query!')
            return

        if sort not in sorts:
            await ctx.send(f'Invalid sort. Choose from `{", ".join(sorts)}`.')
            return

        elif time not in times:
            await ctx.send(f'Invalid time. Choose from `{", ".join(times)}`.')
            return

        embed = discord.Embed(
            colour=discord.Colour.from_rgb(255, 69, 0),
            title='Search reults',
            description=f'{ctx.author.display_name} searched for "{query}"')

        results = reddit.subreddit(sub).search(
            query=query, sort=sort, time_filter=time, limit=5)

        try:
            for post in results:

                title = post.title if len(
                    post.title) <= 256 else post.title[:253] + '...'

                embed.add_field(name=title,
                                value=(f'[view]({post.shortlink}){tab}'
                                       f'{post.subreddit_name_prefixed}'),
                                inline=False)

            await ctx.send(embed=embed)

        except (pce.NotFound, pce.Redirect):

            await ctx.send('No such subreddit!')


def setup(client):
    client.add_cog(Reddit(client))
