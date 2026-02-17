import discord
from discord.ext import commands
import json
import os
import re

TOKEN = os.getenv("DISCORD_TOKEN") 
DATA_FILE = "teams.json"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f)

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def valid_team_name(name):
    return bool(re.fullmatch(r"[A-Z]{1,8}", name))


@bot.group(invoke_without_command=True)
async def team(ctx):
    await ctx.send("Available commands: join, leave, leaderboard")


@team.command()
async def join(ctx, team_name: str):
    team_name = team_name.upper()

    if not valid_team_name(team_name):
        return await ctx.send("Team names must be UPPERCASE and max 8 characters.")

    data = load_data()
    user_id = str(ctx.author.id)

    if user_id in data["users"]:
        return await ctx.send("You are already in a team. Leave first.")

    data["users"][user_id] = {
        "team": team_name,
        "original_nick": ctx.author.display_name
    }

    save_data(data)

    try:
        await ctx.author.edit(
            nick=f"{ctx.author.display_name} #TEAM {team_name}"
        )
    except:
        pass

    embed = discord.Embed(
        title="Team Joined",
        description=f"{ctx.author.mention} joined **{team_name}**!",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


@team.command()
async def leave(ctx):
    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data["users"]:
        return await ctx.send("You are not in a team.")

    original_nick = data["users"][user_id]["original_nick"]

    del data["users"][user_id]
    save_data(data)
    try:
        await ctx.author.edit(nick=original_nick)
    except:
        pass

    embed = discord.Embed(
        title="Team Left",
        description=f"{ctx.author.mention} left their team.",
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)

@team.command()
async def leaderboard(ctx):
    data = load_data()

    if not data["users"]:
        return await ctx.send("No teams yet.")

    counts = {}

    for user in data["users"].values():
        team = user["team"]
        counts[team] = counts.get(team, 0) + 1

    sorted_teams = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    description = ""
    for team, count in sorted_teams:
        description += f"**{team}** — {count} members\n"

    embed = discord.Embed(
        title="Team Leaderboard",
        description=description,
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)


bot.run(TOKEN)
