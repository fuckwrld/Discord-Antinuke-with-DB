import discord, pymongo, datetime
from discord.ext import commands

mongoClient = pymongo.MongoClient(MONGO_URL_HERE)
db = mongoClient.get_database(DB_NAME_HERE).get_collection(COLLECTION_NAME_HERE)

class AntiRemoval(commands.Cog):
    def __init__(self, client, db):
      self.client = client
      self.db = db

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
      whitelistedUsers = self.db.find_one({ "guild_id": member.guild.id })["whitelisted"]
      async for i in guild.audit_logs(limit=1, after=datetime.datetime.now()-datetime.timedelta(minutes = 2), action=discord.AuditLogAction.ban):
        if i.user.id in whitelistedUsers or i.user in whitelistedUsers:
          return
      await i.user.ban()
      return

    @commands.Cog.listener()
    async def on_member_remove(self, member):
      whitelistedUsers = self.db.find_one({ "guild_id": member.guild.id })["whitelisted"]
      async for i in member.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.ban):
        if i.user.id in whitelistedUsers or i.user in whitelistedUsers:
          return
      await i.user.ban()
      return