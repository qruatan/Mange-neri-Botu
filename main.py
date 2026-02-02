import discord
from discord.ext import tasks, commands
import aiohttp
import os
from dotenv import load_dotenv
from datetime import time, timezone

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # Manga botu için farklı bir token kullanacaksan burayı değiştir

# AYARLAR
TARGET_CHANNEL_ID = 1467881545699295274 # Manga öneri kanalı ID
TARGET_ROLE_ID = 1467881975791485071 # Etiketlenecek rol ID

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='?', intents=intents) # Anime botuyla karışmasın diye prefixi '?' yaptım

# Her gün saat 18:00'da çalışacak (UTC 15:30)
scheduled_time = time(hour=15, minute=00, tzinfo=timezone.utc)

async def get_manga_recommendation():
    url = "https://api.jikan.moe/v4/random/manga" # Tek fark buradaki 'manga' kelimesi
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['data']
            return None

@tasks.loop(time=scheduled_time)
async def daily_manga():
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel:
        manga = await get_manga_recommendation()
        if manga:
            mention_text = f"<@&{TARGET_ROLE_ID}> Yeni bir manga keşfetme vakti! 📖"
            
            embed = discord.Embed(
                title=f"📖 {manga['title']}",
                description=manga.get('synopsis', 'Açıklama bulunamadı.')[:400] + "...",
                url=manga.get('url'),
                color=discord.Color.green() # Manga için yeşil renk daha şık durabilir
            )
            embed.set_image(url=manga['images']['jpg']['large_image_url'])
            embed.add_field(name="⭐ Puan", value=manga.get('score', 'N/A'), inline=True)
            embed.add_field(name="📚 Bölüm Sayısı", value=manga.get('chapters', 'Devam Ediyor'), inline=True)
            embed.set_footer(text="Keyifli okumalar!")
            
            await channel.send(content=mention_text, embed=embed)

@bot.command(name="mangatest")
async def mangatest(ctx):
    """Manuel manga testi"""
    await daily_manga()
    await ctx.send("✅ Manga önerisi gönderildi!")

@bot.event
async def on_ready():
    print(f'Manga Botu {bot.user} aktif!')
    if not daily_manga.is_running():
        daily_manga.start()

bot.run(TOKEN)