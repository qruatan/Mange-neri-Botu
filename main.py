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
TARGET_ROLE_ID = 1470102696152535186 # Etiketlenecek rol ID

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

@tasks.loop(time=manga_time)
async def daily_manga():
    channel = bot.get_channel(MANGA_CHAN)
    data = await get_data('manga')
    
    if channel and data:
        # Verileri güvenli şekilde alıyoruz (.get kullanımı)
        title = data.get('title') or data.get('title_english') or "Başlık Bulunamadı"
        url = data.get('url', 'https://myanimelist.net')
        
        images = data.get('images', {})
        jpg_data = images.get('jpg', {})
        img_url = jpg_data.get('large_image_url')

        embed = discord.Embed(
            title=f"📖 Günün Mangası: {title}", 
            url=url, 
            color=discord.Color.green()
        )
        if img_url:
            embed.set_image(url=img_url)
        
        await channel.send(embed=embed)

@bot.command(name="test")
async def test_komutu(ctx):
    # Bu komut 18:00'i beklemeden fonksiyonu manuel tetikler
    await ctx.send("⏳ Günlük paylaşım görevi manuel olarak başlatılıyor...")
    try:
        # Fonksiyonunun adı tam olarak neyse onu yazmalısın (Örn: daily_anime veya daily_recommendation)
        await daily_manga() 
        await ctx.send("✅ Görev başarıyla çalıştırıldı!")
    except Exception as e:
        await ctx.send(f"❌ Bir hata oluştu: {e}")

@bot.event
async def on_ready():
    print(f'Manga Botu {bot.user} aktif!')
    if not daily_manga.is_running():
        daily_manga.start()

print(f"Token yüklendi mi: {TOKEN is not None}")

bot.run(TOKEN)