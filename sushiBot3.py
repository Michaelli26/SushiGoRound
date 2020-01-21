'''sushiBot.py plays the miniclip game SushiGoRound.
Assumption: game is open and visible
'''

import pyautogui,time,cv2, threading, Xlib.threaded

pyautogui.PAUSE = 0.15
play = skip= con = orderRegion= platesRegion = time_end = time_start = None
preBuyOn = False
matRoll = 1.4 # mat roll takes 1.5 seconds to complete
sushiImages = ['caliRoll.png','masagoRoll.png', 'onigiri.png','salmonRoll.png','shrimpRoll.png', 'unagiRoll.png']
orders = { 'caliRoll' : 0, 'masagoRoll':0,'onigiri' :0, 'dragonRoll':0, 'unagiRoll' : 0, 'salmonRoll' : 0, 'shrimpRoll':0}
recipe = {'masagoRoll':['rice','nori','masago', 'masago'],
          'caliRoll' : ['rice','nori','masago'],
          'onigiri' :['rice','rice','nori'],
          'dragonRoll':['rice','rice','nori','masago','unagi','unagi'],
          'unagiRoll' : ['rice','rice','nori','masago','salmon','unagi','shrimp'],
          'salmonRoll' : ['rice','nori','salmon','salmon'],
          'shrimpRoll' : ['rice','nori','shrimp','shrimp']
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
ordered = [] # holds the last ordered item until it is delivered, if this item was just ordered, it cannot be ordered
# again for 6 seconds

roundTime = [3,4,5]

# functions needed
#makeSushi(sushi) checks if all ingredients are in inventory, makes the sushi roll, and deletes it from the queue.
#if not all ingredients available, calls on orderIngredient() and moves onto the next roll
def makeSushi(sushi):
    global ordered
    print('Trying to make ' + sushi)
    tracker = {'shrimp': 0, 'rice' : 0, 'nori' : 0, 'masago' : 0, 'salmon':0, 'unagi':0}
    makeOrder = True
    for item in recipe[sushi]:
        tracker[item] += 1
        if tracker[item] > inventory[item]:
            print('Can\'t make ' + sushi + ', not enough ' + item + '.')
            makeOrder = False
            if item not in ordered: # doesn't try to duplicate orders
                orderIngredient(item)
            return False
    if makeOrder is True:
        print('Making ' + sushi)
        for ingredient in recipe[sushi]:
            pyautogui.click(ingredientsRegion[ingredient][0]+20,ingredientsRegion[ingredient][1]+20, interval = 0.1)
            inventory[ingredient] -= 1
        pyautogui.click(ingredientsRegion['masago'][0]+300,ingredientsRegion['masago'][1]) #clicks on sushi roller
        clearPlates()
        #time.sleep(matRoll)
        orders[sushi] -= 1    #delete sushi from order queue



#orders an ingredient that is out or is limiting for a roll needed to be made
def orderIngredient(ingredient):
    global ordered, inventory
    if ingredient in ordered:
        print('Just bought ' + ingredient)
        return
    print('Ordering more ' + ingredient + '. Current inventory ')
    print(inventory)
    pyautogui.click(restock['phone'])
    if ingredient == 'rice':
        pyautogui.click(restock[ingredient],interval = 0.1)
        pixel = pyautogui.pixel(restock[ingredient][0],restock[ingredient][1])
        #check if we can afford the ingredient by matching gray pixel
        if pixel == (118,83,85):
            print('Can\'t afford ' + ingredient)
            pyautogui.click(restock['endCall'])
            return
        else:
            pyautogui.click(restock[ingredient],interval = 0.1)
    else:
        pyautogui.click(restock['topping'],interval = 0.1)
        pixel = pyautogui.pixel(restock[ingredient][0],restock[ingredient][1])
            #check if we can afford the ingredient by matching gray pixel
        if pixel == (109,123,127):
            print('Can\'t afford ' + ingredient)
            pyautogui.click(restock['endCall'])
            return
        pyautogui.click(restock[ingredient], interval = 0.1)
    pyautogui.click(restock['free'], interval = 0.1)
    ordered.append(ingredient)
    # takes 6 seconds for item to be delivered
    timer = threading.Timer(6,delivered, args = [ingredient])
    timer.start()

#Actual playing of the game
def playFun():
    global inventory, time_end, time_start, roundTime, ordered, orders
    timer = roundTime[int(input('Enter round (1,2,3...): \n'))-1]
    inventory = {'shrimp': 5, 'rice' : 10, 'nori' : 10, 'masago' : 10, 'salmon':5, 'unagi':5} # reset inventory for each round
    ordered = []
    orders = { 'caliRoll' : 0, 'masagoRoll':0,'onigiri' :0, 'dragonRoll':0, 'unagiRoll' : 0, 'salmonRoll' : 0, 'shrimpRoll':0}
    print('Playing the game!')
    time_start = time.time()
    time_end = time.time() + 60*timer + 6 # restuarant opens for x(changes by round) mins before closing
    time.sleep(3.5)
    while time_end> time.time():
        clearPlates()
        # try to make any orders that were skipped because there were not enough ingredients
        preBuy()
        clearPlates()
        clearPlates()
        clearPlates()
        findOrders()
        clearPlates()
        for order in orders.keys():
            for count in range(orders[order]):
                makeSushi(order)


def delivered(ingredient):
    global ordered
    if ingredient in ['rice','nori','masago']:
        inventory[ingredient] += 10
    else:
        inventory[ingredient]+=5
    ordered.remove(ingredient)
    print(ingredient + ' is delivered. Inventory : ')
    print(inventory)
    print('Recently ordered list : ', end = '')
    print(ordered)
    
#finds and clicks the continue button during start up
def continue_():
    global con
    while con is None:
        con = pyautogui.locateOnScreen('continue.png',grayscale = True, confidence=0.7)
        print('Finding Continue Button')
    if isinstance(con,tuple) is True:
        pyautogui.click(con[0],con[1])

# preBuys items if they fall below 3 for rice, nori, and masago
def preBuy():
    global ordered, preBuyOn
    preBuyOn = True
    for item in inventory.keys():
        if item not in ordered:
            if item in ['rice','nori','masago'] and inventory[item] < 4:
                print('Prebuying ' + item)
                orderIngredient(item)
            elif item in ['salmon','shrimp','unagi'] and inventory[item]< 2:
                print('Prebuying ' + item)
                orderIngredient(item)
    preBuyOn = False
            
#find orders function
def findOrders():
    global orderRegion, orders
    print('Finding Orders...')
    if time.time() < time_end - 25 and time.time() > time_start + 10:
        preBuyThread = threading.Thread(target=preBuy)
        preBuyThread.start()
    orders = {'masagoRoll':0, 'caliRoll' : 0, 'onigiri' :0, 'dragonRoll':0, 'unagiRoll' : 0, 'salmonRoll' : 0, 'shrimpRoll':0}
    # only function during playFun() that doesn't use the mouse. Trying to utilize mouse and always have it moving
    plates = threading.Thread(target = clearPlates)
    plates.start()
    for roll in sushiImages:
        sushiType = roll[:len(roll)-4]
        orderImage = pyautogui.locateAllOnScreen(roll, region = orderRegion, grayscale = True, confidence = 0.98)
        for i in orderImage:
            orders[sushiType] = orders.get(sushiType) + 1

    print('Current Orders: ')
    print(orders)

#plate appearance location is hardcoded on a 4k monitor, with the game on a Chrome Browser maximized
def clearPlates():
    global preBuyOn
    if preBuyOn is False:
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



            


