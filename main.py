import discord
import json
from discord.ext import commands, tasks
from discord.ext.commands import cooldown, BucketType, CommandOnCooldown
import os
import random
import keep_alive
import aiohttp
import asyncio

from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

intents = discord.Intents.all()

client = commands.Bot(command_prefix=".", intent=intents, case_insensitive=True)
client.remove_command("help")

#start
@client.event
async def on_ready():
    print("The bot is ready to go!")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".help"))
    send_meme.start()

#task loop area
@tasks.loop(minutes=1)
async def send_meme():
    subreddit = ['memes','dankmeme']
    subredditt = random.choice(subreddit)
    try:
        for i in client.guilds:
            guild = i
            if int(guild.id) == 749855517127737496:
                channel = guild.get_channel(806741919240945704)
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://www.reddit.com/r/{subredditt}/new.json?sort=hot,") as data:
                        res = await data.json()
                        choose = res['data']['children'] [random.randint(0, 25)]
                        title = choose['data']['title']
                        standard = 'https://www.reddit.com'
                        lin = choose['data']['permalink']
                        newlink = standard + lin
                        embed = discord.Embed(description= f'[{title}]({newlink})')
                        embed.set_image(url= choose['data']['url'] )
                        likes = choose['data']['ups']
                        replies = choose['data']['num_comments']
                        embed.set_footer(text = f'👍 {likes} | 💬 {replies}')
                        await channel.send(embed=embed)
    except Exception as e:
        print(f'an error occured in memesfordankememe {e}')

#ping command
@client.command()
async def ping(ctx):
	await ctx.send(f'Pong! :ping_pong: `{round(client.latency * 1000)}ms`')

#donate command
@client.command()
async def donate(ctx, timer=None, winners=None, requirements=None,*, prize=None):
	if timer == None:
		await ctx.send("Please specify the timer of the giveaway next time! Usage: `.donate (time) (no of winners) (requirement) (prize)`")
		return

	if winners == None:
		await ctx.send("Please specify the number of winners of the the giveaway next time! Usage: `.donate (time) (no of winners) (requirement) (prize)`")
		return

	if requirements == None:
		await ctx.send("Please specify the requirement for the giveaway next time, It can be `None` if not required! Usage: `.donate (time) (no of winners) (requirement) (prize)`")
		return

	if prize == None:
		await ctx.send("Please specify the prize of the giveaway next time! Usage: `.donate (time) (no of winners) (requirement) (prize)`")
		return

	channel = client.get_channel(808929255526367252)
	log = client.get_channel(810815279952822302)
	em = discord.Embed(title="GIVEAWAY Dontation Request!", description=f"Sponser: <@!{ctx.author.id}>\nTimer: {timer}\nWinners: {winners}\nRequriement: {requirements}\nPrize: {prize}\n")
	em.set_thumbnail(url="https://media.tenor.com/images/ba3ec917b6414b01fa85d33979336864/tenor.gif")

	e = await channel.send(embed=em)
	await e.add_reaction("✅")
	await e.add_reaction("❎")

	await log.send(f"{ctx.author} has made a GIVEAWAY donation request with arguemtents below-:\n\nTimer: {timer}\nWinners: {winners}\nRequriement: {requirements}\nPrize: {prize}")

	await ctx.send("Successfully sent your giveaway request! Please wait for any online staff to review it! We will notify you when we will be done.")
    x = client.get_channel(808929255526367252)
    await x.send("<@&806507393772027904>")

#event command
@client.command()
async def event(ctx):
    m = None
    p = None
    await ctx.send("Please provide the event instructions like what will we do in it? Please be as much detailed as possible!")

    try:
      msg = await client.wait_for(
        "message",
        timeout = 15,
        check = lambda message: message.author == ctx.author and message.channel == ctx.channel)

      if msg:
          m = msg.content
          await ctx.send("Please provide the prize of the event!")

          try:
            msg = await client.wait_for(
              "message",
              timeout = 15,
              check = lambda message: message.author == ctx.author and message.channel == ctx.channel)

            if msg:
                p = msg.content
                em = discord.Embed(title="Event Request!", description=f"Requester: <@!{ctx.author.id}>\nEvent Info: **{m}**\nEvent Prize: **{p}**\n")
                em.set_image(url="https://i.pinimg.com/originals/3f/a8/8c/3fa88cee7fa27307ab85339aa6513f31.gif")
                logs = client.get_channel(810815257949241368)
                channel = client.get_channel(806507498139811860)

                message = await channel.send(embed=em)
                await channel.send("<@&806507395412000788>")
                await message.add_reaction("✅")
                await message.add_reaction("❎")

                await logs.send(f"Event Request by **{ctx.author}**!\n\nEvent Info: **{m}**\nEvent Prize: **{p}**")

          except asyncio.TimeoutError:
              await ctx.send("You didn't answer in time!")

    except asyncio.TimeoutError:
        await ctx.send("You didn't answer in time!")

    await ctx.send("Successfully added your request to the Events channel! Staff will verify it soon please wait! We will Dm you about it as soon as possible!")

#invites command
@client.command()
async def invites(ctx, usr: discord.Member = None):
    if usr == None:
       user = ctx.author
    else:
       user = usr
    total_invites = 0
    for i in await ctx.guild.invites():
        if i.inviter == user:
            total_invites += i.uses
    await ctx.send(f"{user.name} has invited {total_invites} member{'' if total_invites == 1 else 's'}!")

#revoke command
@client.command()
@commands.has_permissions(administrator=True)
async def revoke(ctx):
  for invite in await ctx.author.guild.invites():
      await invite.delete()

  await ctx.send("Successfully done!")

#open_lvl function
async def open_lvl(user):
    users = await get_lvl_data()

    if str(user.id) in users:
        return False

    else:
        users[str(user.id)] = {}
        users[str(user.id)]["level"] = 1
        users[str(user.id)]["experience"] = 0

    with open("level.json", "w") as f:
        json.dump(users,f,indent=4)
    return True

#get_lvl_data function
async def get_lvl_data():
    with open("level.json", "r") as f:
        users = json.load(f)

    return users

#add_experience function
async def add_experience(user, exp):
    users = await get_lvl_data()

    users[str(user.id)]["experience"] += exp

    with open("level.json", "w") as f:
        json.dump(users, f, indent=4)

#level_up function
async def level_up(user):
    users = await get_lvl_data()

    experience = users[str(user.id)]["experience"]
    lvl_start = users[str(user.id)]["level"]
    lvl_end = int(experience ** (1/4))

    if lvl_start < lvl_end:
        ch = client.get_channel(810038166786277387)
        await ch.send(f"Congrats {user.mention}! You have leveled up to level {lvl_end}! Keep going!\n")
        users[str(user.id)]["level"] = lvl_end
        with open("level.json", "w") as f:
            json.dump(users, f, indent=4)

#levelon_open function
async def levelon_open(server):
    users = await levelon_data()

    if str(server.id) in users:
        return False

    else:
        users[str(server.id)] = {}
        users[str(server.id)]["levelon"] = "off"

    with open("levelon.json", "w") as f:
        json.dump(users,f,indent=4)
    return True

#levelon_data function
async def levelon_data():
    with open("levelon.json", "r") as f:
        users = json.load(f)

    return users

#on_message event
@client.event
async def on_message(message):
    await levelon_open(message.guild)
    users = await levelon_data()
    server = message.guild

    if users[str(server.id)]["levelon"] == "on":
        if message.author.bot == True:
            return

        await open_lvl(message.author)
        await add_experience(message.author, 5)
        await level_up(message.author)

    await client.process_commands(message)

#levelsettings
@client.command()
@commands.has_permissions(manage_channels=True)
async def levelsettings(ctx, mode = None):
    syntax = "```yml\nSyntax: .levelsettings (mode)\nExample Usage: .levelsettings on```"

    if mode == None:
        embed = discord.Embed(title=":negative_squared_cross_mark: Please specify the mode! The mode can only be `on`/`off`\n\n", description=syntax, color=discord.Color.red())
        await ctx.send(embed=embed)
        return     

    if mode.lower() != "on" and mode.lower() != "off":
        embed = discord.Embed(title=":negative_squared_cross_mark: The mode arguement can only be `on`/`off`\n\n", description=syntax, color=discord.Color.red())
        await ctx.send(embed=embed)
        return  

    await levelon_open(ctx.guild)
    users = await levelon_data()

    server = ctx.guild

    if users[str(server.id)]["levelon"] == "on" and mode.lower() == "on":
        embed = discord.Embed(title=":negative_squared_cross_mark: The levelling system is already on!\n\n", description=syntax, color=discord.Color.red())
        await ctx.send(embed=embed)
        return  

    if users[str(server.id)]["levelon"] == "off" and mode.lower() == "off":
        embed = discord.Embed(title=":negative_squared_cross_mark: The levelling system is already off!\n\n", description=syntax, color=discord.Color.red())
        await ctx.send(embed=embed)
        return  

    users[str(server.id)]["levelon"] = mode.lower()

    with open("levelon.json", "w") as f:
        json.dump(users, f, indent=4)

    await ctx.send(f"Successfully changed the levelsettings mode to `{mode.lower()}`")

#level command
@client.command()
async def level(ctx, member: discord.Member = None):
    await levelon_open(ctx.guild)
    users = await levelon_data()
    server = ctx.guild

    if users[str(server.id)]["levelon"] == "on":
        if member == None:
            member = ctx.author

        level = Image.open("level.png")

        asset = member.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)

        pfp = pfp.resize((128,127))

        level.paste(pfp, (105,34))

        await open_lvl(member)
        users = await get_lvl_data()

        draw = ImageDraw.Draw(level)
        font = ImageFont.truetype("level.ttf", 40)

        l = users[str(member.id)]["level"]
        e = users[str(member.id)]["experience"]

        draw.text((355, 75), f": {member.name}", (0, 0, 0), font=font)
        draw.text((232, 180), f": {l}", (0, 0, 0), font=font)
        draw.text((220, 242), f": {e}", (0, 0, 0), font=font)

        level.save("lev.png")

        await ctx.send(file=discord.File("lev.png"))

        return

    await ctx.send("The leveling system is currently off! Inorder to use it turn it on!")

#rank command
@client.command(aliases=["lb"])
async def leaderboard(ctx, x = 3):
    syntax = "```yml\nSyntax: .leaderboard (number)\nExample Usage: .leaderboard 3```"

    if x <= 0:
        embed = discord.Embed(title=":negative_squared_cross_mark: The number can't be less than or equal to 0\n\n", description=syntax, color=discord.Color.red())
        await ctx.send(embed=embed)
        return     

    await levelon_open(ctx.guild)
    users = await levelon_data()
    server = ctx.guild

    if users[str(server.id)]["levelon"] == "off":
        await ctx.send("The leveling system is currently off! Inorder to use it turn it on!")
        return

    users = await get_lvl_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["experience"] + 0
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(title=f"Top {x} experienced people", description="This is decided on the basis of the experience they have!", color=discord.Color.green())
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = ctx.guild.get_member(int(id_))
        name = member.name
        em.add_field(name=f"{index}. {name}", value=f"{amt}", inline=False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed=em)

#help command
@client.command()
async def help(ctx):
    embed = discord.Embed(title="Help Menu\n\n", description="`.donate (time) (winners) (requirement) (prize)`: Sends a donation request to the donations channel\n\n`.event`: Send a event request to the event-donations channel!\n\n`.invites (user)`: See the number of members invited by the user\n\n`.leaderboard (amount)`: See the leaderboard of the most xp earned by people\n\n`level (user)` See the specified user's levelling profile\n\n`levelsettings (mode)`: Change the mode of the levelling system to either on / off\n\n`ping`: See the client's latency\n\n`revoke`: Revoke all the invites from the server using this command\n\n`.vouch (user)`: Vouch for a user!\n\n`.vouches (user)`: See how many vouches does that user have!\n\n", color=ctx.author.color)
    await ctx.send(embed=embed)

#open_vouch funtion
async def open_vouch(user):
    users = await get_vouch_data()

    if str(user.id) in users:
        return False

    else:
        users[str(user.id)] = {}
        users[str(user.id)]["vouches"] = 0

    with open("vouch.json","w") as f:
        json.dump(users, f, indent=4)
    return True

#get_vouch_data function
async def get_vouch_data():
    with open("vouch.json","r") as f:
        users = json.load(f)

        return users

#vouch command
@client.command()
@cooldown(1, 60, BucketType.user)
async def vouch(ctx, member: discord.Member = None):
    syntax = "```yml\nSyntax: .vouch (member)\nExample Usage: .vouch @Atom```"

    if member == None:
        embed = discord.Embed(title=":negative_squared_cross_mark: Please specify a member you want to vouch for next time\n\n", description=syntax, color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if member == ctx.author:
        embed = discord.Embed(title=":negative_squared_cross_mark: You can't vouch for yourself?!\n\n", description=syntax, color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    await open_vouch(member)
    users = await get_vouch_data()
    users[str(member.id)]["vouches"] += 1
    with open("vouch.json","w") as f:
        json.dump(users, f, indent=4)

    await ctx.send("Successfully done!")  

#vouch error
@vouch.error
async def vouch_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"You need to wait ``{error.retry_after:,.2f}`` seconds to use that command again.")

#vouches command
@client.command()
async def vouches(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    await open_vouch(member)
    users = await get_vouch_data()
    vouchess = users[str(member.id)]["vouches"]

    await ctx.send(f"{member.name} has {vouchess} vouches.")

#load command
@client.command()
async def load(ctx, extension):
    if ctx.author.id == 586844180681195530:
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f"Succesfully loaded {extension}!")
        return

    await ctx.send("You don't have permission to use that command!")

#unload command
@client.command()
async def unload(ctx, extension):
    if ctx.author.id == 586844180681195530:
        client.unload_extension(f'cogs.{extension}')
        await ctx.send(f"Succesfully unloaded {extension}!")
        return

    await ctx.send("You dont have permission to use that command!")

#reload command
@client.command()
async def reload(ctx, extension):
    if ctx.author.id == 586844180681195530:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f"Succesfully reloaded {extension}")
        return

    await ctx.send("You dont have permission to use that command!")

#run area
keep_alive.keep_alive()
token=os.environ.get('Token')
client.run(token)
