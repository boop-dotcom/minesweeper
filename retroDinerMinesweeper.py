from tkinter import *
import random
from tkinter import messagebox

class Tile(Label):
    '''one tile object in the form of a tkinter Button'''
    def __init__(self,master,x,y,tile=0):
        '''Tile(master, x, y, tile=0) -> Tile object
        initializes a Tile object'''
        self.colors = ['', '#02A799','#FB8EAE','#38D0BF','#F7B1CC',
                       '#15E2BA', '#F9A0BD','#0CC5AA', '#FA97B6','']
        self.fgbgalt = ['#EEF0ED', '#0D0B0A', '#CECFC9', '#4A4B4C']
        self.fgbg = ['#0CC5AA', '#F9A0BD', '#2C2B2B'] 
        Label.__init__(self,bg=self.fgbg[0],relief='raised', fg='black', width=4,height=2,font=('Arial',16, 'bold')) #display
        self.grid(row=y, column=x)
        self.coords = (x,y)         #row, column coord tuple
        self.isFlagged = False      #starts unflagged
        self.tileDisplay = tile     #defaults to empty
        self.isExposed = False
        self.master = master

        #checkered pattern
        if (x % 2 == 0 and y % 2 == 0) or (x % 2 == 1 and y % 2 == 1): #for checkers pattern
            #self.bow = 'white'                                         #black or white
            self['bg'] = self.fgbg[0]
        else:
            self['bg'] = self.fgbg[1]
        #listeners
        self.bind('<Button-1>', self.expose_tile)
        self.bind('<Button-2>', self.toggle_mine_flag)
        self.bind('<Button-3>', self.toggle_mine_flag)
        

    def toggle_mine_flag(self,master):
        '''self.toggle_mine_flag(master) -> None
        puts an astrix at the box on right click if not flagged
        removes flag from box otherwise'''
        if not self.is_exposed():
            if self['bg'] == self.fgbg[1]:
                self['fg'] = 'black'
            else:
                self['fg'] = 'white'
            if self['text'] == '◎':             #is already marked, de-mark
                self['text'] = ' '
                self.isFlagged = False
                self.master.mine_count_change(1)
            elif self.master.mineCount != 0:    #if mines left and not marked, mark
                self['text'] = '◎'
                self.master.mine_count_change(-1)
                self.isFlagged = True
            self.master.winning_game()

    def expose_tile(self, master, dontExpose=False):
        '''self.expose_tile(master, dontExpose=False) -> None
        on left click, displays number in itself and
        if empty exposes adjacent squares'''
        if not self.isFlagged and not self.isExposed:                   #not marked as a mine

            #if first move of the game
            if not self.master.pressedStart and self.coords != (0,0):
                print('Press the starred tile to begin!')
            elif not self.master.pressedStart and self.coords == (0,0): 
                self.master.pressedStart = True
                self['relief'] = 'sunken'
                self['bg'] = self.fgbg[2]
                if self.tileDisplay == 0:                               #if should be displayed as empty
                    self['state'] = DISABLED
                    if not dontExpose:                                  #only done on first exposing (not in auto-expose)
                        self.master.auto_expose(self)
                else:                                                   #number tile
                    self['fg'] = self.colors[int(self.tileDisplay)]
                    self['text'] = self.tileDisplay
                    self.isExposed=True

            #if is a mine
            elif self.tileDisplay == '◎':                       
                self.master.expose_all_mines()
                messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)

            #if should be displayed as empty (no surrounding mines)
            elif self.tileDisplay == 0:                 
                self['relief'] = 'sunken'
                self['state'] = DISABLED
                self['bg'] = self.fgbg[2]
                if not dontExpose:                                      #only done on first exposing (not in auto-expose)
                    self.master.auto_expose(self)

            #normal number tile
            else:                                       
                self['fg'] = self.colors[int(self.tileDisplay)]
                self['bg'] = self.fgbg[2]
                self['relief'] = 'sunken'
                self['text'] = self.tileDisplay
                self.isExposed = True
        self.master.winning_game()


    def turn_mine_red(self):
        '''self.turn_mine_red() -> None
        makes the mine red when a mine square is exposed'''
        self['bg'] = '#555453' #00AFA4
        self['fg'] = 'white'
        self['text'] = '◉'

    def is_exposed(self):
        '''self.is_exposed() -> Bool
        returns True if the square has been exposed'''
        return self.isExposed

    def get_column(self):
        '''self.get_column -> Int
        gets the column cooridinate'''
        return self.coords[0]

    def get_row(self):
        '''self.get_row() -> Int
        gets the row cooridinate'''
        return self.coords[1]

class MineField(Frame):
    '''a grid where all the Tiles are stored'''
    
    def __init__(self,master,rows=12,columns=10,mines=15):
        '''MineField(master, rows=12, columns=10, mines=15) -> MineField object
        initializes a MineField'''
        Frame.__init__(self,master,bg='black')
        self.grid()

        #initialize vars
        #mines
        self.mines = []             #list of all mines
        self.mineCoords = []        #coords of all mines
        self.mineCount = 0          #num of mines in the game

        #tiles
        self.tiles = []             #list of all tiles
        self.tileCoords = []        #coords of all non-mine tiles
        self.tilesAndCoords = {}    #dictionary; key=coords, value=Tile object

        #game states
        self.lost = False
        self.hasWon = False
        self.pressedStart = False

        #mineCount label
        self.mineCountLabel = Label(text= str(mines), font=('Arial', 18))
        self.mineCountLabel.grid(row=rows+1, columnspan = columns)
        
        #randomly generating mine placement
        while self.mineCount != mines:
            #randomly generate coords
            mineCoord = (0, 0) #enter while loop
            while mineCoord == (0, 0): #so no mine in top left
                row = random.randint(0, rows - 1)
                column = random.randint(0, columns - 1)
                mineCoord = (column, row)
            if mineCoord not in self.mineCoords:
                self.mineCoords.append(mineCoord)
                self.mines.append(Tile(self, column, row, '◎'))
                self.mineCount += 1

        #find the number of adjacent mine tiles   
        for row in range(rows):
            for column in range(columns):
                if (column, row) not in self.mineCoords:
                    numSurroundingMines = 0
                    adjacentTiles = [(column - 1, row - 1), (column, row - 1), (column + 1, row - 1),
                                     (column - 1, row),     (column + 1, row),
                                     (column - 1, row + 1), (column, row + 1), (column + 1, row + 1)]
                    for tile in adjacentTiles:
                        if tile in self.mineCoords: #is a mine
                            numSurroundingMines += 1
                    thisTile = Tile(self, column, row, numSurroundingMines)
                    self.tiles.append(thisTile)
                    self.tileCoords.append((column, row))
                    self.tilesAndCoords.update({(column, row) : thisTile})

        #initialize top left tile
        tileStart = self.tilesAndCoords.get((0,0))
        tileStart['bg'] = '#2C2B2B'
        tileStart['fg'] = '#CECFC9'
        tileStart['text'] = '☆'

    def get_pressed_start(self):
        '''self.get_pressed_start() -> Bool
        returns True if self.pressedStart is true (if
        top left corner has been clicked)'''
        return self.pressedStart

    def mine_count_change(self, num):
        '''self.mine_count_change(num) -> None
        updates minecount and minecount label'''
        self.mineCount += num
        self.mineCountLabel['text'] = str(self.mineCount)
        

    def expose_all_mines(self):
        '''self.expose_all_mines() -> None
        exposes all the mines if game lost
        unbinds all keys, buttons, clicks, etc'''
        for mine in self.mines:         #turns mines red and unbinds
            mine.turn_mine_red()
            mine.unbind('<Button-1>')
            mine.unbind('<Button-2>')
            mine.unbind('<Button-3>')
        for tile in self.tiles:         #unbinds
            tile.unbind('<Button-1>')
            tile.unbind('<Button-2>')
            tile.unbind('<Button-3>')
        self.lost = True

    def winning_game(self):
        '''self.winning_game() -> None
        checks if game has been won
        if it has, triggers endgame sequence'''
        if not self.lost and not self.hasWon:
            for tile in self.tiles:
                if not tile.isExposed:
                    return  #break
            self.hasWon = True  #so message doesn't trigger more than once
            messagebox.showinfo('Minesweeper','Congratulations -- you won!',parent=self)

    def auto_expose(self, tile):
        '''self.auto_expose(tile) -> None
        auto-exposes cells around a 'zero' tile '''
        if tile.tileDisplay == 0 and not tile.is_exposed():
            tile.isExposed=True                         #terminal condition activated 
            adjTiles = self.locate_adjacents(tile)      #find all adjacent tiles
            for tile in adjTiles:
                if not isinstance(tile, type(None)):    #remove type errors
                    if not tile.is_exposed():           #for any not yet exposed
                        tile.expose_tile(self, True)
                        self.auto_expose(tile)
                

    def locate_adjacents(self, tile):
        '''self.locate_adjacents(tile) -> List
        list of all adjacent tiles'''
        c = tile.get_column()
        r = tile.get_row()
        adjacentCoords = [(c-1, r-1), (c, r-1), (c+1, r-1),
                            (c-1, r), (c+1, r),
                            (c-1, r+1), (c, r+1), (c+1, r+1)]
        adjacentCoords = [coord for coord in adjacentCoords if coord in self.tileCoords] #removes any coords off the grid
        adjacentTiles = [self.tilesAndCoords.get(coords) for coords in adjacentCoords]   #converts each coord pair to it's tile
        return(adjacentTiles)
        
def play_retro_diner_minesweeper(rows=12,columns=10,mines=15):
    '''plays minesweeper'''
    root = Tk()
    root.title('Minesweeper')
    ms = MineField(root,rows,columns,mines)
    root.mainloop()

play_retro_diner_minesweeper(15, 15, 20)
