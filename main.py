import discord
import os
import requests
import json
from keep_alive import keep_alive

client = discord.Client()

urlApiLink = 'https://www.virustotal.com/vtapi/v2/url/report'
channelBanList = []

# linkFound returns TRUE if a link is in the message; else FALSE
def linkFound(message):
  container = message.rsplit(" ")

  for word in container:
    if word.startswith("http") or word.startswith("www"):
      return True
  
  return False

# linkString cuts the link down to a readable version for VirusTotal
def linkString(message):
  container = message.rsplit(" ")

  for word in container:
    if word.startswith("http") :
      wordList = word.split("/")
      return wordList[2]
    elif word.startswith("www"):
      wordList = word.split("/")
      return wordList[0]

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  #Start of Message Handler
  if message.author == client.user:
    return
  
  ################### Bot Switch For Channels #########################
  if(message.content.startswith("$stop")):
    if message.channel.name not in channelBanList:
      await message.channel.send("Stopping scans in " + message.channel.name)
      channelBanList.append(message.channel.name)
    
  elif message.content.startswith("$run"):
    if message.channel.name in channelBanList:
      await message.channel.send("Running scans in " + message.channel.name)
      channelBanList.remove(message.channel.name)

  if(message.channel.name in channelBanList):
    return


  ############################ URL Scans ###################################
  #Scans Link through VirusTotal; Returns any detected positive results and prints to console
  if(linkFound(message.content)):
    try:
      link = linkString(message.content)
      
      params = {'apikey': os.environ['Key'], 'resource': link}
      response = requests.get(urlApiLink, params=params)
      response_json = json.loads(response.content)
      positiveEngineList = []

      for i in response_json["scans"]:
          if(response_json["scans"][i]["detected"] == True):
            positiveEngineList.append(i)

      if(response_json["positives"] > 0):
        await message.channel.send("CAUTION: " + str(response_json["positives"]) + " out of " + str(response_json["total"]) + " vendors flagged this URL as malicious: " + str(positiveEngineList))

      if(response_json["positives"] <= 0):
        await message.channel.send("Safe URL")
      
      return

    except:
      pass

keep_alive()
client.run(os.environ['BotToken'])