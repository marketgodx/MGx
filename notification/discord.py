
import requests
import json


def discord_notify(message=''):
    channelID = "" # enable dev mode on discord, right-click on the channel, copy ID
    botToken = ""    # get from the bot page. must be a bot, not a discord app

    baseURL = "https://discordapp.com/api/channels/{}/messages".format(channelID)
    headers = { "Authorization":"Bot {}".format(botToken),
                "User-Agent":"myBotThing (http://some.url, v0.1)",
                "Content-Type":"application/json", }



    POSTedJSON =  json.dumps ( {"content":message} )

    r = requests.post(baseURL, headers = headers, data = POSTedJSON)