from pyscript import display
from pyscript import document
import random
import pitch
from pyodide.ffi.wrappers import set_interval
from pyodide.ffi.wrappers import clear_interval

lastCursor = None
currentGS = 0
usersNotes = [[],[],[]]
lineFinished = False
strikes = 0
won = False
lost = False
token = None
tokenCount = 0
tokenText = None
applyingToken = False
emerald = None
emeraldCount = 0
emeraldText = None
applyingEmerald = False
applyingEmeraldText = None

class Game:
    cMajorScale = [0,2,4,5,7,9,11]
    
    
    def __init__(self, app, levelNum = 0):
        self.easy = levelNum < 7
        global token
        token = None
        global emerald
        emerald = None
        self.levelNum = levelNum
        self.app = app
        global currentGS
        currentGS = 0
        global won
        won = False

        global usersNotes
        usersNotes = [[],[],[]]

        self.lines = [[],[],[]]
        self.alloweds = [[],[],[]]
        """
        self.generate_line(pitch.Pitch(0,0), 2)
        for p in self.lines[2]:
            display(str(p))
        
        """
        letterNum = random.randint(0,6)
        p = pitch.Pitch(letterNum,self.cMajorScale[letterNum])
        #self.staves[staff].append(p)
        
        for n in range(3):
            currentGS = n
            p = pitch.copy_pitch(p)
            p.myGS = n
            p.add_gsv(app,120)
            p.show_note()
            p.add_ledgers()
            
            usersNotes[n].append(p)
            self.generate_line(p,n)
            p = self.lines[n][len(self.lines[n]) - 1]
            p.add_gsv(app,700)
            p.show_note()
            p.add_ledgers()

            instructions = document.createElementNS("http://www.w3.org/2000/svg","text")
            text = document.createTextNode("Use only " + str(self.alloweds[n][0]) + "s and " + str(self.alloweds[n][1]) + "s.")
            #instructions.setAttribute("unselectable", "on")
            instructions.appendChild(text)
            instructions.setAttribute("x", 100)
            instructions.setAttribute("y", int(document.getElementById("grandStaff" + str(n)).children.item(0).children.item(4).getAttribute("y1")))
            instructions.setAttribute("fill", "grey")
            app.appendChild(instructions)

        currentGS = 0

    def add_token(self):
        lnNum = random.randint(0,2)
        ln = self.lines[lnNum]
        p = random.choice(ln[1:-1])
        global token
        token = pitch.copy_pitch(p)
        token.myGS = lnNum
        token.add_gsv(self.app, 400)
        token.show_note()
        token.add_ledgers()

    def add_emerald(self):
        lnNum = random.randint(0,2)
        ln = self.lines[lnNum]
        p = random.choice(ln[1:-1])
        global emerald
        emerald = pitch.copy_pitch(p)
        emerald.myGS = lnNum
        emerald.add_gsv(self.app, 400)
        emerald.show_note()
        emerald.add_ledgers()
    
    def generate_line(self, pitch, ln):
        numPitches = 2 + self.levelNum + random.randint(0,1)
        allPossible = None
        #display(numPitches)
        allowedInters = None
        while True:
            allowedInters = self.generate_intervals()
            allPossible = [[pitch]]
            while len(allPossible[0]) < numPitches:#continue to make moves until line is long enough
                allPossible = self.make_moves(allPossible, allowedInters)# makes one move
                if len(allPossible) == 0:# hit deadends on all brances
                    break
            if len(allPossible) > 0:
                break

        self.lines[ln] = allPossible[random.randint(0,len(allPossible)-1)]
        self.alloweds[ln] = allowedInters

    def make_moves(self, lines, allowedInters):
        newLines = []
        for line in lines:
            for inter in allowedInters:
                lastNote = line[len(line) - 1]
                p =  pitch.Pitch(lastNote.letterNum + inter.size, lastNote.hs + inter.hs)
                if abs(p.myAccidental) <= 2 and abs(p.letterNum) <= 16:
                    shorterPathExits = False
                    for ln in lines:
                        if p in ln:
                            shorterPathExits = True
                            break
                    if not shorterPathExits:
                        newLines.append(line + [p])
        return newLines
    
    def generate_intervals(self):
        results = []
        for interNum in range(2):
            while True:
                size = random.randint(0,7)
                if self.easy:#no aug uni/dim oct on easy
                    size = random.randint(1,6)
                quality = None
                if size == 0 or size == 7:
                    if size == 7 and random.randint(0,1) == 1:
                        quality = -1
                    else:
                        quality = 1
                elif size == 3:
                    if self.easy:
                        quality = random.randint(0,1)
                    else:
                        quality = random.randint(-2,2)
                elif size == 4:
                    if self.easy:
                        quality = random.randint(-1,0)
                    else:
                        quality = random.randint(-2,2)
                else:
                    if self.easy:
                        quality = random.randint(-1,0)
                    else:
                        quality = random.randint(-3,2)
                if interNum == 0 or results[0].quality != quality or results[0].size != size:
                    results.append(Interval(size, quality=quality,ascending=(interNum == 0)))
                    break
        return results

    def try_adding(self, p, event = None):
        p.myGS = currentGS
        global usersNotes#not really necessary
        lastNote = usersNotes[currentGS][len(usersNotes[currentGS]) - 1]
        inter = Interval(p.letterNum - lastNote.letterNum, p.hs - lastNote.hs, ascending = (p.hs > lastNote.hs))
        enh = False
        if applyingEmerald:
            for i in self.alloweds[currentGS]:
                if inter.hs == i.hs:
                    enh = True
        if inter in self.alloweds[currentGS] or enh:
            global token
            global tokenCount
            if (not token is None) and p.myGS == token.myGS and token == p and (not applyingToken):
                token.accept_token()
                tokenCount += 1
                global tokenText
                tokenText.textContent = "Gold Tokens: " + str(tokenCount);

            global emerald
            global emeraldCount
            if (not emerald is None) and p.myGS == emerald.myGS and emerald == p:
                emerald.accept_emerald()
                emeraldCount += 1
                global emeraldText
                emeraldText.textContent = "Enharmonic Emeralds: " + str(emeraldCount);
            #display("good note")
            self.good_note(p, event)
            return True
        else:
            self.bad_note(lastNote, p, event, inter)
            return False
            
    def good_note(self, p, event):
        global usersNotes
        global currentGS
        usersNotes[currentGS].append(p)
        lastIndex = len(usersNotes[p.myGS]) - 1 - usersNotes[p.myGS][::-1].index(p)
        x = 120 + lastIndex * 580 / len(usersNotes[currentGS])
        #add animation here
        if p == self.lines[currentGS][len(self.lines[currentGS]) - 1]:
            #display("line finished")
            global lineFinished
            #display("LIINE FINISHED")
            lineFinished = True
            global applyingEmerald
            applyingEmerald = False
            x = 700
        p.add_gsv(self.app, x)
        p.add_conline()


    def bad_note(self, lastNote, p, event, inter):
        global strikes
        strikes += 1
        self.badNoteText = document.createElementNS("http://www.w3.org/2000/svg","text")
        interStr = str(inter)
        if inter.ascending:
            interStr = " an " + interStr
        else:
            interStr = " a " + interStr
        text = document.createTextNode(str(lastNote) + " to " + str(p) + " forms " + interStr + ".")
        self.badNoteText.appendChild(text)
        self.badNoteText.setAttribute("x", 20)
        self.badNoteText.setAttribute("y", 40)
        #self.badNoteText.setAttribute("stroke", "white")
        self.badNoteText.setAttribute("fill", "white")
        self.app.appendChild(self.badNoteText)
        p.yv = 0
        p.y = p.get_y()
        p.add_gsv(self.app, event.offsetX)
        p.show_note()
        p.badNoteText = self.badNoteText
        p.fallAni = set_interval(p.fall,10)
        pitch.ani = True
        pitch.falling = True
        #add animation here

        
class Interval:
    qualityNames = [["doubly diminished", "diminished", "minor","major", "augmented","doubly augmented"],["doubly diminished", "diminished","perfect","augmented","doubly augmented"]]
    majors = [2,4,9,11]
    majorSizes = [1,2,5,6]#where unison = 0 second = 1
    perfects = [0,5,7,12]
    perfectSizes = [0,3,4,7]
    sizeNames = ["unison","second","third","fourth","fifth","sixth","seventh","octave"]
    cMajorScale = [0,2,4,5,7,9,11]
    
    #sizes 0 = unison 
    def __init__(self, size, hs = None, quality = None, ascending = None):
        self.size = size
        
        if hs is None:
            self.quality = quality
            if abs(self.size) % 7 in self.perfectSizes:
                self.qualityName = self.qualityNames[1][2 + self.quality]
            else:
                self.qualityName = self.qualityNames[0][3 + self.quality]
            self.ascending = ascending
            self.set_hs_from_quality()
            if not self.ascending:
                self.size = -self.size
                self.hs = -self.hs
        else:
            self.hs = hs
            self.set_quality_from_hs(hs)
            self.ascending = (hs >= 0)
            
        self.sizeName = self.sizeNames[abs(self.size) % 7]
        if abs(self.size) % 7  == 0 and self.size != 0:
            self.sizeName = "octave"

    def set_quality_from_hs(self, hs):
        if abs(self.size) % 7 in self.perfectSizes:
            perfHs = self.perfects[self.perfectSizes.index(abs(self.size) % 7)]
            if abs(self.size) >= 7 and abs(self.size) % 7 == 0 and abs(hs) % 12 > 3:
                perfHs = 12
            self.quality =  abs(hs) % 12 - perfHs
            self.qualityName = self.qualityNames[1][2 + self.quality]
        else:
            majHs = self.majors[self.majorSizes.index(abs(self.size) % 7)]
            self.quality = abs(hs) % 12 - majHs
            self.qualityName = self.qualityNames[0][3 + self.quality]
            
    def set_hs_from_quality(self):
        self.hs = self.cMajorScale[self.size]
        self.hs += self.quality
        
    def __str__(self):
        name = "descending"
        if self.ascending:
            name = "ascending"
        name += " " + self.qualityName + " " + self.sizeName
        return name

    def __eq__(self,other):
        #display(str(self) + " " + str(other))
        return str(self) == str(other)


