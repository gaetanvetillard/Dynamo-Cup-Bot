import discord
from discord import player
from discord.utils import get

DISCORD_TOKEN = 'ODM2NTU5NTg1MjQyMzgyMzY4.YIfw0w.rX5De7MNOedZeD2ZnAE7miv98Vk'
MODE = "duo"
CATEGORY = 720675067532673038
MAX = 50
REGISTER_CHANNEL = 719956101109645442
WELCOME_CHANNEL = 837048983745462342


intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    if message.channel.id == REGISTER_CHANNEL:
        if message.author == client.user:
            return
        
        if message.content.startswith("!register"):

            try:
                player_1 = message.mentions[0]
                player_2 = message.mentions[1]
        
            except:
                new_embed = discord.Embed(title="Mauvais Format", description="Format: !register @player_1 @player_2", colour=discord.Colour.red())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=new_embed)
                return

            if player_1.id == player_2.id:
                    new_embed = discord.Embed(title="Vous ne pouvez pas jouer en solo !", description="Merci de réessayer.", colour=discord.Colour.red())
                    new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                    await message.channel.send(embed=new_embed)
                    return
                
            elif player_1.id != message.author.id and player_2.id != message.author.id:
                new_embed = discord.Embed(title="Vous ne pouvez pas inscrire quelqu'un d'autre que vous.", description="Merci de réessayer.", colour=discord.Colour.red())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=new_embed)
                return

            #player 1
            for role in player_1.roles:
                if role.name.split('-')[0] == MODE:
                    new_embed = discord.Embed(title="Le joueur 1 est déjà dans une équipe !", description="Merci de réessayer.", colour=discord.Colour.red())
                    new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                    await message.channel.send(embed=new_embed)
                    return

            #player 2
            for role in player_2.roles:
                if role.name.split('-')[0] == MODE:
                    new_embed = discord.Embed(title="Le joueur 2 est déjà dans une équipe !", description="Merci de réessayer.", colour=discord.Colour.red())
                    new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                    await message.channel.send(embed=new_embed)
                    return



            guild = message.guild
            category = guild.get_channel(CATEGORY)
            all_channels = [channel for channel in category.channels]
            i=1
            if len(all_channels) > 0 and len(all_channels) <= MAX:
                for channel in all_channels:
                    if int(channel.name[-1]) != i:
                        position = channel.position - 1
                        n=i
                        break
                    i+=1
            else:
                n = 1
                position = 0
            name = MODE + '-' + str(n)
            channel = await guild.create_text_channel(name, category=category, position=position)
            new_role = await guild.create_role(name=name)
            await channel.set_permissions(guild.default_role, send_messages=False, read_messages=False)
            await channel.set_permissions(new_role, send_messages=True, read_messages=True)
            await player_1.add_roles(new_role)
            await player_2.add_roles(new_role)
            try:
                await player_1.edit(nick=f"{MODE.capitalize()} {n} | {player_1.name}")
            except:
                pass
            try:
                await player_2.edit(nick=f"{MODE.capitalize()} {n} | {player_2.name}")
            except:
                pass
            
            new_embed = discord.Embed(title="Votre équipe à bien été inscrite.", colour=discord.Colour.green())
            new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=new_embed)

        if message.content.startswith("!slots"):
            guild = message.guild
            category = guild.get_channel(CATEGORY)
            all_channels = [channel.name for channel in category.channels if MODE in channel.name]
            new_embed = discord.Embed(title="Slots", description=f"Il y a : {len(all_channels)} {MODE}s", colour=discord.Colour.gold())
            new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=new_embed)

        if message.content.startswith("!unregister"):
            guild = message.guild
            category = guild.get_channel(CATEGORY)
            author = message.author
            team_to_delete = None
            channel_to_delete = None
            for role in author.roles:
                if MODE in role.name:
                    team_to_delete = role
                    for channel in category.channels:
                        if channel.name[-1] == role.name[-1] and MODE in channel.name:
                            channel_to_delete = channel

            if team_to_delete != None and channel_to_delete != None:
                new_embed = discord.Embed(title="Votre team a bien été désinscrite.", description=f"Désinscription du {role.name.capitalize()}.", colour=discord.Colour.orange())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                
                for member in guild.members:
                    for role in member.roles:
                        if role.name == team_to_delete.name:
                            try:
                                await member.edit(nick=member.name)
                            except:
                                pass
                await team_to_delete.delete()
                await channel_to_delete.delete()
                await message.channel.send(embed=new_embed)
    
            else:
                new_embed = discord.Embed(title="Impossible de vous désinscrire", description=f"Vous n'êtes dans aucune team.", colour=discord.Colour.red())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=new_embed)
  
        if message.author.guild_permissions.administrator:
            if message.content.startswith('!delete_channels'):
                guild = message.guild
                for channel in guild.channels:
                    if channel.name.split('-')[0] == MODE or channel.name.split('-')[0] == 'trio':
                        await channel.delete()
                new_embed = discord.Embed(title="Channels are deleted.", colour=discord.Colour.red())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=new_embed)

            if message.content.startswith('!delete_roles'):
                guild = message.guild
                for role in guild.roles:
                    if MODE in role.name:
                        await role.delete()
                new_embed = discord.Embed(title="Roles are deleted.", colour=discord.Colour.red())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=new_embed)

            if message.content.startswith('!reset_pseudos'):
                guild = message.guild
                for member in guild.members:
                    if member.nick:
                        if MODE in member.nick.lower():
                            try:
                                await member.edit(nick=member.name)
                            except:
                                pass
                new_embed = discord.Embed(title="Pseudos are reseted.", colour=discord.Colour.red())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=new_embed)

@client.event
async def on_member_join(member):
    embed = discord.Embed(title="Nouveau membre sur le discord !", description=f"Bienvenue {member.mention}", colour=discord.Colour.gold())
    await client.get_channel(WELCOME_CHANNEL).send(embed=embed)


client.run(DISCORD_TOKEN)