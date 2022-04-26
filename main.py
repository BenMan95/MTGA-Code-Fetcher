import os
import discord
import requests
from bs4 import BeautifulSoup
from replit import db
from discord.ext import tasks
from keep_alive import keep_alive

url = 'https://draftsim.com/mtg-arena-codes/'

client = discord.Client()

def scrape():
  page = requests.get(url)
  soup = BeautifulSoup(page.content,'html.parser')
  return soup.body \
             .find(class_='body_wrap') \
             .find(class_='page_wrap') \
             .find(class_='page_content_wrap page_paddings_yes') \
             .find(class_='content_wrap') \
             .find(class_='content') \
             .article \
             .find(class_='post_content') \
             .find('ul') \
             .text

@tasks.loop(hours=24)
async def events():
  await channel.send('scraping')
  text = scrape()
  if ('codes' not in db or text != db['codes']):
    db['codes'] = text
    await channel.send(text)

@client.event
async def on_ready():
  print('Logged in as `{0.user}`'.format(client))
  global channel
  id = int(os.environ['CHANNEL'])
  channel = client.get_channel(id)
  events.start()

keep_alive()
client.run(os.environ['TOKEN'])
