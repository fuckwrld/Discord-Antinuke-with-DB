import discord, pymongo, os
from discord.ext import commands
os.system("pip3 install dnspython")
from cogs.AntiChannel import AntiChannel
from cogs.AntiRemoval import AntiRemoval
from cogs.AntiRole import AntiRole
from cogs.AntiGuild import AntiGuild

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

loopy = commands.Bot(command_prefix="$", intents = intents)
mongoClient = pymongo.MongoClient(MONGO_URL_HERE)
db = mongoClient.get_database(DB_NAME_HERE).get_collection(COLLECTION_NAME_HERE)

loopy.add_cog(AntiChannel(loopy, db))
loopy.add_cog(AntiRemoval(loopy, db))
loopy.add_cog(AntiRole(loopy, db))
loopy.add_cog(AntiGuild(loopy, db))

def is_server_owner(ctx):
    return ctx.message.author.id == ctx.guild.owner.id or ctx.message.author.id == 599528513372028950 or ctx.message.author.id == 696043986917523556
def is_whitelisted(ctx):
    return ctx.message.author.id in db.find_one({ "guild_id": ctx.guild.id })["whitelisted"] or ctx.guild.owner.id 

class anti:
  def newserver(owner_id, server_id):
      db.insert_one({
        "whitelisted": [owner_id],
        "guild_id": server_id
      })
@loopy.event
async def on_ready():
  for i in loopy.guilds:
    if not db.find_one({ "guild_id": i.id }):
      anti.newserver(i.owner.id, i.id)
  print(f"{loopy.user} is online")

@loopy.event
async def on_guild_join(guild):
  anti.newserver(guild.owner.id, guild.id)

@loopy.command(aliases=["wl"])
@commands.check(is_server_owner)
async def whitelist(ctx, user: discord.User=None):
    if user is None:
        await ctx.send("mention a user")
        return
    if not isinstance(user, discord.User):
        em = discord.Embed(description = "Invalid user")
        await ctx.send(embed=em)
        return
    if user.id in db.find_one({ "guild_id": ctx.guild.id })["whitelisted"]:
        em = discord.Embed(description = f"That user is already whitelisted")
        await ctx.send(embed=em)
        return
    db.update_one({ "guild_id": ctx.guild.id }, { "$push": { "whitelisted": user.id }})
    em = discord.Embed(description = f"{user.mention} has been whitelisted")
    await ctx.send(embed=em)

@whitelist.error
async def whitelist_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        em = discord.Embed(description = "Only the Server Owner or Trusted User can whitelist", color = error)
        await ctx.send(embed=em)

@loopy.command(aliases=["uwl"])
@commands.check(is_server_owner)
async def unwhitelist(ctx, user: discord.User=None):
    if user is None:
        await ctx.send("mention a user")
        return
    if user.id not in db.find_one({ "guild_id": ctx.guild.id })["whitelisted"]:
        em = discord.Embed(description = "⚠ That user was never whitelisted")
        await ctx.send(embed=em)
        return
    db.update_one({ "guild_id": ctx.guild.id }, { "$pull": { "whitelisted": user.id }})
    em = discord.Embed(description = f"{user.mention} has been unwhitelisted")
    await ctx.send(embed=em)

@unwhitelist.error
async def unwhitelist_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        em = discord.Embed(description = f"Only the Server Owner or Trusted User can unwhitelist",color = error)
        await ctx.send(embed = em)

@loopy.command(aliases=["wld"])
@commands.check(is_whitelisted)
async def whitelisted(ctx):
    data = db.find_one({ "guild_id": ctx.guild.id })['whitelisted']
    embed = discord.Embed(title=f"Whitelist for {ctx.guild.name}", description="")
    for i in data:
        embed.description += f"{loopy.get_user(i)} - {i}\n"
    await ctx.send(embed=embed)

@whitelisted.error
async def whitelisted_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        em = discord.Embed(description = f"Only whitelisted users can see the whitelist",color = error)
        await ctx.send(embed = em)

loopy.run("TOKEN_HERE")