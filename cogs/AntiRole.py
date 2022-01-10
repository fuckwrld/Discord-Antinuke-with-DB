import discord, pymongo, datetime
from discord.ext import commands

mongoClient = pymongo.MongoClient(MONGO_URL_HERE)
db = mongoClient.get_database(DB_NAME_HERE).get_collection(COLLECTION_NAME_HERE)

class AntiRole(commands.Cog):
    def __init__(self, client, db):
        self.client = client
        self.db = db

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        whitelistedUsers = self.db.find_one({ "guild_id": role.guild.id })["whitelisted"]
        async for i in role.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.role_create): 
            if i.user.id in whitelistedUsers or i.user in whitelistedUsers:
                return
            await i.user.ban()
            return

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        whitelistedUsers = self.db.find_one({ "guild_id": role.guild.id })["whitelisted"]
        async for i in role.guild.audit_logs(limit=1, after=datetime.datetime.now() - datetime.timedelta(minutes = 2), action=discord.AuditLogAction.role_delete):
            if i.user.id in whitelistedUsers or i.user in whitelistedUsers:
                return
            await i.user.ban()
            return