import cv2, pyautogui

ingredientsRegion = {'shrimp': None, 'rice' : None, 'nori' : None, 'masago' : None, 'salmon':None, 'unagi':None}
for key in ingredientsRegion.keys():
    print('finding ' + key)
    while ingredientsRegion.get(key) is None:
        ingredientsRegion[key] = pyautogui.locateOnScreen(key + '.png', grayscale = True, confidence = 0.9)

# functions needed
