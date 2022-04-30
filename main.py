import os
import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup
from time import time
from datetime import datetime
from replit import db
from keep_alive import keep_alive

url = 'https://draftsim.com/mtg-arena-codes/'

client = discord.Client()

def scrape():
  try:
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')
    eles =  soup.body \
                .find(class_='body_wrap') \
                .find(class_='page_wrap') \
                .find(class_='page_content_wrap page_paddings_yes') \
                .find(class_='content_wrap') \
                .find(class_='content') \
                .article \
                .find(class_='post_content') \
                .find('ul') \
                .find_all('li')
    if eles:
      return [ele.text for ele in eles]
  except Exception:
    pass

@tasks.loop(hours=1)
async def find_codes():
  codes = scrape()

  # Construct message to send
  try: # Attempt to construct message as an embed
    embed = discord.Embed(title='MTGA Codes',
                          url='https://myaccounts.wizards.com/account',
                          timestamp=datetime.utcnow())
    if codes: # Add codes as fields
      embed.description = 'New codes found!'
      for pair in codes:
        code,reward = pair.split(' – ')
        embed.add_field(name=code,value=reward)
    else: # if no codes, show error
      embed.description = 'An error occurred. Codes could not be found.'
    embed.set_footer(text='Last updated')
    content = None
  except Exception: # Construct message as plain text if there is an error
    timestamp = '\n\nLast updated: <t:{}>'.format(int(time()))
    if codes: content = '\n'.join(codes)
    else:     content = 'An error occured. Codes could not be found.'
    content += timestamp
    embed = None

  # Display the message
  if 'msg' in db and codes == db['codes']:
    # Send new message if codes are new
    msg = await channel.fetch_message(db['msg'])
    await msg.edit(content=content,embed=embed)
  else: # Change timestamp of prevous message if codes are old
    db['codes'] = codes
    msg = await channel.send(content=content,embed=embed)
    db['msg'] = msg.id

@client.event
async def on_ready():
  print('Logged in as `{0.user}`'.format(client))
  global channel
  id = int(os.environ['CHANNEL'])
  channel = client.get_channel(id)
  find_codes.start()

keep_alive()
client.run(os.environ['TOKEN'])
