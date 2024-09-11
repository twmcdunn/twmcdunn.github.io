import pyautogui
from pyscript import document
from pyscript import display

display("HELLO FROM MAIN")

try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        display(positionStr, end='')
        display('\b' * len(positionStr), end='', flush=True)
except KeyboardInterrupt:
    display('\n')
    
