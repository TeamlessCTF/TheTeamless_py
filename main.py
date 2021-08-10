import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import MemberConverter
import requests
from json import loads, dumps
from time import time, sleep
import datetime
from os import system, getenv

bot = commands.Bot(
	command_prefix="t.",
	case_insensitive=True,
	help_command=None
)

token = getenv("TOKEN")

ctfproposals = 855779318118613012
# ctfproposals = 872949630957129758

reactions = {}
f = open("ctfs.json")
reactions = loads(f.read())
f.close()

@bot.event 
async def on_ready():
	print(f"Bot: {bot.user} logged in!")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=" over TeamlessCTF"))

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="TheTeamless", color=0x308a20)
    embed.add_field(name="t.interestpoll", value=f"Sends a poll in <#{ctfproposals}> to gauge interest in a CTF.", inline=False)
    embed.add_field(name="t.createctf", value="Creates a reaction role, channels, and manages permissions for a CTF.", inline=False)
    embed.add_field(name="t.reminder", value="Sets a reminder for a CTF. Pings the role 1 week, day, and hour before the CTF starts.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def interestpoll(ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == msg.channel
    
    await ctx.send("Which CTF is this poll for? **Alternatively, enter a CTFtime link! (eg, <https://ctftime.org/event/1258>)**")
    ctf_choice = await bot.wait_for("message", check=check)
    ctf_choice = ctf_choice.content
    if "ctftime.org" in ctf_choice:
        j = requests.get(f"https://ctftime.org/api/v1/events/?limit=100&start={int(time())}&finish={int(time()) * ord(':thonk:'[0])}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "}).text
        j = loads(j)
        for x in j:
            if str(ctf_choice.split("/")[4]) == str(x['id']):
                await ctx.send(f"Adding **{x['title']}**")
                c = bot.get_channel(ctfproposals)
                embed = discord.Embed(title=f"{x['title']}", description=x['description'], color=0x8c0000)
                embed.add_field(name="Starts: ", value=datetime.datetime.fromisoformat(x['start']).strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
                embed.add_field(name="Ends: ", value=datetime.datetime.fromisoformat(x['finish']).strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
                embed.add_field(name="URL: ", value=x['url'], inline=False)
                embed.add_field(name="Weight: ", value=x['weight'], inline=False)
                embed.set_thumbnail(url=x['logo'])
                msg = await c.send(embed=embed)
                await msg.add_reaction("👍")
                await msg.add_reaction("👎")
                #thread the message (using http requests)

                headers = {
                    'Authorization': f'Bot {token}',
                    'Content-Type': 'application/json',
                }

                data = f'{{"name":"{x["title"]}", "auto_archive_duration": 1440}}'

                r = requests.post(f'https://discord.com/api/v9/channels/{ctfproposals}/messages/{msg.id}/threads', headers=headers, data=data)
                print(r.text)
                return

        await ctx.send("Couldn't find that CTF!")
        return

    await ctx.send('When does the CTF start?')
    start = await bot.wait_for("message", check=check)
    await ctx.send("When does the CTF end?")
    end = await bot.wait_for("message", check=check)
    await ctx.send("What is the CTF url?")
    url = await bot.wait_for("message", check=check)
    name = ctf_choice
    await ctx.send("Please provide a description of the CTF.")
    desc = await bot.wait_for("message", check=check)
    await ctx.send(f"Adding **{name}**")
    c = bot.get_channel(ctfproposals)
    embed = discord.Embed(title=name, description=desc.content, color=0x8c0000)
    embed.add_field(name="Starts: ", value=start.content, inline=False)
    embed.add_field(name="Ends: ", value=end.content, inline=False)
    embed.add_field(name="URL: ", value=url.content, inline=False)
    msg = await c.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    #thread the message (using http requests)
    



@bot.command()
@commands.has_permissions(manage_roles=True)
async def createctf(ctx):
    global reactions
    def check(msg): 
        return msg.author == ctx.author and msg.channel == msg.channel
    await ctx.send(f"Enter the message ID of a proposal in <#{ctfproposals}> or supply the event name.")
    id = await bot.wait_for("message", check=check)
    id = id.content
    if id.isdigit():
        c = bot.get_channel(ctfproposals)
        message = await c.fetch_message(id)
        emb = message.embeds[0]
        roleid = await ctx.guild.create_role(name=emb.title, color=0x992d22)
        roleid = roleid.id
        sent = await c.send(f"React to this message with <:rooYay:870785531536113784> to join this CTF and get the **<@&{roleid}>** role!", embed=emb)
        id = sent.id
        await sent.add_reaction("<:rooYay:870785531536113784>")
        await message.delete()

        category = await ctx.guild.create_category(emb.title)
        print(category)
        await category.set_permissions(get(ctx.guild.roles, id=roleid), read_messages=True, send_messages=True, connect=True, speak=True)
        await category.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)
        await ctx.guild.create_text_channel("info", category=get(ctx.guild.categories, name=emb.title))
        await ctx.guild.create_text_channel("discussion", category=get(ctx.guild.categories, name=emb.title))
        await ctx.guild.create_text_channel("___unsolved___", category=get(ctx.guild.categories, name=emb.title))
        await ctx.guild.create_text_channel("___solved___", category=get(ctx.guild.categories, name=emb.title))
    else:
        await ctx.send('When does the CTF start?')
        start = await bot.wait_for("message", check=check)
        await ctx.send("When does the CTF end?")
        end = await bot.wait_for("message", check=check)
        await ctx.send("What is the CTF url?")
        url = await bot.wait_for("message", check=check)
        name = id
        await ctx.send("Please provide a description of the CTF.")
        desc = await bot.wait_for("message", check=check)
        embed = discord.Embed(title=name, description=desc.content, color=0x8c0000)
        embed.add_field(name="Starts: ", value=start.content, inline=False)
        embed.add_field(name="Ends: ", value=end.content, inline=False)
        embed.add_field(name="URL: ", value=url.content, inline=False)
        roleid = await ctx.guild.create_role(name=name, color=0x992d22)
        roleid = roleid.id
        await ctx.guild.create_category(name)
        c = bot.get_channel(ctfproposals)
        await c.send(embed=embed)

        category = await ctx.guild.create_category(name)
        await category.set_permissions(get(ctx.guild.roles, id=roleid), read_messages=True, send_messages=True, connect=True, speak=True)
        await category.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)
        await ctx.guild.create_text_channel("info", category=get(ctx.guild.categories, name=name))
        await ctx.guild.create_text_channel("discussion", category=get(ctx.guild.categories, name=name))
        await ctx.guild.create_text_channel("___unsolved___", category=get(ctx.guild.categories, name=name))
        await ctx.guild.create_text_channel("___solved___", category=get(ctx.guild.categories, name=name))

    with open("ctfs.json", "r") as f:
        raw = f.read()
        j = loads(raw)
    j[str(id)] = roleid

    with open("ctfs.json", 'w') as f:
        f.write(dumps(j))
    

    f = open("ctfs.json")
    reactions = loads(f.read())
    f.close()

    
    
@bot.event
async def on_raw_reaction_add(event):
    if str(event.message_id) not in reactions.keys():
        return
    if event.emoji.id != 870785531536113784: 
        return
    user = event.member
    role = get(user.guild.roles, id=reactions[str(event.message_id)])
    await user.add_roles(role)

bot.run(token)