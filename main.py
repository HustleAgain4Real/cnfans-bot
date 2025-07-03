from pyrogram import Client, filters
import re
import asyncio
from keep_alive import keep_alive

# Lance le serveur pour UptimeRobot
keep_alive()

# Configuration API
api_id = 25231452
api_hash = "8b7348737ab53b259f466c3227dee881"
bot_token = "7048772517:AAEb0F_NU4SBSmX_xNuVlp6-JDyrNBiStbM"

# Canaux
source_channel = "@RealNnnnnn"
target_channel = -1002245551932

# Identifiant affilié CNFANS
your_aff_id = "951431"

app = Client("cnfans_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Test du bot
@app.on_message(filters.command("test") & filters.private)
async def test_cmd(client, message):
    await client.send_message(target_channel, "✅ Test réussi : le bot peut publier ici !")
    await message.reply("Test exécuté ✅")

# Album (media group)
album_buffer = {}

@app.on_message(filters.chat(source_channel) & filters.media_group)
async def handle_album(client, message):
    group_id = message.media_group_id
    if group_id not in album_buffer:
        album_buffer[group_id] = []

    album_buffer[group_id].append(message)
    await asyncio.sleep(2)

    # Another handler might have already processed this group
    if group_id not in album_buffer:
        return

    if len(album_buffer[group_id]) >= 1:
        messages = sorted(album_buffer.pop(group_id), key=lambda m: m.message_id)
        media = []

        # Caption source
        full_text = ""
        for msg in messages:
            if msg.caption:
                full_text = msg.caption
                break

        # Lien affilié CNFANS
        cnfans_match = re.search(r'https?://cnfans\.com/product(?:\?shop_type=weidian)?[^\d]*(\d+)', full_text)
        if cnfans_match:
            product_id = cnfans_match.group(1)
            cnfans_link_with_ref = f"https://cnfans.com/product?platform=WEIDIAN&id={product_id}&ref={your_aff_id}"
        else:
            cnfans_link_with_ref = "https://cnfans.com"

        article_match = re.search(r'🔎Article: ?(.+)', full_text)
        price_match = re.search(r'💵Price ?: ?(.+)', full_text)

        article = article_match.group(1).strip() if article_match else "Non spécifié"
        price = price_match.group(1).strip() if price_match else "Non spécifié"

        final_caption = (
            f"🔎 Prend ton : {article}\n"
            f"💵Price : {price}\n"
            f"🖇 CnFans Link : {cnfans_link_with_ref}\n\n"
            f"🥇 Inscris-toi avec ce lien pour avoir des réductions sur CNFANS 🥇\n"
            f"📌 LIEN d'inscription : https://cnfans.com/register?ref={your_aff_id}"
        )

        for i, msg in enumerate(messages):
            if msg.photo:
                media.append({
                    "type": "photo",
                    "media": msg.photo.file_id,
                    "caption": final_caption if i == len(messages) - 1 else ""
                })
            elif msg.video:
                media.append({
                    "type": "video",
                    "media": msg.video.file_id,
                    "caption": final_caption if i == len(messages) - 1 else ""
                })

        try:
            await client.send_media_group(target_channel, media)
            print("[INFO] Album transféré.")
        except Exception as e:
            print(f"[ERROR] Erreur album : {e}")

# Message simple
@app.on_message(filters.chat(source_channel) & ~filters.media_group)
async def forward_single(client, message):
    text = message.caption or message.text or ""
    print("[DEBUG] Message reçu :", text)

    cnfans_match = re.search(r'https?://cnfans\.com/product(?:\?shop_type=weidian)?[^\d]*(\d+)', text)
    if cnfans_match:
        product_id = cnfans_match.group(1)
        cnfans_link_with_ref = f"https://cnfans.com/product?platform=WEIDIAN&id={product_id}&ref={your_aff_id}"
    else:
        cnfans_link_with_ref = "https://cnfans.com"

    article_match = re.search(r'🔎Article: ?(.+)', text)
    price_match = re.search(r'💵Price ?: ?(.+)', text)

    article = article_match.group(1).strip() if article_match else "Non spécifié"
    price = price_match.group(1).strip() if price_match else "Non spécifié"

    new_text = (
        f"🔎 Prend ton : {article}\n"
        f"💵Price : {price}\n"
        f"🖇 CnFans Link : {cnfans_link_with_ref}\n\n"
        f"🥇 Inscris-toi avec ce lien pour avoir des réductions sur CNFANS 🥇\n"
        f"📌 LIEN d'inscription : https://cnfans.com/register?ref={your_aff_id}"
    )

    try:
        if message.photo:
            await client.send_photo(target_channel, photo=message.photo.file_id, caption=new_text)
            print("[INFO] Photo transférée.")
        elif message.video:
            await client.send_video(target_channel, video=message.video.file_id, caption=new_text)
            print("[INFO] Vidéo transférée.")
        else:
            await client.send_message(target_channel, new_text)
            print("[INFO] Message texte transféré.")
    except Exception as e:
        print(f"[ERROR] Erreur transfert simple : {e}")

# Lancement
app.run()
