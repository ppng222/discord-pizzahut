# bot.py
import os
import random
import json
import requests
import asyncio
from io import BytesIO
import discord
from PIL import Image
from discord.ext import commands
from dotenv import load_dotenv
blacklist_servers = [754041601059454987]
size_emojis = ["1️⃣","2️⃣"]
extra_emojis = ["❌","✅"]
number_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣"]
meat_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","➡️"]
veg_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟","➡️"]
crusts = ["1️⃣ Original Pan Pizza", "2️⃣ Hand Tossed Pizza", "3️⃣ Thin 'N Crispy", "4️⃣ Original Stuffed Crust"]
crustSizes = ["1️⃣ Regular Pizza", "2️⃣ Personal Pizza"]
meatList = ["1️⃣ Bacon","2️⃣ Beef","3️⃣ Chicken","4️⃣ Ham","5️⃣ Italian Sausage","6️⃣ Meatball","7️⃣ Pepperoni","8️⃣ Pork"]
vegList = ['1️⃣ Banana Pepper', '2️⃣ Green Bell Peppers', '3️⃣ Green Olives', '4️⃣ Jalapenos', '5️⃣ Mushrooms', '6️⃣ Black Olives', '7️⃣ Red Onions', '8️⃣ Pineapples', '9️⃣ Spinach', '🔟 Tomatoes']
sauceList = ['1️⃣ Classic Marinara','2️⃣ Creamy Garlic Parmesan','3️⃣ Barbeque','4️⃣ Buffalo']
finishList = ['1️⃣ None','2️⃣ Garlic Buttery Blend', '3️⃣ Hut Favorite', '4️⃣ Toasted Parmesan']
crust_resolver = {
  "1️⃣": "pan",
  "2️⃣": "hand_tossed",
  "3️⃣": "thin",
  "4️⃣": "stuffed_crust",
  "5️⃣": "ppp"
}
crust_finish_resolver = {
  "1️⃣": "NoFinish",
  "2️⃣": "GarlicButteryBlend",
  "3️⃣": "HutFavorite",
  "4️⃣": "ToastedParmesan"
}
cheese_resolver = {
  "✅": True,
  "❌": False
}
sauce_resolver = {
  "1️⃣": "Marinara",
  "2️⃣": "CreamyGarlicParm",
  "3️⃣": "BBQ",
  "4️⃣": "Buffalo"
}
meat_resolver = {
	"1️⃣": "Bacon",
	"2️⃣": "Beef",
	"3️⃣": "Chicken",
	"4️⃣": "Ham",
	"5️⃣": "ItalianSausage",
	"6️⃣": "Meatball",
	"7️⃣": "Pepperoni",
	"8️⃣": "Pork"
}
veggie_resolver = {
	"1️⃣": "BananaPepper",
	"2️⃣": "GreenBellPepper",
	"3️⃣": "GreenOlives",
	"4️⃣": "Jalapeno",
	"5️⃣": "Mushroom",
	"6️⃣": "Olives_black",
	"7️⃣": "Onion_red",
	"8️⃣": "Pineapple",
	"9️⃣": "Spinach_Fresh",
	"🔟": "Tomato"
}
pizza_data = json.load(open('ingredients.json','r'))
pizza_presets = json.load(open('pizza_presets.json','r'))

load_dotenv()
TOKEN = os.getenv('token')

def createEmbed(color,title,description):
    return discord.Embed(color=color,title=title,description=description)
def dlPILImage(url):
    imResponse = requests.get(url)
    return Image.open(BytesIO(imResponse.content))
def createPizzaImage(pizzaObject):
    ## gathering the ingredients ##
    crust = pizza_data['crusts'][pizzaObject['crust']][pizzaObject['crust_finish']]
    toppingsList = []
    if pizzaObject['crust'] == 'ppp':
        size = 'ppp'
    else:
        size = 'ML'
    sauce = pizza_data['sauces'][pizzaObject['sauce']][size]
    if pizzaObject['cheese'] == True:
        cheese = pizza_data['cheeses']['mozz'][size]
    elif pizzaObject['cheese'] == "Cum":
        cheese = pizza_data['cheeses']['cum']['ML']
    else:
        cheese = None
    for top in pizzaObject['meattoppings']:
        if top['extra'] == True:
            amount = 'extra'
        else:
            amount = 'reg'
        toppingURL = pizza_data['meats'][top['name']][size][amount]
        toppingsList.append(toppingURL)
    for top in pizzaObject['vegtoppings']:
        if top['extra'] == True:
            amount = 'extra'
        else:
            amount = 'reg'
        toppingURL = pizza_data['veggies'][top['name']][size][amount]
        toppingsList.append(toppingURL)
        
    ## sending the pizza through the oven ##
    baseImage = Image.new('RGBA',(525,525))
    crustIM = dlPILImage(crust)
    sauceIM = dlPILImage(sauce)
    baseImage.alpha_composite(crustIM)
    baseImage.alpha_composite(sauceIM)
    if cheese != None:
        cheeseIM = dlPILImage(cheese)
        baseImage.alpha_composite(cheeseIM)
    for top in toppingsList:
        toppingImage = dlPILImage(top)
        toppingImage = toppingImage.convert('RGBA')
        baseImage.alpha_composite(toppingImage)
    ## the pizza is out of the oven ##
    return baseImage
def createPizzaTopping(name,extra):
    topping = {"name":name,"extra":extra}
    return topping
'''
BOT COMMANDS
'''  
bot = commands.Bot(command_prefix='hut.')  

@bot.command(name='allpresets',help='Looking for all the pizza options?')
async def all_preset(ctx):
    preset_embed = createEmbed(0xFF0000,"Pizza Presets!","Lazy to make your own huh?\n Your pizza preset got a space in it? Surround it with quotes!")
    for presetName in pizza_presets:
      preset = pizza_presets[presetName]
      if preset['show_in_kristens_server'] == False:
          if ctx.guild.id in blacklist_servers:
            continue
          else:
            preset_embed.add_field(name=preset['name'],value=preset['description'],inline=True)
      else:
          preset_embed.add_field(name=preset['name'],value=preset['description'],inline=True)
    await ctx.send(embed=preset_embed)
    return
@bot.command(name='makepreset',help="Want a quick fix?")
async def make_preset(ctx,arg):
    print(arg)
    pizzaObject = pizza_presets[arg]
    pizzaOrder = createPizzaImage(pizzaObject)
    with BytesIO() as image_binary:
        pizzaOrder.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send("*knock knock* Your pizza is here!",file=discord.File(fp=image_binary, filename='image.png'))
    return   
  
@bot.command(name='makerandom',help='Funny combinations!')
async def make_random(ctx):
    pizzaObject = {
      "name": "",
      "description": "",
      "show_in_kristens_server": False,
      "crust": -1,
      "crust_finish": -1,
      "sauce": -1,
      "cheese": -1,
      "meattoppings": [],
      "vegtoppings": []
    }
    pizzaObject['crust'] = crust_resolver[random.choice(number_emojis)]
    pizzaObject['crust_finish'] = crust_finish_resolver[random.choice(number_emojis)]
    pizzaObject['sauce'] = sauce_resolver[random.choice(number_emojis)]
    pizzaObject['cheese'] = random.choice((True, False))
    meatAmount = random.randrange(0,len(list(pizza_data['meats']))-1)
    vegAmount = random.randrange(0,len(list(pizza_data['veggies']))-1)
    meatList = list(meat_resolver)
    vegList = list(veggie_resolver)
    for i in range(meatAmount):
        meatIndex = random.randrange(0,len(meatList)-1)
        meatType = meat_resolver[meatList[meatIndex]]
        extra = random.choice((True, False))
        meatList.pop(meatIndex)
        pizzaObject['meattoppings'].append(createPizzaTopping(meatType,extra))
    for i in range(vegAmount):
        vegIndex = random.randrange(0,len(meatList)-1)
        vegType = veggie_resolver[vegList[vegIndex]]
        extra = random.choice((True, False))
        vegList.pop(vegIndex)
        pizzaObject['vegtoppings'].append(createPizzaTopping(vegType,extra))
    print(pizzaObject)
    pizzaOrder = createPizzaImage(pizzaObject)
    print("hello")
    with BytesIO() as image_binary:
        pizzaOrder.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send("*knock knock* Your pizza is here!",file=discord.File(fp=image_binary, filename='image.png'))
    return
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, id=743862891622694983)
    channel = discord.utils.get(guild.channels, id=743862891622694986)
    await channel.send("THE BOT HAS AWOKEN")
    global pizza_presets
    pizza_presets = json.load(open('pizza_presets.json','r'))
    print("THE BOT HAS AWOKEN")
    return
@bot.command(name='reload')
async def reload(ctx):
    global pizza_presets
    pizza_presets = json.load(open('pizza_presets.json','r'))
    await ctx.send("Presets reloaded!")
    return
@bot.command(name='makepizza',help='Hungry? Customize your own pizza!')
@commands.cooldown(1,60,commands.BucketType.guild)
async def make_pizza(ctx):
    pizzaObject = {
      "crust": -1,
      "crust_finish": -1,
      "sauce": -1,
      "cheese": -1,
      "meattoppings": [],
      "vegtoppings": []
    }
    
    
    
    
    crust_embed = discord.Embed(color=0xe02522,title='Select your crust!',description='Choose from four delicious types of crust')
    crust_embed.add_field(name="Crusts", value='\n'.join(crusts), inline=True)
    mess1 = await ctx.send(embed=crust_embed)
    for emoji in number_emojis:
        await mess1.add_reaction(emoji)
    def check1(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in number_emojis
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check1)
    except TimeoutError:
        newEmbed = createEmbed(0xe02522,"Game timeout","timeout")
        await mess1.edit(embed=newEmbed)
        return
    else:
        newEmbed = createEmbed(0xe02522,"Crust selected","crust !")
        await mess1.edit(embed=newEmbed)
        cache_msg = discord.utils.get(bot.cached_messages, id=mess1.id)
        # find the user reaction #
        pizzaObject['crust'] = reaction.emoji
        await mess1.delete()
    if pizzaObject['crust'] == '1️⃣':
        size_embed = discord.Embed(color=0xe02522,title='Would you like this as a regular or personal pizza?',description='Size don\'t matter here')
        size_embed.add_field(name="Sizes", value='\n'.join(crustSizes), inline=True)
        size_message = await ctx.send(embed=size_embed)
        for emoji in size_emojis:
            await size_message.add_reaction(emoji)
        def checkSize(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in number_emojis
        try:
            reaction, user = await bot.wait_for('reaction_add', check=checkSize)
            pizzaObject['size'] = reaction.emoji
        except TimeoutError:
            return
        else:
            if reaction.emoji == "2️⃣":
                pizzaObject['crust'] = "5️⃣"
            await size_message.delete()
            
    finish_embed = discord.Embed(color=0xe02522,title='Would you like a flavor on your crust?',description='Choose from four types of flavors')
    finish_embed.add_field(name="Flavors", value='\n'.join(finishList), inline=True)
    finishMess = await ctx.send(embed=finish_embed)
    for emoji in number_emojis:
        await finishMess.add_reaction(emoji)
    def check1(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in number_emojis
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check1)
    except TimeoutError:
        newEmbed = createEmbed(0xe02522,"Game timeout","timeout")
        await finishMess.edit(embed=newEmbed)
        return
    else:
        pizzaObject['crust_finish'] = reaction.emoji
        await finishMess.delete()
        
    cheese_embed = createEmbed(0xe02522,"Would you like cheese?","Yummy mozzarella!")    
    cheeseMessage = await ctx.send(embed=cheese_embed) 
    for emoji in extra_emojis:
       await cheeseMessage.add_reaction(emoji)   
    def check1(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in extra_emojis
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check1)
    except TimeoutError:
        newEmbed = createEmbed(0xe02522,"Game timeout","timeout")
        await mess1.edit(embed=newEmbed)
        return
    else:
        pizzaObject['cheese'] = reaction.emoji
        await cheeseMessage.delete()    
        
        
        
        
        
    sauce_embed = createEmbed(0xe02522,"What kinda sauce you want?","Marinara sounds good today")  
    sauce_embed.add_field(name="Sauces", value='\n'.join(sauceList),inline=True)
    sauceMessage = await ctx.send(embed=sauce_embed) 
    for emoji in number_emojis:
       await sauceMessage.add_reaction(emoji)   
    def check1(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in number_emojis
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check1)
    except TimeoutError:
        newEmbed = createEmbed(0xe02522,"Game timeout","timeout")
        await mess1.edit(embed=newEmbed)
        return
    else:
        pizzaObject['sauce'] = reaction.emoji
        await sauceMessage.delete()          
            
          
          
          
          
    meat_embed = discord.Embed(color=0xe02522,title='Choose your meats!',description="Pepperoni is always the classic")
    meat_list_tmp = meatList
    meat_embed.add_field(name="Meats", value='\n'.join(meat_list_tmp),inline=True)
    meatMessage = await ctx.send(embed=meat_embed)
    meat_emoji_tmp = meat_emojis
    for emoji in meat_emoji_tmp:
        await meatMessage.add_reaction(emoji)
    def check2(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in meat_emojis
    meat_loop = True
    while meat_loop:
      meat_topping = {"name":"","extra":False}
      try:
          meatreaction, user = await bot.wait_for('reaction_add', check=check2)
      except TimeoutError:
          newEmbed = createEmbed(0xe02522,"Game timeout","timeout")
          await meatMessage.edit(embed=newEmbed)
          return
      else:
          # find the user reaction #
          if meatreaction.emoji == "➡️":
                meat_loop = False
                await meatMessage.delete()
          else:
                toppingIndex = meat_emoji_tmp.index(meatreaction.emoji)
                meat_emoji_tmp.pop(toppingIndex)
                meat_list_tmp.pop(toppingIndex)
                await meatMessage.delete()
                extra_embed = createEmbed(0xe02522,"Would you like extra?","There's never too much of one topping")
                extraMessage = await ctx.send(embed=extra_embed)
                for emoji in extra_emojis:
                    await extraMessage.add_reaction(emoji)
                def checkExtra(reaction, user):
                    return user == ctx.message.author and str(reaction.emoji) in extra_emojis
                try:
                    reaction, user = await bot.wait_for('reaction_add', check=checkExtra)
                except TimeoutError:
                    newEmbed = createEmbed(0xe02522,"Game timeout","timeout")
                    await extraMessage.edit(embed=newEmbed)
                    return
                else:
                    if reaction.emoji == "✅":
                        meat_topping['extra'] = True
                    meat_topping['name'] = meat_resolver[meatreaction.emoji]
                    pizzaObject['meattoppings'].append(meat_topping)
                    await extraMessage.delete()
                
              
                if len(pizzaObject['meattoppings']) != 1:
                    plural = 's'
                else:
                    plural = ''
                newEmbed = createEmbed(0xe02522,"Choose your meat!","You've chosen {} meat{} so far!".format(len(pizzaObject['meattoppings']),plural))
                newEmbed.add_field(name="Meats", value='\n'.join(meat_list_tmp),inline=True)
                meatMessage = await ctx.send(embed=newEmbed)
                for emoji in meat_emoji_tmp:
                    await meatMessage.add_reaction(emoji)
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
    veg_embed = discord.Embed(color=0xe02522,title='Choose your veggies!',description="Eat your veggies kids!")
    veg_list_tmp = vegList
    veg_embed.add_field(name="Veggies", value='\n'.join(veg_list_tmp),inline=True)
    vegMessage = await ctx.send(embed=veg_embed)
    veg_emoji_tmp = veg_emojis
    for emoji in veg_emoji_tmp:
        await vegMessage.add_reaction(emoji)
    def check2(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in veg_emojis
    veg_loop = True
    while veg_loop:
      veg_topping = {"name":"","extra":False}
      try:
          vegreaction, user = await bot.wait_for('reaction_add', check=check2)
      except TimeoutError:
          newEmbed = createEmbed(0xe02522,"Game timeout","timeout")
          await vegMessage.edit(embed=newEmbed)
      else:
          # find the user reaction #
          if vegreaction.emoji == "➡️":
                veg_loop = False
                await vegMessage.delete()
          else:
                toppingIndex = veg_emoji_tmp.index(vegreaction.emoji)
                veg_emoji_tmp.pop(toppingIndex)
                veg_list_tmp.pop(toppingIndex)
                await vegMessage.delete()
                extra_embed = createEmbed(0xe02522,"Would you like extra?","There's never too much of one topping")
                extraMessage = await ctx.send(embed=extra_embed)
                for emoji in extra_emojis:
                    await extraMessage.add_reaction(emoji)
                def checkExtra(reaction, user):
                    return user == ctx.message.author and str(reaction.emoji) in extra_emojis
                try:
                    reaction, user = await bot.wait_for('reaction_add', check=checkExtra)
                except TimeoutError:
                    newEmbed = createEmbed(0xe02522,"Game timeout","timeout")
                    await extraMessage.edit(embed=newEmbed)
                    return
                else:
                    if reaction.emoji == "✅":
                        veg_topping['extra'] = True
                    veg_topping['name'] = veggie_resolver[vegreaction.emoji]
                    pizzaObject['vegtoppings'].append(veg_topping)
                    await extraMessage.delete()
                
              
                if len(pizzaObject['vegtoppings']) != 1:
                    plural = 's'
                else:
                    plural = ''
                newEmbed = createEmbed(0xe02522,"Choose your veggies!","You've chosen {} veggie{} so far!".format(len(pizzaObject['vegtoppings']),plural))
                newEmbed.add_field(name="Veggies", value='\n'.join(veg_list_tmp),inline=True)
                vegMessage = await ctx.send(embed=newEmbed)
                for emoji in veg_emoji_tmp:
                    await vegMessage.add_reaction(emoji)               
                    
                    
                    
    #so now we need to convert the emojis in the dict to text#
    pizzaObject['crust'] = crust_resolver[pizzaObject['crust']]
    pizzaObject['sauce'] = sauce_resolver[pizzaObject['sauce']]                
    pizzaObject['cheese'] = cheese_resolver[pizzaObject['cheese']]                
    pizzaObject['crust_finish'] = crust_finish_resolver[pizzaObject['crust_finish']] 
    pizzaOrder = createPizzaImage(pizzaObject)
    with BytesIO() as image_binary:
        pizzaOrder.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send("*knock knock* Your pizza is here!",file=discord.File(fp=image_binary, filename='image.png'))
    return
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('Our pizza oven is still warming up, please try again in {:.2f}s'.format(error.retry_after))
                  
bot.run(TOKEN)