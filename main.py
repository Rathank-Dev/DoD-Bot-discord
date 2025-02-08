import discord
from discord.ext import commands
import yt_dlp as youtube_dl

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Set up ffmpeg options
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

# Music command to play YouTube audio
@bot.command()
async def play(ctx, url: str):
    # Connect to voice channel
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_channel = await channel.connect()
        
        # Use yt-dlp to extract the audio URL
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['formats'][0]['url']
        
        # Play the audio in the voice channel
        voice_channel.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))

        await ctx.send(f"Now playing: {info['title']}")
    else:
        await ctx.send("You need to join a voice channel first!")
 #welcome   
@bot.event
async def on_member_join(member):
    # Get the welcome channel (change 'welcome' to your channel's name)
    welcome_channel = discord.utils.get(member.guild.text_channels, name='welcome')  # Modify to your channel's name
    
    if welcome_channel:
        # Get the user's profile creation date and join date
        creation_date = member.created_at.strftime("%B %d, %Y")
        join_date = member.joined_at.strftime("%B %d, %Y")
        
        # Send a welcome message with profile info
        await welcome_channel.send(
            f"🎉 **Welcome to the server, {member.mention}!** 🎉\n"
            f"👤 **Username:** {member.name}\n"
            f"📅 **Account Created On:** {creation_date}\n"
            f"📅 **Joined Server On:** {join_date}\n"
            f"**We're so happy to have you here!** 😄\n"
            f"✨ Let's make this a great time together! ✨"
        )
    else:
        print("No welcome channel found.")

# Ticket panel message ID
ticket_message_id = None  # You will set the ID after sending the message in Discord

# Create a new ticket when the user reacts with the emoji
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    # Check if the reaction is on the ticket panel message
    if reaction.message.id == ticket_message_id:
        if str(reaction.emoji) == '🎫':  # 🎫 emoji to open a ticket
            guild = reaction.message.guild
            category = discord.utils.get(guild.categories, name="Tickets")  # Ensure you have a 'Tickets' category

            # Create a new private text channel for the user
            ticket_channel = await guild.create_text_channel(
                f'ticket-{user.name}', 
                category=category, 
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    user: discord.PermissionOverwrite(read_messages=True),
                }
            )

            await ticket_channel.send(f"Hello {user.mention}, welcome to your ticket! A support team member will be with you shortly.")

            # Let the user know their ticket was created
            await user.send(f"Your ticket has been created: {ticket_channel.mention}")
        
        elif str(reaction.emoji) == '❌':  # ❌ emoji to close the ticket
            # Check if the reaction is on a ticket channel
            if isinstance(reaction.message.channel, discord.TextChannel):
                if reaction.message.channel.name.startswith('ticket-'):
                    await reaction.message.channel.delete()  # Delete the ticket channel

# Command to create a ticket panel message (once)
@bot.command()
async def create_ticket_panel(ctx):
    global ticket_message_id
    # Send a message in a designated channel (e.g., #ticket-panel) with reaction options
    ticket_panel_channel = discord.utils.get(ctx.guild.text_channels, name='ticket-panel')  # Make sure the channel exists
    
    if ticket_panel_channel:
        message = await ticket_panel_channel.send(
            "Click the 🎫 to open a new support ticket, or ❌ to close the ticket."
        )
        
        # Add reactions to the message
        await message.add_reaction('🎫')  # React with a 🎫 emoji to create a ticket
        await message.add_reaction('❌')  # React with a ❌ emoji to close the ticket

        ticket_message_id = message.id
        await ctx.send("Ticket panel has been created!")
    else:
        await ctx.send("Ticket panel channel not found. Please create a #ticket-panel channel.")
        
# Command to stop the music
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Music stopped and disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to any voice channel!")

bot.run('YOUR_BOT_TOKEN')
