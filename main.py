#import pyautogui
from pyscript import document
from pyscript import display
from pyscript import window
from js import DOMParser
#from pyodide.ffi.wrappers import add_event_listener
import pitch
import game
from pyodide.http import open_url
from pyodide.ffi.wrappers import set_interval
from pyodide.ffi.wrappers import clear_interval
import time
import random
from threading import Lock
from threading import Thread
import time

#from music21 import roman


#display("HELLO FROM MAIN")
#display(game.Interval(0,2).qualityName)
app = None
appWidth = 800
appHeight = 800


accidental = 0
cMajorScale = [0,2,4,5,7,9,11]
letters = ["C","D","E","F","G","A","B"]
notes = []
letterName = None
mouseX = 0
mouseY = 0
myGame = None
speechText = None
tokenLevel = 3
emeraldLevel = 4
levelNum = 0
maestro = None
instructions = None
def draw_staffs():
    global app
    url = "./g2.svg"
    doc = DOMParser.new().parseFromString(
        open_url(url).read(), "image/svg+xml"
    )
    node = doc.documentElement

    url = "./b.svg"
    doc = DOMParser.new().parseFromString(
        open_url(url).read(), "image/svg+xml"
    )
    bassCleffnode = doc.documentElement

    for grandStaff in range(3):
        gs = document.createElementNS("http://www.w3.org/2000/svg","svg")
        gs.setAttribute("id","grandStaff" + str(grandStaff))
        for trebBass in range(2):
            staff = document.createElementNS("http://www.w3.org/2000/svg","svg")
            linesAndSpacecs = 10
            if trebBass == 0:
                linesAndSpaces = 11
            for ln in range(linesAndSpaces):
                y = 160 + 5 * ln + trebBass * 65 + grandStaff * 185
                
                #add six extra line/spaces above treble staves
                if trebBass == 0 and ln == 0:
                    for extraLn in range(7,1,-1):
                        extray = y - extraLn * 5
                        line = document.createElementNS("http://www.w3.org/2000/svg","line")
                        line.setAttribute("stroke-width",1)
                        line.setAttribute("stroke","black")
                        line.setAttribute("x1", 50)
                        line.setAttribute("x2", appWidth - 50)
                        line.setAttribute("y1", extray)
                        line.setAttribute("y2", extray)
                        staff.appendChild(line)
                    myNode = node.cloneNode(True)
                    myNode.setAttribute("height", 54)
                    myNode.setAttribute("y", y)
                    myNode.setAttribute("x", -85)
                    myNode.setAttribute("id","treb"+str(grandStaff))
                    myNode.setAttribute("name","myTreb"+str(grandStaff))
                    app.appendChild(myNode)
                line = document.createElementNS("http://www.w3.org/2000/svg","line")
                line.setAttribute("stroke-width",1)
                if (ln + trebBass) % 2 == 0 and ln != 10:
                    line.setAttribute("stroke","white")
                    line.setAttribute("x1", 50)
                else:
                    line.setAttribute("stroke","black")
                    line.setAttribute("x1", 150)
                line.setAttribute("x2", appWidth - 50)
                line.setAttribute("y1", y)
                line.setAttribute("y2", y)
                staff.appendChild(line)

                if trebBass == 1 and ln == 0:
                    myNode = bassCleffnode.cloneNode(True)
                    myNode.setAttribute("y", y + 4)
                    myNode.setAttribute("x", 50)
                    myNode.setAttribute("id","bass"+str(grandStaff))
                    myNode.setAttribute("name","myBass"+str(grandStaff))
                    app.appendChild(myNode)
                #add six extra line/spaces below bass staves
                if trebBass == 1 and ln == 9:
                    for extraLn in range(1,7):
                        extray = y + extraLn * 5
                        line = document.createElementNS("http://www.w3.org/2000/svg","line")
                        line.setAttribute("stroke-width",1)
                        line.setAttribute("stroke","black")
                        line.setAttribute("x1", 50)
                        line.setAttribute("x2", appWidth - 50)
                        line.setAttribute("y1", extray)
                        line.setAttribute("y2", extray)
                        staff.appendChild(line)
                    
            gs.appendChild(staff)
        app.appendChild(gs)

def display_app(a = None):
    if a is None:
        h = window.screen.height
        w = window.screen.width
        page = document.createElementNS("http://www.w3.org/2000/svg","svg")
        page.setAttribute("id","page")
        page.setAttribute("width",w)
        page.setAttribute("height", h)
        page.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        global app
        app = document.createElementNS("http://www.w3.org/2000/svg","svg")
        app.setAttribute("id","app")
        app.setAttribute("py-mousemove", "mouse_move")
    
        document.body.setAttribute("py-keydown", "key_down")
        document.body.setAttribute("py-keyup", "key_up")
        #app.setAttribute("py-keyup", "key_event")
        app.setAttribute("py-mouseup", "start_game")
        app.setAttribute("width",appWidth)
        app.setAttribute("height", appHeight)
        app.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        app.setAttribute("x", (w/2) - 250)
        app.setAttribute("y", (h/2) - 250)
        #page.appendChild(app)
        app.setAttribute("unselectable", "on")
        document.body.appendChild(app)
    box = document.createElementNS("http://www.w3.org/2000/svg","rect")
    box.setAttribute("width",appWidth)
    box.setAttribute("height",appHeight)
    box.setAttribute("fill","black");
    app.appendChild(box)

    if levelNum >= tokenLevel:
        app.appendChild(game.tokenText)
    if levelNum >= emeraldLevel:
        app.appendChild(game.emeraldText)
    
    url = "./maestro.svg"
    #url = "./conductor/0.svg"
    doc = DOMParser.new().parseFromString(
        open_url(url).read(), "image/svg+xml"
    )
    global maestro
    maestro = doc.documentElement
    maestro.setAttribute("width",200)#667)
    maestro.setAttribute("x",600)
    maestro.setAttribute("y",530)
    
    maestro.setAttribute("id","maestro")
    maestro.setAttribute("name","mrMasetro")

    app.appendChild(maestro)

    global speech
    url = "./speech.svg"
    doc = DOMParser.new().parseFromString(
        open_url(url).read(), "image/svg+xml"
    )
    speech = doc.documentElement
    speech.setAttribute("width",450)#667)
    speech.setAttribute("x",200)#667)
    speech.setAttribute("y",660)#650)
    #app.appendChild(speech)
    speech.setAttribute("id","speech")
    speech.setAttribute("name","speechbubble")

    global speechText
    speechText = document.createElementNS("http://www.w3.org/2000/svg","text")
    speechText.setAttribute("dominant-baseline", "middle")
    speechText.setAttribute("text-anchor","middle")
    speechText.setAttribute("x", "0")
    speechText.setAttribute("y", "0")
    #speechText.textContent = "BOOO!"
    speechText.setAttribute("fill", "black")
    speechText.setAttribute("font-size", "4pt")
    speechText.setAttribute("width","100")
    speech.appendChild(speechText)

    twm = document.createElementNS("http://www.w3.org/2000/svg","text")
    twm.setAttribute("dominant-baseline", "bottom")
    twm.setAttribute("text-anchor","left")
    twm.setAttribute("x", "5")
    twm.setAttribute("y", "795")
    twm.textContent = "Created by TWM"
    twm.setAttribute("fill", "grey")
    twm.setAttribute("font-size", "12pt")
    
    app.appendChild(twm)
    
    draw_staffs()
    global letterName
    letterName = document.createElementNS("http://www.w3.org/2000/svg","text")
    text = document.createTextNode("C")
    letterName.appendChild(text)
    letterName.setAttribute("x", 20)
    letterName.setAttribute("y", 20)
    #letterName.setAttribute("stroke", "white")
    letterName.setAttribute("fill", "white")
    app.appendChild(letterName)
    #display("APP DISPLAYED")
    if a is None:
        global instructions
        instructions = document.createElementNS("http://www.w3.org/2000/svg","image");#document.createElement('img')
        instructions.setAttribute("href","./instructions.png")
        instructions.setAttribute("y", 200)
        instructions.setAttribute("x", 50)
        instructions.setAttribute("width",700)
        #instructions.setAttribute("height",400)
        instructions.setAttribute("id","inst")
        instructions.setAttribute("name","myInst")
        app.appendChild(instructions)

conductors = []
for n in range(11):
    url = "./conductor/" + str(n) + ".svg"
    doc = DOMParser.new().parseFromString(
        open_url(url).read(), "image/svg+xml"
    )
    c = doc.documentElement
    c.setAttribute("width",200)#667)
    c.setAttribute("x",600)#600)
    c.setAttribute("y",125)#530)
    
    c.setAttribute("id","conductor")
    c.setAttribute("name","conduc0r")
    conductors.append(c)


display_app()
myGame = None
startTime = None
def start_game(event):
    app.setAttribute("py-mouseup", "animate")
    global instructions
    global myGame
    global startTime
    global lastAddTime
    instructions.remove()
    myGame = game.Game(app)
    startTime = int(time.time())
    lastAddTime = startTime
#lastAdded = None

par = None
strikes = None
level = None
gameTime = None
levelNames = []
cleared = False
#tokenLevel = 1
def move():
    global myGame
    global cleared
    if game.lost and not cleared:
        maestro_complaint("You lost. (...as expected)")
        cleared = True
        #pitch.lock.acquire()
        #if len(game.usersNotes[game.currentGS]) <= 1:
            #game.currentGS = game.currentGS - 1
        for g in range(3):#range (game.currentGS, -1, -1):
            while len(game.usersNotes[g]) > 1:
                p = game.usersNotes[g].pop(len(game.usersNotes[g]) - 1)
                p.remove()
                if p.myFunc in pitch.funcsInProgress:
                    pitch.funcsInProgress.remove(p.myFunc)
        #pitch.lock.release()
        for g in range (3):
            game.currentGS = g
            for n in range(1, len(myGame.lines[g])):
                p = myGame.lines[g][n]
                p.myGS = g
                game.currentGS = g
                if myGame.try_adding(p):
                    p.animate(app, 400, 10)

        #game.lost = False
        
    for gs in game.usersNotes:
        for n in range(1,len(gs)):
            gs[n].move()

    if not game.token is None and not game.token.frame is None:
        game.token.move()
    if not game.emerald is None and not game.emerald.frame is None:
        game.emerald.move()

    """
    global func

    funSt = "funcs: "
    for f in pitch.funcsInProgress:
        funSt += " " + str(f.parent)
    if func is None:
        func = document.createElementNS("http://www.w3.org/2000/svg","text")
        func.setAttribute("y", 75)
        func.setAttribute("x", 30)
        func.setAttribute("fill", "white")
        app.appendChild(func)
    func.textContent = funSt
    """
    global maestroFram
    f = int(maestroFram)
    if f > 0 and f <= 11:
        conductors[f-1].remove()
    if f <=10:
        app.appendChild(conductors[f])
        maestroFram += 0.4
        if int(maestroFram) > 10:
            app.appendChild(maestro)
    
    global gameTime
    global levelNum
    global par
    global strikes
    if game.won and not game.lost:
        #display("won")
        if levelNum == 9:
            winText = document.createElementNS("http://www.w3.org/2000/svg","text")
            winText.setAttribute("dominant-baseline", "middle")
            winText.setAttribute("text-anchor","middle")
            winText.setAttribute("x", "400")
            winText.setAttribute("y", "400")

            totSec = int(time.time()) - startTime
            totMin = totSec // 60
            totHr = totMin // 60
    
            sec = totSec % 60
            min = totMin % 60
    
            tm = str(totHr).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2)
            
            winText.textContent = "You win! Time: " + tm
            winText.setAttribute("fill", "lime")
            winText.setAttribute("font-size", "24pt")
            app.appendChild(winText)
            maestro_complaint("Congratulations, you've ascended to mediocracy.")
            clear_interval(pitch.aniInter)
            return
        
        for n in range(app.childElementCount):
            c = app.children.item(n)
            if not c is None:
                c.remove()
                
        display_app(app)
        levelNum += 1
        if levelNum == 2:
            #display("MENTIONING TIME")
            maestro_complaint("Did I mention you're being timed?")

        lastCursor = None
        
        game.currentGS = 0
        game.usersNotes = [[],[],[]]
        game.lineFinished = False
        #game.strikes = 0
        game.won = False

        pitch.aniInter = 0
        pitch.ani = False
        pitch.falling = False
        pitch.funcsInProgress = []

        #pitch.lock.release()
                
        myGame = game.Game(app, levelNum)
        par = None
        strikes = None
        gameTime = None
        global tokenLevel
        if levelNum == tokenLevel:
            myGame.add_token()
            game.tokenText = document.createElementNS("http://www.w3.org/2000/svg","text")
            game.tokenText.setAttribute("y", 80)
            game.tokenText.setAttribute("x", 600)
            game.tokenText.textContent = "Gold Tokens: 0";
            game.tokenText.setAttribute("fill", "white")
            app.appendChild(game.tokenText)
        elif levelNum > tokenLevel and random.choice([True,False]):
            myGame.add_token()

        global emeraldLevel
        if levelNum == emeraldLevel:
            myGame.add_emerald()
            game.emeraldText = document.createElementNS("http://www.w3.org/2000/svg","text")
            game.emeraldText.setAttribute("y", 100)
            game.emeraldText.setAttribute("x", 600)
            game.emeraldText.textContent = "Enharmonic Emeralds: 0";
            game.emeraldText.setAttribute("fill", "white")
            app.appendChild(game.emeraldText)
        elif levelNum > emeraldLevel and random.choice([True,False]):
            myGame.add_emerald()
    
    global level
    if level is None:
        for a in ["I","II","III","IV","IV"]:
            lObj = document.createElementNS("http://www.w3.org/2000/svg","text")
            lObj.setAttribute("y", 20)
            lObj.setAttribute("x", 600)
            lObj.setAttribute("fill", "white")
            lObj.textContent = "Level " + a
            levelNames.append(lObj)

        lObj = document.createElementNS("http://www.w3.org/2000/svg","text")
        lObj.setAttribute("y", 20)
        lObj.setAttribute("x", 600)
        lObj.setAttribute("fill", "white")
        lObj.textContent = "Level V"
        
        superscript = document.createElementNS("http://www.w3.org/2000/svg", "tspan")
        superscript.textContent = "7"
        superscript.setAttribute("baseline-shift", "super")
        superscript.setAttribute("font-size", "0.7em")
        lObj.appendChild(superscript)
        levelNames.append(lObj)

        # Create the main text object for the level
        lObj = document.createElementNS("http://www.w3.org/2000/svg", "text")
        lObj.setAttribute("y", 20)
        lObj.setAttribute("x", 600)
        lObj.setAttribute("fill", "white")
        lObj.textContent = "Level V"
        
        # Create a tspan for the superscript 6
        superscript_6 = document.createElementNS("http://www.w3.org/2000/svg", "tspan")
        superscript_6.textContent = "6"
        superscript_6.setAttribute("baseline-shift", "super")  # Superscript shift
        superscript_6.setAttribute("font-size", "0.7em")  # Scale down the size
        
        # Create a tspan for the subscript 5
        subscript_5 = document.createElementNS("http://www.w3.org/2000/svg", "tspan")
        subscript_5.textContent = "5"
        subscript_5.setAttribute("baseline-shift", "sub")  # Superscript shift
        subscript_5.setAttribute("dx", "-0.5em")  # Move left to align directly under the 6
        subscript_5.setAttribute("font-size", "0.7em")  # Scale down the size
        
        # Append the tspans for 6 and 5 to the main text
        lObj.appendChild(superscript_6)
        lObj.appendChild(subscript_5)
        
        # Add the final SVG text object to the levelNames list (or wherever you're appending it)
        levelNames.append(lObj)

        # Create the main text object for the level
        lObj = document.createElementNS("http://www.w3.org/2000/svg", "text")
        lObj.setAttribute("y", 20)
        lObj.setAttribute("x", 600)
        lObj.setAttribute("fill", "white")
        lObj.textContent = "Level vii"
        
        # Create a tspan for the half-diminished symbol "ø"
        tspan_half_dim = document.createElementNS("http://www.w3.org/2000/svg", "tspan")
        tspan_half_dim.setAttribute("baseline-shift", "super")  # Superscript shift
        tspan_half_dim.setAttribute("font-size", "0.7em")  # Scale down the size
        tspan_half_dim.textContent = "ø7"        
        lObj.appendChild(tspan_half_dim)
        
        # Create a tspan for "/V"
        tspan_applied_chord = document.createElementNS("http://www.w3.org/2000/svg", "tspan")
        tspan_applied_chord.textContent = "/V"
        lObj.appendChild(tspan_applied_chord)
        
        # Add the final SVG text object to the levelNames list (or wherever you're appending it)
        levelNames.append(lObj)

        # Create the main text object for the level
        lObj = document.createElementNS("http://www.w3.org/2000/svg", "text")
        lObj.setAttribute("y", 20)
        lObj.setAttribute("x", 600)
        lObj.setAttribute("fill", "white")
        lObj.textContent = "Level Gr"
        
        # Create a tspan for the half-diminished symbol "ø"
        tspan_half_dim = document.createElementNS("http://www.w3.org/2000/svg", "tspan")
        tspan_half_dim.setAttribute("baseline-shift", "super")  # Superscript shift
        tspan_half_dim.setAttribute("font-size", "0.7em")  # Scale down the size
        tspan_half_dim.textContent = "+6"        
        lObj.appendChild(tspan_half_dim)
        
        # Add the final SVG text object to the levelNames list (or wherever you're appending it)
        levelNames.append(lObj)

        # Create the main text object for the level
        lObj = document.createElementNS("http://www.w3.org/2000/svg", "text")
        lObj.setAttribute("y", 20)
        lObj.setAttribute("x", 600)
        lObj.setAttribute("fill", "white")
        lObj.textContent = "Level N"
        
        # Create a tspan for the half-diminished symbol "ø"
        tspan_half_dim = document.createElementNS("http://www.w3.org/2000/svg", "tspan")
        tspan_half_dim.setAttribute("baseline-shift", "sub")  # Superscript shift
        tspan_half_dim.setAttribute("font-size", "0.7em")  # Scale down the size
        tspan_half_dim.textContent = "6"        
        lObj.appendChild(tspan_half_dim)
        
        # Add the final SVG text object to the levelNames list (or wherever you're appending it)
        levelNames.append(lObj)
    
    #global par
    if par is None:
        par = document.createElementNS("http://www.w3.org/2000/svg","text")
        par.setAttribute("y", 40)
        par.setAttribute("x", 600)
        par.setAttribute("fill", "white")
        app.appendChild(par)

    
    #global strikes
    if strikes is None:
        strikes = document.createElementNS("http://www.w3.org/2000/svg","text")
        strikes.setAttribute("y", 60)
        strikes.setAttribute("x", 600)
        strikes.setAttribute("fill", "white")
        app.appendChild(strikes)

    if gameTime is None:
        gameTime = document.createElementNS("http://www.w3.org/2000/svg","text")
        gameTime.setAttribute("y", 780)
        gameTime.setAttribute("x", 20)
        gameTime.setAttribute("fill", "white")
        if levelNum >= 2:
            app.appendChild(gameTime)

    if not myGame is None:
        parCount = 0
        for ln in myGame.lines:
            parCount += len(ln)
        par.textContent = "Par " + str(parCount)
        stkText = "Strikes: "
        for n in range(game.strikes):
            stkText += '\u266f'
        strikes.textContent = stkText

        totSec = int(time.time()) - startTime
        totMin = totSec // 60
        totHr = totMin // 60

        sec = totSec % 60
        min = totMin % 60

        gameTime.textContent = str(totHr).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2)
        
        if not level is None:
            level.remove()
        level = levelNames[levelNum]
        app.appendChild(level)
        
longTime = open_url("./long_time.txt").readlines()
wrongNote = open_url("./wrong_notes.txt").readlines()

complaintAni = 0
complaintLock = Lock()
isComplaining = False
complaints = []
maestroFram = 11

def maestro_complaint(text = None):
    maestro.remove()
    global maestroFram
    maestroFram = 0
    #display("Maestro_complaint: acquire lock")
    #complaintLock.acquire()
    global isComplaining
    if isComplaining:
        global complaints
        complaints.append(text)
        return

    isComplaining = True
    app.appendChild(speech)
    global speechText
    if text is None:
        text = random.choice(longTime)
    newLines = [0]
    for n in range(50, len(text), 50):
        nl = text.find(" ", n)
        if nl > 0:
            newLines.append(nl)
    newLines.append(len(text))
    for n in range(len(newLines) - 1):
        tspan = document.createElementNS("http://www.w3.org/2000/svg", "tspan")
        tspan.setAttribute("x", "50%")#100
        tspan.setAttribute("dy", 7)
        if n == 0:
            y = 7
            if len(newLines) - 1 == 2:
                y = 11
            if len(newLines) - 1 == 1:
                y = 14
            tspan.setAttribute("y", y)
        tspan.textContent = text[newLines[n]:newLines[n+1]]
        #display(text[newLines[n]:newLines[n+1]])
        speechText.appendChild(tspan)
    #app.appendChild(speech)
    global complaintAni
    complaintAni = set_interval(clear_complaint, 6000)
        
    #speechText.textContent = random.choice(longTime)


def clear_complaint():
    childCount = speechText.childElementCount
    for n in range(childCount):
        child = speechText.children.item(0)
        if not child is None:
            child.remove()
    speech.remove()
    clear_interval(complaintAni)
    global isComplaining
    isComplaining = False
    if len(complaints) > 0:
        maestro_complaint(complaints.pop(0))
    #complaintLock.release()
    
#maestro_complaint()
pitch.aniInter = set_interval(move,40)

lastAddTime = startTime
addDurs = []

def animate(event):
    if pitch.falling:
        return 
    global myGame
    if game.lost:

                #display("won")
        for n in range(app.childElementCount):
            c = app.children.item(n)
            if not c is None:
                c.remove()
                
        loading = document.createElementNS("http://www.w3.org/2000/svg","text")
        loading.setAttribute("dominant-baseline", "middle")
        loading.setAttribute("text-anchor","middle")
        loading.setAttribute("x", 400)
        loading.setAttribute("y", 400)
        loading.textContent = "Loading..."
        loading.setAttribute("fill", "white")
        loading.setAttribute("font-size", "24pt")
        #loading.setAttribute("width","100")
        app.appendChild(loading)       

        global levelNum
        levelNum = 0
        
        lastCursor = None
        
        game.currentGS = 0
        game.usersNotes = [[],[],[]]
        game.lineFinished = False
        #game.strikes = 0
        game.won = False

        pitch.aniInter = 0
        pitch.ani = False
        pitch.falling = False
        pitch.funcsInProgress = []

        game.strikes = 0
        game.lost = False
        game.token = None
        game.tokenCount = 0
        game.tokenText = None
        game.applyingToken = False

        
        game.emerald = None
        game.emeraldCount = 0
        game.emeraldText = None
        game.applyingEmerald = False
        #pitch.lock.release()

        display_app(app)
        myGame = game.Game(app, levelNum)
        global par
        par = None
        global strikes
        strikes = None
        global gameTime
        gameTime = None
        global startTime
        startTime = int(time.time())
        #lastAdded = None
        global level
        global maestroFram
        maestroFram = 11
        level = None
        global cleared
        cleared = False
        loading.remove()
        pitch.aniInter = set_interval(move,40)
        return

    
    if not game.token is None and game.currentGS == game.token.myGS:
        x = 400
        if not game.token.frame is None:
            x = game.token.x
        game.token.queue_or_build_func(app, x, 10)

    if not game.emerald is None and game.currentGS == game.emerald.myGS:
        x = 400
        if not game.emerald.frame is None:
            x = game.emerald.x
        game.emerald.queue_or_build_func(app, x, 10)
    #display("click")
    letterNum = calculate_letter(event)
    p = pitch.Pitch(letterNum, accidental = accidental)
    #global myGame
    if myGame.try_adding(p, event):
        p.animate(app, event.offsetX, 10)
        global lastAddTime
        t = int(time.time())
        dur = t - lastAddTime
        addDurs.append(dur)
        ave = 0
        for n in addDurs:
            ave += n
        ave /= len(addDurs)
        if dur > ave:
            maestro_complaint()
        lastAddTime = t
    else:
        maestro_complaint(random.choice(wrongNote))
        #global lastAdded
        #lastAdded = p


def add_pitch(event):
    letterNum = calculate_letter(event)
    p = pitch.Pitch(letterNum, accidental = accidental)
    myGame.try_adding(p, event)
    #notes.append(p)
    #p.add_gsv(app, mouseX)

def calculate_letter(event):
    gs = document.getElementById("grandStaff" + str(game.currentGS))
    min = -1
    #display(mouseY, gs.children.item(0).children.item(0).getAttribute("y1"))
    closestSt = 0
    closestLn = 0
    for st in range(2):
        staff = gs.children.item(st)
        for ln in range(staff.children.length):
            line = staff.children.item(ln)
            if min < 0 or abs(int(line.getAttribute("y1")) - mouseY) < min:
                min = abs(int(line.getAttribute("y1")) - mouseY)
                closestSt = st
                closestLn = ln
    letterNum = 16 - closestLn
    if closestSt == 1:
        letterNum = -1 - closestLn
    return letterNum

def show_coords(event):
    display(mouseX)

def mouse_move(event):
    global mouseX
    mouseX = event.offsetX
    global mouseY
    mouseY = event.offsetY
    draw_cursor(event)
    #display("move")


def key_down(event):
    draw_cursor(event)
    if(event.key == "Backspace"):
        #pitch.lock.acquire()
        #if len(game.usersNotes[game.currentGS]) <= 1:
            #game.currentGS = game.currentGS - 1
        if len(game.usersNotes[game.currentGS]) > 1 and not game.lineFinished:
            p = game.usersNotes[game.currentGS].pop(len(game.usersNotes[game.currentGS]) - 1)
            p.remove()
            if p.myFunc in pitch.funcsInProgress:
                pitch.funcsInProgress.remove(p.myFunc)

    elif event.key == "t" and game.tokenCount > 0 and not game.lineFinished:
        game.tokenCount -= 1
        game.tokenText.textContent = "Gold Tokens: " + str(game.tokenCount)
        while(len(game.usersNotes[game.currentGS]) > 1):
            p = game.usersNotes[game.currentGS].pop(len(game.usersNotes[game.currentGS]) - 1)
            p.remove()
            if p.myFunc in pitch.funcsInProgress:
                pitch.funcsInProgress.remove(p.myFunc)

        global applyingToken
        game.applyingToken = True
        for n in range(1, len(myGame.lines[game.currentGS])):
                p = pitch.copy_pitch(myGame.lines[game.currentGS][n])
                p.myGS = game.currentGS
                if myGame.try_adding(p):
                    p.animate(app, 400, 10)
        game.applyingToken = False

    elif event.key == "e" and game.emeraldCount > 0:
        #display("e")
        game.emeraldCount -= 1
        game.emeraldText.textContent = "Enharmonic Emeralds: " + str(game.emeraldCount)
        game.applyingEmerald = True
        game.applyingEmeraldText = document.createElementNS("http://www.w3.org/2000/svg","text")
        game.applyingEmeraldText.textContent = "...or ENH."
        game.applyingEmeraldText.setAttribute("x", 670)
        game.applyingEmeraldText.setAttribute("y", int(document.getElementById("grandStaff" + str(game.currentGS)).children.item(0).children.item(4).getAttribute("y1")))
        game.applyingEmeraldText.setAttribute("fill", "lime")
        app.appendChild(game.applyingEmeraldText)

    
def key_up(event):
    draw_cursor(event)

func = None
def draw_cursor(event):
    met = event.metaKey or event.ctrlKey
    alt = event.altKey
    shift = event.shiftKey
    global accidental
    if shift and not met:
        accidental = 1
    elif alt:
        accidental = -1
    elif shift and met:
        accidental = 2
    elif met:
        accidental = -2
    else:
        accidental = 0
    circle = document.createElementNS("http://www.w3.org/2000/svg","circle")
    circle.setAttribute("cx",mouseX)
    circle.setAttribute("cy",mouseY)
    circle.setAttribute("r",5)
    circle.setAttribute("stroke","white")
    circle.setAttribute("stroke-width",1)
    circle.setAttribute("fill","white")
    #app.appendChild(circle)

    myX = mouseX
    myY = mouseY
    if accidental == -1 or accidental == -2:
        accString = '\u266d'
    elif accidental == 1:
        accString = '\u266f'
    #elif accidental == -2:
        #accString = '\u1d12b'
    elif accidental == 2:
        accString = "x"#'\u1d12a'
    else:
        accString = '\u266e'

    flat = document.createElementNS("http://www.w3.org/2000/svg","text")
    text = document.createTextNode(accString)
    flat.appendChild(text)
    if accidental != 2:
        flat.setAttribute("x", myX - 20)
        flat.setAttribute("y", myY + 6)
    else:
        flat.setAttribute("x", myX - 15)
        flat.setAttribute("y", myY + 4) 
    flat.setAttribute("fill", "white")
    #circle.appendChild(flat)

    cursor = document.createElementNS("http://www.w3.org/2000/svg","svg")
    cursor.appendChild(circle)
    cursor.appendChild(flat)
    app.appendChild(cursor)
    
    if accidental == -2:
            flat = document.createElementNS("http://www.w3.org/2000/svg","text")
            text = document.createTextNode(accString)
            flat.appendChild(text)
            flat.setAttribute("x", myX - 30)
            flat.setAttribute("y", myY + 6)
            flat.setAttribute("fill", "white")
            cursor.appendChild(flat)
    
    #global lastCursor
    if not(game.lastCursor is None):
        game.lastCursor.remove()
    game.lastCursor = cursor
    
    acciNames = ["double flat", "flat", "natural", "sharp", "double sharp"]

    acciName = acciNames[accidental + 2]
    letterName.textContent = letters[(calculate_letter(event) + 14) % 7] + " " + acciName


def test():
    p1  = pitch.Pitch(-7,accidental=2)
    p2  = pitch.Pitch(-13,accidental=2)
    inter = game.Interval(p2.letterNum - p1.letterNum, p2.hs - p1.hs, ascending = (p2.hs > p1.hs))

    display(str(p1) + str(p1.hs) + " " + str(p2) + str(p2.hs) + " " + str(inter))
#test()

#app.addEventListener("keydown", test)
#add_event_listener(app, "keydown", "test()")
#document.setAttribute("py-keydown", "draw_cursor")



