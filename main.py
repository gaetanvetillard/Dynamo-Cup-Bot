import discord
from sqlalchemy import create_engine, Table, Column, Integer, Float, MetaData, select, desc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
import os


DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
MODE = "duo"
CATEGORY = 720675067532673038
MAX = 50
REGISTER_CHANNEL = 719956101109645442
WELCOME_CHANNEL = 837048983745462342
LEADERBOARD_CHANNEL = 837025557081882680
with open("tops.json") as f:
    TOP = json.load(f)
    f.close()


intents = discord.Intents().all()
client = discord.Client(intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="!register"))


engine = create_engine(os.environ.get('DATABASE_URL'))
db = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Leaderboard(db):
    __tablename__ = 'leaderboard'

    id = Column(Integer, primary_key=True)
    team = Column(Integer)
    score = Column(Integer)
    games = relationship("Game", back_populates="team")


class Game(db):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("leaderboard.id"))
    team = relationship("Leaderboard", back_populates="games")
    top = Column(Integer)
    kills = Column(Integer)
    points = Column(Integer)


db.metadata.create_all(engine)

def update_leaderboard(guild):
    all_teams = session.query(Leaderboard).order_by(desc(Leaderboard.score)).all()
    _message = ""
    for team in all_teams:
        #Find players in this team 
        players = ""
        for member in guild.members:
            for role in member.roles:
                if role.name.split('-')[-1] == str(team.team):
                    if players == "":
                        players += member.name
                    else:
                        players += " & " + member.name
        if players == "":
            players = f"{MODE.capitalize()} {team.team}"
        _message += f'__{all_teams.index(team) + 1} - {team.score} points :__ **{players}**\n'
    return _message



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
            all_channels = [channel for channel in category.channels if MODE in channel.name]
            i=1
            position = None
            if len(all_channels) > 0 and len(all_channels) <= MAX:
                for channel in all_channels:
                    if int(channel.name.split('-')[-1]) != i:
                        position = channel.position - 1
                        n=i
                        break
                    i+=1
                n=i
                if position == None:
                    position = channel.position
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
            
            new_embed = discord.Embed(title="Votre équipe a bien été inscrite.", colour=discord.Colour.green())
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
                        if channel.name == role.name:
                            channel_to_delete = channel

            if team_to_delete != None and channel_to_delete != None:
                new_embed = discord.Embed(title="Votre équipe a bien été désinscrite.", description=f"Désinscription du {role.name.capitalize()}.", colour=discord.Colour.orange())
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

    if message.channel.category_id == CATEGORY:
        if message.content.startswith('$result add') and message.author.guild_permissions.administrator:
            if len(message.content.split(' ')) == 4:
                team_num = message.channel.name.split('-')[-1]
                top = message.content.split(' ')[2]
                kills = message.content.split(' ')[3]
                points = TOP[top] + int(kills)
                #check team in leaderboard
                team = session.query(Leaderboard).filter_by(team=team_num).first()
                if team == None:
                    team = Leaderboard(
                        team=team_num,
                        score=0,
                    )
                    session.add(team)
                game_result = Game(
                    team=team,
                    top=int(top),
                    kills=int(kills),
                    points=points
                )
                session.add(game_result)
                #Update score on leaderboard
                team.score += points
                session.commit()
                await message.add_reaction('✅')

        if message.content.startswith('$leaderboard') and message.author.id == 331405760544112641 and message.channel.id == LEADERBOARD_CHANNEL:
            await message.channel.send("Classement :")

        if message.content.startswith('$reset_leaderboard') and message.author.id == 331405760544112641 and message.channel.id == LEADERBOARD_CHANNEL:
            for table in reversed(db.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
            await message.channel.add_reaction('✅')

        if message.content.startswith('$update_leaderboard'):
            msg = update_leaderboard(message.guild)
            await message.channel.purge(limit=15)
            await message.channel.send(f'**Classement :**\n\n{msg}')


    if message.author.guild_permissions.administrator:
        if message.content.startswith('!status'):
            new_embed = discord.Embed(title="Status", description=f":green_circle: Bot {discord.Status.online}", colour=discord.Colour.red())
            new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=new_embed)

        if message.content.startswith('!clear'):
            if len(message.content.split(' ')) == 2:
                amount = message.content.split(' ')[-1]
                try:
                    amount = int(amount)
                except ValueError:
                    amount = 50
            else:
                amount = 50
            await message.channel.purge(limit=amount)
            new_embed = discord.Embed(title="Success.", description=f"{amount} messages are deleted.", colour=discord.Colour.green())
            new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=new_embed)




@client.event
async def on_member_join(member):
    _mention = f"<@!{member.id}>"
    _guild_name = member.guild
    embed = discord.Embed(title="Nouveau membre sur le discord !", description=f"Bienvenue {_mention} sur le serveur de la {_guild_name} !", colour=discord.Colour.gold())
    await client.get_channel(WELCOME_CHANNEL).send(embed=embed)



client.run(DISCORD_TOKEN)