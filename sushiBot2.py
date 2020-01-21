'''sushiBot.py plays the miniclip game SushiGoRound.
Assumption: game is open and visible
'''

import pyautogui,time,cv2, threading

play = skip= con = orderRegion= platesRegion = time_end = None
matRoll = 1.4 # mat roll takes 1.5 seconds to complete
sushiImages = ['caliRoll.png','masagoRoll.png', 'onigiri.png','salmonRoll.png']
orders = {'masagoRoll':0, 'caliRoll' : 0, 'onigiri' :0, 'dragonRoll':0, 'unagiRoll' : 0, 'salmonRoll' : 0}
recipe = {'masagoRoll':['rice','nori','masago', 'masago'],
          'caliRoll' : ['rice','nori','masago'],
          'onigiri' :['rice','rice','nori'],
          'dragonRoll':['rice','rice','nori','masago','unagi','unagi'],
          'unagiRoll' : ['rice','rice','nori','masago','salmon','unagi','shrimp'],
          'salmonRoll' : ['rice','nori','salmom','salmon']
          }
inventory = {'shrimp': 5, 'rice' : 10, 'nori' : 10, 'masago' : 10, 'salmon':5, 'unagi':5}
restock = {'phone' : (2213,1500),
    'topping' : (2240,1260),
    'rice'  : (2052, 1318),
    'endCall' : (2228,1440),
    'shrimp' : (1914, 1100),
    'unagi' : (2120,1100),
    'nori' : (1920,1255),
    'salmon' : (1918,1380),
    'masago' : (2150,1260),
    'free' : (1986,1315)
               }
lastOrdered = None # holds the last ordered item until it is delivered, if this item was just ordered, it cannot be ordered
# again for 6 seconds

# functions needed
#makeSushi(sushi) checks if all ingredients are in inventory, makes the sushi roll, and deletes it from the queue.
#if not all ingredients available, calls on orderIngredient() and moves onto the next roll
def makeSushi(sushi):
    global lastOrdered
    print('Trying to make ' + sushi)
    tracker = {'shrimp': 0, 'rice' : 0, 'nori' : 0, 'masago' : 0, 'salmon':0, 'unagi':0}
    makeOrder = True
    for item in recipe[sushi]:
        tracker[item] += 1
        if tracker[item] > inventory[item]:
            print('Can\'t make ' + sushi + ', not enough ' + item)
            makeOrder = False
            if lastOrdered is None: # doesn't try to duplicate orders
                lastOrdered = item
                orderIngredient(item)
    if makeOrder is True:
        print('Making ' + sushi)
        for ingredient in recipe[sushi]:
            pyautogui.click(ingredientsRegion[ingredient][0]+20,ingredientsRegion[ingredient][1]+20, interval = 0.1)
            inventory[ingredient] -= 1
        pyautogui.click(ingredientsRegion['masago'][0]+300,ingredientsRegion['masago'][1]) #clicks on sushi roller
        time.sleep(matRoll)
    orders[sushi] -= 1    #delete sushi from order queue

#orders an ingredient that is out or is limiting for a roll needed to be made
def orderIngredient(ingredient):
    print('Ordering more ' + ingredient)
    #check if we can afford the ingredient by matching gray pixel
    pixel = pyautogui.pixel(restock[ingredient][0],restock[ingredient][1])
    if pixel == (109,123,127) or (ingredient is 'rice' and pixel == (118,83,85)):
        print('Can\'t afford ' + ingredient)
        pyautogui.click(restock['endCall'])
        return
    pyautogui.click(restock['phone'])
    if ingredient == 'rice':
        pyautogui.click(restock[ingredient],interval = 0.15)
        pyautogui.click(restock[ingredient],interval = 0.15)
    else:
        pyautogui.click(restock['topping'],interval = 0.15)
        pyautogui.click(restock[ingredient], interval = 0.15)
    pyautogui.click(restock['free'], interval = 0.15)
    lastOrdered = ingredient
    # takes 6 seconds for item to be delivered
    timer = threading.Timer(6.5,delivered, args = [ingredient])
    timer.start()

#Actual playing of the game
def playFun():
    global inventory, time_end
    inventory = {'shrimp': 5, 'rice' : 10, 'nori' : 10, 'masago' : 10, 'salmon':5, 'unagi':5} # reset inventory for each round
    print('Playing the game!')
    time.sleep(3)
    time_end = time.time() + 60*3 + 6 # restuarant opens for 3 mins before closing
    while time_end> time.time():
        clearPlates()
        findOrders()
        for order in orders.keys():
            while orders[order] > 0:
                makeSushi(order)

def delivered(ingredient):
    global lastOrdered
    if ingredient in ['rice','nori','masago']:
        inventory[ingredient] += 10
    else:
        inventory[ingredient]+=5
    lastOrdered = None
    print(ingredient + ' is delivered. Inventory : ')
    print(inventory)
    
#finds and clicks the continue button during start up
def continue_():
    global con
    while con is None:
        con = pyautogui.locateOnScreen('continue.png',grayscale = True, confidence=0.7)
        print('Finding Continue Button')
    if isinstance(con,tuple) is True:
        pyautogui.click(con[0],con[1])
            
#find orders function
def findOrders():
    global orderRegion, orders
    print('Finding Orders...')
 # only function during playFun() that doesn't use the mouse. Trying to utilize mouse and always have it moving
    plates = threading.Thread(target = clearPlates)
    orders = {'masagoRoll':0, 'caliRoll' : 0, 'onigiri' :0, 'dragonRoll':0, 'unagiRoll' : 0, 'salmonRoll' : 0}
    plates.start()
    for roll in sushiImages:
        sushiType = roll[:len(roll)-4]
        orderImage = pyautogui.locateAllOnScreen(roll, region = orderRegion, grayscale = True, confidence = 0.97)
        for i in orderImage:
            orders[sushiType] = orders.get(sushiType) + 1
    print('Current Orders: ')
    print(orders)

#plate appearance location is hardcoded on a 4k monitor, with the game on a Chrome Browser maximized
def clearPlates():
    print('Clearing Plates...')
    for count in range(6):
        pyautogui.click(960 + count*250, 1100)
        

#START OF PROGRAM RUN SEQUENCE
# find region where the orders will appear before the game actually starts
while orderRegion is None:
    print('Finding Order Region')
    orderRegion = pyautogui.locateOnScreen('ordersRegion.png', confidence=0.8)
 

#finds the play button at the start of the game
while play is None:
    play = pyautogui.locateOnScreen('play.png', confidence=0.8)
    print('Finding Play Button')
    if isinstance(play,tuple) is True:
        pyautogui.click(play[0],play[1])
        break

#TODO find region where all the ingredients will appear
    
continue_()

#finds where the ingredients are located on the screen
ingredientsRegion = {'shrimp': None, 'rice' : None, 'nori' : None, 'masago' : None, 'salmon':None, 'unagi':None}
for key in ingredientsRegion.keys():
    print('Finding Ingredients Region for ' + key)
    while ingredientsRegion.get(key) is None:
        ingredientsRegion[key] = pyautogui.locateOnScreen(key + '.png', grayscale = True, confidence = 0.9)
          
#finds the skip button to start the game
while skip is None:
    skip = pyautogui.locateOnScreen('skip.png', confidence=0.9)
    print('Finding Skip Button')
    if isinstance(skip,tuple) is True:
        pyautogui.click(skip[0],skip[1])
        break
continue_()

playFun()



            


