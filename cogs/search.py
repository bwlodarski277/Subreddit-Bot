import discord
from discord.ext import commands
from globalVars import reddit, tab
import prawcore.exceptions as pce

sorts = ['relevance', 'hot', 'top', 'new', 'comments']
times = ['hour', 'day', 'week', 'month', 'year', 'all']

description = ''
with open('cogs/search.txt', 'r') as file:
    description = file.read()


class Reddit(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(description=description, brief='Searches Reddit using query.')
    async def search(self, ctx, query=None, sort='relevance', time='all', sub='all'):

        sort = sort.lower()
        time = time.lower()

        if not query:
            await ctx.send('Please enter a search query!')
            return

        if sort not in sorts:
            await ctx.send(f'Invalid sort. Choose from `{", ".join(sorts)}`.')
            return

        if time not in times:
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

                title = post.title
                if len(title) > 256:
                    title = title[:253] + '...'

                value = f'[view]({post.shortlink}){tab}{post.subreddit_name_prefixed}'

                embed.add_field(name=title, value=value, inline=False)

            await ctx.send(embed=embed)

        except Exception: # Catch 'em all, there's too many

            await ctx.send('No such subreddit!')


def setup(client):
    client.add_cog(Reddit(client))
