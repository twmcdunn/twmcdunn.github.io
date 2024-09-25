from pyscript import document
import game
from pyscript import display
from pyodide.ffi.wrappers import set_interval
from pyodide.ffi.wrappers import clear_interval
from threading import Lock
from js import Audio

aniInter = 0
ani = False
falling = False
funcsInProgress = []

lock = Lock()

sounds = []

pitchId = 0

for n in range(12):
    sounds.append(Audio.new(str(n) + '.mp3'))

def copy_pitch(p):
    return Pitch(p.letterNum, p.hs)

class Pitch:
    cMajorScale = [0,2,4,5,7,9,11]
    letterNames = ["C","D","E","F","G","A","B"]
    acciNames = ["double flat", "flat", "natural", "sharp", "double sharp"]
    
    def __init__(self, letter, halfSteps = None, accidental = None):
        #self.funcToBuild = []
        self.imEmerald = False
        self.imToken = False
        self.frame = None
        global pitchId 
        pitchId += 1
        self.pitchId = pitchId
        self.myGS = game.currentGS
        self.queuedFunctions = []
        self.ledgers = None
        self.animating = False
        self.conline = None
        self.yv = None
        self.y = None
        self.badNoteText = None
        self.fallAni = None
        self.floatAni = None
        self.letterNum = letter
        if accidental is None:
            self.hs = halfSteps
            naturalHS = self.cMajorScale[(self.letterNum + 21) % 7]
            self.myAccidental = (self.hs + 36) % 12 - naturalHS
            if abs(self.myAccidental) > 2:
                if naturalHS == 0:
                    naturalHS = 12
                elif naturalHS == 11:
                    naturalHS = -1
                ##if neither of the above is true, it's a triple flat or triple sharp (not allowed in game)
                self.myAccidental = (self.hs + 36) % 12 - naturalHS
        elif halfSteps is None:
            if letter >= 0:
                self.hs = self.cMajorScale[letter % 7] + accidental
                self.hs += 12 * (letter // 7)
            else:
                self.hs = self.cMajorScale[(28 + letter) % 7] + accidental
                self.hs -= 12 * (1 + abs(letter + 1) // 7)
            self.myAccidental = accidental

    def __str__(self):
        return self.letterNames[(self.letterNum + 21) % 7] + " " + self.acciNames[self.myAccidental + 2]
    
    def __eq__(self,other):
        return self.hs == other.hs and self.letterNum == other.letterNum

    def get_y(self, midCTreb = None, midCBass = None):
        if midCTreb is None:
            gs = document.getElementById("grandStaff" + str(self.myGS))
            #display("grandStaff" + str(self.myGS))
            treble = gs.children.item(0)#treble staff of gs 0
            bass = gs.children.item(1)
            midCTreb = int(treble.children.item(16).getAttribute("y1"))
            midCBass = int(bass.children.item(0).getAttribute("y1")) - 5
        y = -5*self.letterNum
        if self.letterNum >= 0:
            y += midCTreb
        else:
            y += midCBass
        return y

    def build_function(self, app, x0, v0):
        #self.funcToBuild.append([x0,v0])
        #display("build funct for: " + str(self))
        
        self.remove_ledgers()
        self.animating = True
        self.app = app
        self.child = None
        self.parent = None
        y0 = self.get_y()
        self.yf = y0
        numOfNotes = len(game.usersNotes[self.myGS])

        child = None
        if (not game.token is None and self.pitchId == game.token.pitchId) or (not game.emerald is None and self.pitchId == game.emerald.pitchId):
            self.xf = 700 - (0.25 * 580 / numOfNotes)
        else:
            lastIndex = len(game.usersNotes[self.myGS]) - 1 - game.usersNotes[self.myGS][::-1].index(self)
            self.xf = 120 + lastIndex * 580 / numOfNotes
            if game.lineFinished:
                self.xf = 120 + lastIndex * 580 / (numOfNotes - 1)
            if lastIndex > 1:
                child = game.usersNotes[self.myGS][lastIndex - 1]
        bounces = 3


        self.myFunc = Function(y0,self.yf,v0,bounces, self, child)
        self.xv = 0.8 * (self.xf - x0) / self.myFunc.totFrames
        self.x = x0
        self.y = y0
        self.frame = 0
        self.myGsv.setAttribute("cx",self.x)
        self.myGsv.setAttribute("cy",self.y)
        self.show_note()
        self.add_conline()

    def queue_or_build_func(self, app, x0, v0):
        if self.animating:
            self.queuedFunctions.append([app,x0,v0])
        else:
            self.build_function(app, x0, v0)

    def animate(self, app, x0, v0):
        #self.build_function(app, x0, v0)
        self.queue_or_build_func(app, x0, v0)
        #display("set interval")
        global aniInter
        global ani
        ani = True
        #aniInter = set_interval(self.move,10)
        #display(aniInter)

    def fall(self):
        self.y += self.yv
        self.yv += 0.04
        self.myGsv.setAttribute("cy",self.y)
        if self.y > 800:
            clear_interval(self.fallAni)
            global ani
            ani = False
            global falling
            falling = False
            self.badNoteText.remove()
            self.myGsv.remove()
            if game.strikes == 3:
                game.lost = True

    def float(self):
        self.y += self.yv
        self.yv -= 0.1
        self.myGsv.setAttribute("cy",self.y)
        if self.y < 0:
            clear_interval(self.floatAni)
            global ani
            ani = False
            if self.imToken:
                self.tokenText.remove()
            #display("donefloat")
            if self.imEmerald:
                self.emeraldText.remove()
            self.myGsv.remove()
        
    def move(self):
        #display("pitch.move: acquire lock")
        #lock.acquire()
        
        self.frame += 0.8
        self.y = self.myFunc.get_y(self.frame)

        if self.animating:
            self.x += self.xv
            #display(self.y)
            self.myGsv.setAttribute("cx",self.x)
            self.myGsv.setAttribute("cy",self.y)
        if self.frame >= self.myFunc.totFrames:
            if len(funcsInProgress) == 0:
                if game.lost:
                    #display("clear")
                    clear_interval(aniInter)
                    for gs in game.usersNotes:
                        for n in range(1,len(gs)):
                            gs[n].add_ledgers()
                global ani
                ani = False
                #display("animation finised")
                if game.lineFinished:
                    #self.update_conline()
                    game.currentGS = game.currentGS + 1
                    if game.currentGS > 2:
                        game.won = True
                        game.currentGS = 0
                        #lock.release()
                        return
                    line = document.createElementNS("http://www.w3.org/2000/svg","line")
                    line.setAttribute("stroke-width",1)
                    line.setAttribute("stroke","white")
                    un = game.usersNotes
                    p1 = un[game.currentGS-1][len(un[game.currentGS-1])-1]
                    p2 = un[game.currentGS][0]
                    line.setAttribute("x1", p1.x)
                    line.setAttribute("x2", p2.x)
                    line.setAttribute("y1", p1.y)
                    line.setAttribute("y2", p2.y)
                    self.app.appendChild(line)
                    #display("Line and animation finished " + str(self))
                    game.lineFinished = False
                    #display("LN FINISHED FALEFIED by" + str(self))

            self.x = self.xf #align perfectly
            self.y = self.yf
            self.myGsv.setAttribute("cx",self.x)
            self.myGsv.setAttribute("cy",self.y)
            if self.animating:
                self.add_ledgers()
            self.animating = False
            if len(self.queuedFunctions) > 0:
                param = self.queuedFunctions.pop(0)
                self.build_function(param[0], self.x, param[2])
        
            #if not self.parent is None:
                #self.parent.child = None
        
        if not self.child is None:
            self.child.parent = self
            #display("child move")
            #self.child.move()
        #if not game.lineFinished or self.animating:
        self.update_conline()
        
        #lock.release()

    def remove(self):
        self.myGsv.remove()
        self.remove_ledgers()
        if not self.conline is None:
            self.conline.remove()
        
    def add_gsv(self, app, xVal):
        gs = document.getElementById("grandStaff" + str(self.myGS))
        #display("grandStaff" + str(self.myGS))
        treble = gs.children.item(0)#treble staff of gs 0
        bass = gs.children.item(1)
        midCTreb = int(treble.children.item(16).getAttribute("y1"))
        midCBass = int(bass.children.item(0).getAttribute("y1")) - 5
        
        y = self.get_y(midCTreb,midCBass)
        global myY
        global myX
        myY = y
        myX = xVal
        self.x = myX
        self.y = y
        #global myGsv 
        self.myGsv = document.createElementNS("http://www.w3.org/2000/svg","circle")
        self.myGsv.setAttribute("cx",myX)
        self.myGsv.setAttribute("cy",y)
        self.myGsv.setAttribute("r",5)
        self.myGsv.setAttribute("stroke-width",1)
        
        if not game.token is None and self.pitchId == game.token.pitchId:
            self.myGsv.setAttribute("stroke","yellow")
            self.myGsv.setAttribute("fill","yellow")
            #display("YELLOW")
        elif not game.emerald is None and self.pitchId == game.emerald.pitchId:
            self.myGsv.setAttribute("stroke","lime")
            self.myGsv.setAttribute("fill","lime")
        else:
            self.myGsv.setAttribute("fill","white")
            self.myGsv.setAttribute("stroke","white")
        self.app = app

    def add_conline(self):
        if (not game.token is None and self.pitchId == game.token.pitchId) or (not game.emerald is None and self.pitchId == game.emerald.pitchId):
            return
        if not self.conline is None:
            self.conline.remove()
        self.conline = document.createElementNS("http://www.w3.org/2000/svg","line")
        self.conline.setAttribute("stroke-width",1)
        self.conline.setAttribute("stroke","white")
        self.update_conline()
        self.app.appendChild(self.conline)


    def update_conline(self):
        if (not game.token is None and self.pitchId == game.token.pitchId) or (not game.emerald is None and self.pitchId == game.emerald.pitchId):
            return
        x = self.x
        y = self.y
        lastIndex = len(game.usersNotes[self.myGS]) - 1 - game.usersNotes[self.myGS][::-1].index(self)
        if lastIndex > 0:
            child = game.usersNotes[self.myGS][lastIndex - 1]
            x = child.x
            y = child.y
        self.conline.setAttribute("x1", self.x)
        self.conline.setAttribute("x2", x)
        self.conline.setAttribute("y1", self.y)
        self.conline.setAttribute("y2", y)

    def show_note(self):
        self.app.appendChild(self.myGsv)
        
    def add_ledgers(self):
        myY = self.y
        myX = self.x
        #display("adding accidnetal myX = " + str(self.x) + " " + str(self))
        gs = document.getElementById("grandStaff" + str(self.myGS))
        #display("grandStaff" + str(self.myGS))
        treble = gs.children.item(0)#treble staff of gs 0
        bass = gs.children.item(1)
        midCTreb = int(treble.children.item(16).getAttribute("y1"))
        midCBass = int(bass.children.item(0).getAttribute("y1")) - 5
        self.ledgers = document.createElementNS("http://www.w3.org/2000/svg","svg")
        if self.letterNum >= 0:
            for ln in range((self.letterNum - 10)//2):
                y = midCTreb - (12 + 2*ln) * 5
                line = document.createElementNS("http://www.w3.org/2000/svg","line")
                line.setAttribute("stroke-width",1)
                line.setAttribute("stroke","white")
                line.setAttribute("x1", myX - 8)
                line.setAttribute("x2", myX + 8)
                line.setAttribute("y1", y)
                line.setAttribute("y2", y)
                self.ledgers.appendChild(line)
        else:
            for ln in range((-self.letterNum - 10)//2):
                y = midCBass + (12 + 2*ln) * 5
                line = document.createElementNS("http://www.w3.org/2000/svg","line")
                line.setAttribute("stroke-width",1)
                line.setAttribute("stroke","white")
                line.setAttribute("x1", myX - 8)
                line.setAttribute("x2", myX + 8)
                line.setAttribute("y1", y)
                line.setAttribute("y2", y)
                self.ledgers.appendChild(line)
        if self.myAccidental == -1 or self.myAccidental == -2:
            accString = '\u266d'
        elif self.myAccidental == 1:
            accString = '\u266f'
        #elif self.myAccidental == -2:
            #accString = '\u1d12b'
        elif self.myAccidental == 2:
            accString = "x"#'\u1d12a'
        else:
            accString = '\u266e'

        flat = document.createElementNS("http://www.w3.org/2000/svg","text")
        text = document.createTextNode(accString)
        flat.appendChild(text)
        if self.myAccidental != 2:
            flat.setAttribute("x", myX - 20)
            flat.setAttribute("y", myY + 6)
        else:
            flat.setAttribute("x", myX - 15)
            flat.setAttribute("y", myY + 4) 
        flat.setAttribute("fill", "white")
        self.ledgers.appendChild(flat)

        if self.myAccidental == -2:
            flat = document.createElementNS("http://www.w3.org/2000/svg","text")
            text = document.createTextNode(accString)
            flat.appendChild(text)
            flat.setAttribute("x", myX - 30)
            flat.setAttribute("y", myY + 6)
            flat.setAttribute("fill", "white")
            self.ledgers.appendChild(flat)
            
        if self.letterNum == 0:
            y = midCTreb
            line = document.createElementNS("http://www.w3.org/2000/svg","line")
            line.setAttribute("stroke-width",1)
            line.setAttribute("stroke","white")
            line.setAttribute("x1", myX - 8)
            line.setAttribute("x2", myX + 8)
            line.setAttribute("y1", y)
            line.setAttribute("y2", y)
            self.ledgers.appendChild(line)
        self.app.appendChild(self.ledgers)   

    def accept_emerald(self):
        self.yv = 0
        self.imEmerald = True
        game.emerald = None
        if not self.myFunc is None and self.myFunc in funcsInProgress:
            funcsInProgress.remove(self.myFunc)
                    
        self.emeraldText = document.createElementNS("http://www.w3.org/2000/svg","text")
        self.emeraldText.setAttribute("dominant-baseline", "middle")
        self.emeraldText.setAttribute("text-anchor","middle")
        self.emeraldText.setAttribute("x", self.x)
        self.emeraldText.setAttribute("y", self.y + 20)
        self.emeraldText.textContent = "Press \'e\' to use."
        self.emeraldText.setAttribute("fill", "lime")
        self.emeraldText.setAttribute("font-size", "12pt")
        #self.emeraldText.setAttribute("width","100")
        self.app.appendChild(self.emeraldText)
        
        self.floatAni = set_interval(self.float,10)
    
    def accept_token(self):
        self.yv = 0
        self.imToken = True
        game.token = None
        if not self.myFunc is None and self.myFunc in funcsInProgress:
            funcsInProgress.remove(self.myFunc)
                    
        self.tokenText = document.createElementNS("http://www.w3.org/2000/svg","text")
        self.tokenText.setAttribute("dominant-baseline", "middle")
        self.tokenText.setAttribute("text-anchor","middle")
        self.tokenText.setAttribute("x", self.x)
        self.tokenText.setAttribute("y", self.y + 20)
        self.tokenText.textContent = "Press \'t\' to use."
        self.tokenText.setAttribute("fill", "yellow")
        self.tokenText.setAttribute("font-size", "12pt")
        #self.tokenText.setAttribute("width","100")
        self.app.appendChild(self.tokenText)
        
        self.floatAni = set_interval(self.float,10)
        #self.remove()
        
        
    def remove_ledgers(self):
        if not self.ledgers is None:
            self.ledgers.remove()

class Function:
    def __init__(self, y0,yf,v0,bounces, parent, child = None):
        funcsInProgress.append(self)
        self.y0 = y0
        self.yf = yf
        self.v0 = v0
        #display(str(v0))
        self.parent = parent
        self.bounceNum = 0

        self.segs = [[v0,y0]]
        self.trans = []

        for n in range(bounces):
            t = self.get_next_bounce()
            #display(t)
            v0 =  self.v0 * pow(0.65, n + 1)
            y0 = self.yf
            self.trans.append(t)
            self.segs.append([v0,y0])
        
        self.bounces = bounces
        self.totFrames = self.get_next_bounce()
        self.remainingBounces = []
        self.remainingBounces.extend(self.trans)
        #for n in self.remainingBounces:
            #display(n)
        
        self.child = child
        self.hasBounced = False

    def get_next_bounce(self):
        v0 = self.segs[len(self.segs) - 1][0]
        y0 = self.segs[len(self.segs) - 1][1]
        yf = self.yf
        totPrevFrames = 0
        if len(self.trans) > 0:
            totPrevFrames = self.trans[len(self.trans) - 1]
        return totPrevFrames + ((-v0 - pow((v0 * v0) + (4 * 0.5 * (y0 - yf)),0.5)) / (2 * (-0.5)))

    def get_v(self, f):
        ind = 0
        for t in self.trans:
            if f > t:
                ind += 1
                
        v0 = self.segs[ind][0]
        return -f + v0

    def get_y(self, f):
        #f = f * 001
        if f >= self.totFrames:
            if self in funcsInProgress:
                #display("remove")
                funcsInProgress.remove(self)
            return self.yf
        ind = 0
        for t in self.trans:
            if f > t:
                ind += 1
        v0 = self.segs[ind][0]
        y0 = self.segs[ind][1]
        if len(self.remainingBounces) != 0 and f >= self.remainingBounces[0]:
            self.remainingBounces.pop(0)
            self.bounce()
        if ind > 0:
            f = f - self.trans[ind - 1]
        return -((-pow(f,2) / 2.0) + (v0 * f)) + y0

    def bounce(self):
        #display("bounce")
        #afplay @"./key.mp3"
        s = Audio.new(str((self.parent.hs + 120) % 12) + ".mp3")
        s.volume = (abs(self.v0) / 50) * pow(0.5,self.bounceNum)
        s.play()
        self.bounceNum += 1
        
        #Audio.new('key.mp3').play()
        if not self.hasBounced:
            self.hasBounced = True
            if not (self.child is None):
                self.child.v0 = self.v0 * 0.9
                self.child.x0 = self.child.x
                #self.child.build_function(self.parent.app, self.child.x, self.v0 * 0.9)
                self.child.queue_or_build_func(self.parent.app, self.child.x, self.v0 * 0.9)
                #self.child.app = self.parent.app
                self.parent.child = self.child
                #self.child.parent = self.parent

        
        
        