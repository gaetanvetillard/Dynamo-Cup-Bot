import discord
from sqlalchemy import create_engine, Table, Column, Integer,String, MetaData, select, desc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
import os
from sqlalchemy.sql.sqltypes import BigInteger


DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
MODE = "duo"
CATEGORY = 720675067532673038
MAX = 50
REGISTER_CHANNEL = 719956101109645442
WELCOME_CHANNEL = 837048983745462342
LEADERBOARD_CHANNEL = 838367990621274133
ADMIN_COMMANDS = 837636396263931916
LEADERBOARD_MSG = 838377697783840799
with open("tops.json") as f:
    TOP = json.load(f)
    f.close()


intents = discord.Intents().all()
client = discord.Client(intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name="!register"))


engine = create_engine(os.environ.get('DATABASE'))
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

class LeaderboardID(db):
    __tablename__ = 'leaderboardID'

    id = Column(Integer, primary_key=True)
    msg_id = Column(BigInteger)

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
        else:
            players = f"**{players}** *({MODE.capitalize()} {team.team})*"
        _message += f'__{all_teams.index(team) + 1} - **{team.score}** points :__ {players}\n'
    return _message

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        first_embed = discord.Embed(title="Commandes disponibles pour @everyone", description="Liste des commandes disponible pour tous.", colour=discord.Colour.blue())
        first_embed.add_field(name="!register", value="Permet de vous inscrire sur le tournois.", inline=False)
        first_embed.add_field(name="!unregister", value="Permet de vous désinscrire si vous êtes dans une équipe.", inline=False)
        first_embed.add_field(name="!slots", value="Affiche le nombre d'équipes inscrites", inline=False)
        first_embed.add_field(name="!match_history", value="Affiche votre historique de parties (à utiliser dans le salon dédié à **votre équipe**)", inline=False)
        second_embed = discord.Embed(title="Commandes disponibles pour les administrateurs", description="Liste des commandes disponible pour les administrateurs.", colour=discord.Colour.purple())
        second_embed.add_field(name="$status", value="Affiche le statut du bot.", inline=False)
        second_embed.add_field(name="$clear", value="$clear {LIMIT} : efface les 50 derniers ou jusqu'à la limite indiquée.", inline=False)
        second_embed.add_field(name="$leaderboard", value="Initialise et affiche le classement (à utiliser dans le salon **admin**).", inline=False)
        second_embed.add_field(name="$update_leaderboard", value="Met à jour manuellement le classement (à utiliser dans le salon **admin**).", inline=False)
        second_embed.add_field(name="$reset_leaderboard", value="Réinitialise le classement (à utiliser dans le salon **admin**).", inline=False)
        second_embed.add_field(name="$add result {TOP} {KILLS}", value="Ajoute un résultat (à utiliser dans le salon de chaque **équipe**).", inline=False)
        second_embed.add_field(name="$points {CHANNEL}", value="Affiche le barème des points dans le channel souhaité (à utiliser dans le salon **admin**).", inline=False)
        second_embed.add_field(name="$delete_channels", value="Supprime tous les salons des équipes (à utiliser dans le salon **admin**).", inline=False)
        second_embed.add_field(name="$delete_roles", value="Supprime tous les rôles des équipes (à utiliser dans le salon **admin**).", inline=False)
        second_embed.add_field(name="$reset_pseudos", value="Réinitialise les pseudos (à utiliser dans le salon **admin**).", inline=False)
        await message.channel.send(embed=first_embed)
        await message.channel.send(embed=second_embed)


    if message.channel.id == REGISTER_CHANNEL:
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
                        print()
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
            return
    
        elif message.content.startswith("!slots"):
            guild = message.guild
            category = guild.get_channel(CATEGORY)
            all_channels = [channel.name for channel in category.channels if MODE in channel.name]
            new_embed = discord.Embed(title="Slots", description=f"Il y a : {len(all_channels)} {MODE}s", colour=discord.Colour.gold())
            new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=new_embed)
            return

        elif message.content.startswith("!unregister"):
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
            return


    if message.channel.category_id == CATEGORY:
        if message.content.startswith('$result add') and message.author.guild_permissions.administrator:
            if len(message.content.split(' ')) == 4:
                team_num = message.channel.name.split('-')[-1]
                top = message.content.split(' ')[2]
                kills = message.content.split(' ')[3]
                if int(top) > 0 and int(top) <= 100 and int(kills) < 50:
                    try:
                        points = TOP[top] + int(kills)
                    except KeyError:
                        points = int(kills)
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
                    content_ = update_leaderboard(message.guild)
                    try:
                        # m = await message.guild.get_channel(LEADERBOARD_CHANNEL).fetch_message(session.query(LeaderboardID).filter_by(id=1).first().msg_id)
                        m = await message.guild.get_channel(LEADERBOARD_CHANNEL).fetch_message(LEADERBOARD_MSG)
                    except:
                        await message.add_reaction('❌')
                        await message.channel.send("Vous devez d'abord initialiser le classement.")
                        return
                    await m.edit(content=f'**Classement :**\n\n{content_}')
                    await message.add_reaction('✅')
                else:
                    await message.add_reaction('❌')
            else:
                await message.add_reaction('❌')
            return

        elif message.content.startswith('$result add'):
            await message.channel.send('Vous devez être administrateur pour pouvoir ajouter des résultats.')
            await message.add_reaction('❌')
            return

        if message.content.startswith('!match_history'):
            try:
                team_num = int(message.channel.name.split('-')[-1])
            except:
                return
            #Find Team in leaderboard Database
            team = session.query(Leaderboard).filter_by(team=team_num).first()
            if team == None or len(team.games) == 0:
                embed = discord.Embed(title="Historique des matchs :", description=f"Aucun match trouvé pour l'équipe {MODE} {team_num}.")
                embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif len(team.games) > 0:
                content = f"__**Historique de l'équipe {team.team}**__\n\n"
                for game in team.games:
                    content += f"__Game n° {team.games.index(game) + 1} :__ TOP {game.top} - {game.kills} Kills => {game.points}pts\n"
                embed = discord.Embed(title="Historique des matchs :", description=content)
                embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            return


    if message.author.guild_permissions.administrator:
        if message.content.startswith('$status'):
            new_embed = discord.Embed(title="Status", description=f":green_circle: Bot {discord.Status.online}", colour=discord.Colour.red())
            new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=new_embed)
            return

        elif message.content.startswith('$clear'):
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
            bot_msg = await message.channel.send(embed=new_embed)
            await bot_msg.delete()
            return

    if message.author.guild_permissions.administrator and message.channel.id == ADMIN_COMMANDS:
        if message.content.startswith('$leaderboard') and message.author.id == 331405760544112641:
            msg = await message.guild.get_channel(LEADERBOARD_CHANNEL).send("**Classement :**")
            leaderboard_id = session.query(LeaderboardID).filter_by(id=1).first()
            if leaderboard_id == None:
                add_id = LeaderboardID(msg_id = msg.id)
                session.add(add_id)
            else:
                leaderboard_id.msg_id = str(msg.id)
            session.commit()
            await message.add_reaction('✅')
            return

        elif message.content.startswith('$reset_leaderboard') and message.author.id == 331405760544112641:
            all_teams = session.query(Leaderboard).all()
            for team in all_teams:
                session.delete(team)
            all_games = session.query(Game).all()
            for game in all_games:
                session.delete(game)
            session.commit()
            await message.add_reaction('✅')
            return

        elif message.content.startswith('$update_leaderboard'):
            content_ = update_leaderboard(message.guild)
            try:
                # m = await message.guild.get_channel(LEADERBOARD_CHANNEL).fetch_message(session.query(LeaderboardID).filter_by(id=1).first().msg_id)
                await message.guild.get_channel(LEADERBOARD_CHANNEL).fetch_message(LEADERBOARD_CHANNEL)
            except:
                await message.add_reaction('❌')
                await message.channel.send("Vous devez d'abord initialiser le classement.")
                return
            await m.edit(content=f'**Classement :**\n\n{content_}')
            await message.add_reaction('✅')
            return

        elif message.content.startswith('$create_leaderboard_teams'):
            guild = message.guild
            category = guild.get_channel(CATEGORY)
            all_teams = [int(channel.name.split('-')[-1]) for channel in category.channels if MODE in channel.name]
            for team in all_teams:
                if session.query(Leaderboard).filter_by(team=team).first() == None:
                    team = Leaderboard(
                            team=team,
                            score=0,
                        )
                    session.add(team)
            session.commit()
            await message.add_reaction('✅')
            return

        elif message.content.startswith('$points'):
            if len(message.content.split(' ')) == 2:
                try:
                    channel_id = int(message.content.split(' ')[-1])
                except:
                    try:
                        channel_id = int(message.content.split(' ')[-1][2:-1])
                    except:
                        await message.add_reaction('❌')
                        return
                channel_ = message.guild.get_channel(channel_id)
                content_tops = ""
                for top in TOP:
                    content_tops += f"**Top {top}** : {TOP[top]}pts\n"
                content_kills = "**1 kill** = __1__pts"
                embed = discord.Embed(title="Barème de points", colour=discord.Colour.gold())
                embed.add_field(name="Points par Top", value=content_tops, inline=True)
                embed.add_field(name="Points par Kill", value=content_kills, inline=True)
                await channel_.send(embed=embed)
                await message.add_reaction('✅')

        elif message.content.startswith('$delete_channels'):
            guild = message.guild
            for channel in guild.channels:
                if channel.name.split('-')[0] == MODE or channel.name.split('-')[0] == 'trio':
                    await channel.delete()
            new_embed = discord.Embed(title="Channels are deleted.", colour=discord.Colour.red())
            new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=new_embed)
            return

        elif message.content.startswith('$delete_roles'):
            guild = message.guild
            for role in guild.roles:
                if MODE in role.name:
                    await role.delete()
            new_embed = discord.Embed(title="Roles are deleted.", colour=discord.Colour.red())
            new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=new_embed)
            return

        elif message.content.startswith('$reset_pseudos'):
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
            return

        elif message.content.startswith('$unregister'):
            guild = message.guild
            category = guild.get_channel(CATEGORY)
            player = message.mentions[0]
            team_to_delete = None
            channel_to_delete = None
            for role in player.roles:
                if MODE in role.name:
                    team_to_delete = role
                    for channel in category.channels:
                        if channel.name == role.name:
                            channel_to_delete = channel

            if team_to_delete != None and channel_to_delete != None:
                new_embed = discord.Embed(title="Votre équipe a bien été désinscrite.", description=f"Désinscription du {team_to_delete.name.capitalize()}.", colour=discord.Colour.orange())
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
                new_embed = discord.Embed(title="Error", description=f"{player.mention} n'est dans aucune team.", colour=discord.Colour.red())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=new_embed)
            return

        elif message.content.startswith("$register"):

            try:
                player_1 = message.mentions[0]
                player_2 = message.mentions[1]
        
            except:
                new_embed = discord.Embed(title="Mauvais Format", description="Format: $register @player_1 @player_2", colour=discord.Colour.red())
                new_embed.set_footer(text=f"Host : {message.author}", icon_url=message.author.avatar_url)
                await message.channel.send(embed=new_embed)
                return

            if player_1.id == player_2.id:
                    new_embed = discord.Embed(title="Vous ne pouvez pas jouer en solo !", description="Merci de réessayer.", colour=discord.Colour.red())
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
                        print()
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
            return

@client.event
async def on_member_join(member):
    _mention = f"<@!{member.id}>"
    _guild_name = member.guild
    embed = discord.Embed(title="Nouveau membre sur le discord !", description=f"Bienvenue {_mention} sur le serveur de la {_guild_name} !", colour=discord.Colour.gold())
    await client.get_channel(WELCOME_CHANNEL).send(embed=embed)



client.run(DISCORD_TOKEN)