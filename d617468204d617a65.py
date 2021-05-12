# Name: Math Maze
# Author: G.G.Otto
# Date: 3/18/21
# Version: 1.0
#
# Generator made by CaptainFlint
#

from tkinter import *
import random

class MazeImage:
    '''represents an image for the maze'''

    def __init__(self, master, images, pos, tag="all", full='#916135', hidable=False):
        '''MazeImage(master, images, pos, tags, full, hidable) -> MazeImage
        constructs the maze image'''
        if len(images) == 0:
            raise ValueError("must give at least one image for MazeImage")
        if isinstance(images, str):
            images = [images]
            
        self.pos = pos
        self.master = master
        self.hidden = False
            
        self.images = [PhotoImage(file=f"assests/images/maze/{image}") for image in images]
        self.current = 0
        self.id = str(random.random())
        self.id2 = str(random.random())
        self.tag = tag
        self.pos = pos
        self.full = full

        self.master.create_image(self.pos, image=self.images[0], tag=(self.id, self.tag))
        self.animating = True

        self.hidable = hidable
        self.hidden = False
        self.set_hidden(False)

    def clicked(self, pos, cell=None, player=None):
        '''MazeImage.clicked(pos) -> bool
        returns if pos in on event'''
        over = cell != None and ((abs(cell[0]-player[0]) <= 1 and cell[1] == player[1]) or \
            (abs(cell[1]-player[1]) <= 1 and cell[0] == player[0]))
        return over and self.pos[0]-25 <= pos[0] <= self.pos[0]+25 and self.pos[1]-25 <= pos[1] <= self.pos[1]+25

    def set_hidden(self, boolean):
        '''MazeImage.set_hidden(boolean) -> None
        sets if the cell is hidden or not'''
        if not self.hidable:
            return
        
        if boolean and not self.hidden:
            self.master.create_rectangle(self.pos[0]-25, self.pos[1]-25, self.pos[0]+25,
                self.pos[1]+25, outline=self.full, fill=self.full, tag=("hide", self.id2, self.tag))
        elif not boolean:
            self.master.delete(self.id2)

    def root(self):
        '''MazeImage.root() -> Tk
        returns the root'''
        if isinstance(self, Maze): return self.get_master()
        elif isinstance(self.master.get_master(), Tk): return self.master.get_master()
        else: return self.master.get_master().get_master().get_root()

    def move(self, x, y):
        '''MazeImage.move(x,y) -> None
        moves the images'''
        self.pos = self.pos[0] + x, self.pos[1] + y

    def set_images(self, images):
        '''MazeImage.set_images(images) -> None
        sets the new sequence of images'''
        if isinstance(images, str):
            images = [images]
        self.images = [PhotoImage(file=f"assests/images/maze/{image}") for image in images]
        self.switch(0)

    def get_current(self):
        '''MazeImage.get_current() -> str
        returns the current image'''
        return self.images[self.current]

    def switch(self, index=None):
        '''MazeImage.switch(index=None) -> None
        switches image to image at index. if index not given, switches to next one in line'''
        if index == None:
            index = (self.current + 1)%len(self.images)
        
        self.master.delete(self.id)
        self.master.create_image(self.pos, image=self.images[self.current], tag=(self.id, self.tag))
        self.current = index
        self.master.tag_raise(self.id2, self.id)
        self.master.tag_raise("player", "all")
        self.master.tag_raise("vision", "all")

    def display(self, image):
        '''MazeImage.display(image) -> None
        stops animations and displays image'''
        self.stop()
        self.master.delete(self.id)
        self.image = PhotoImage(file=f"assests/images/maze/{image}")
        self.master.create_image(self.pos, image=self.image, tag=(self.id, self.tag))
        self.master.tag_raise(self.id2, self.id)
        self.master.tag_raise("player", "all")
        self.master.tag_raise("vision", "all")
        
    def animate(self, time, start=True):
        '''MazeImage.animate(time) -> None
        animates through images'''
        if start:
            self.animating = True
        if not self.animating:
            return
        
        self.switch()
        self.root().after(time, lambda: self.animate(time, False))

    def stop(self):
        '''MazeImage.stop() -> None
        stops animating'''
        self.animating = False
    
class Maze(Canvas):
    '''represents the maze'''

    def __init__(self, master, width, height, size, command, command2, empty="#fff", full="#333",
        chests=10, doors=10, monsters=10, saved=None):
        '''Maze(MathMazeMaze, int, int, int, method, str, str, int, int, int, str) -> Maze
        constructs the maze
        size is the width of the blocks
        empty, full are color strings'''
        Canvas.__init__(self, master, width=400, height=400, highlightthickness=0, bg=full)
        self.master = master

        if saved != None: saved = saved.split("\n")
        self.width = width
        self.height = height
        self.command = command
        self.command2 = command2
        self.size = size
        self.empty = empty
        self.full = full
        self.generator = WilsonMazeGenerator(self, width, height)
        self.generate(saved)

        # maze attributes
        self.chests = {}
        self.doors = {}
        self.good = []
        self.bad = []
        self.speeds = (300, 200, 400, 500, 600, 400)
        self.monsters = {}
        self.deadends = []
        self.chestNum = chests
        self.doorNum = doors
        self.monsterNum = monsters
        self.monsterNames = ["", "skeleton", "bat", "troll", "crab", "frog"]
        
        for pos in self.cells:
            if self.maze[pos[0]][pos[1]] == 1:
                self.good.append(pos)
            else:
                self.bad.append(pos)
        
        if saved == None:
            self.activate_no_save()
        else:
            self.activate_save(saved)

        # vision
        self.vision = PhotoImage(file="assests/images/maze/vision.png")
        self.create_image(200, 200, image=self.vision, tag="vision")
        
        self.player = MazeImage(self, [f"play{i+1}_left.png" for i in range(2)], (200,200))
        self.player.set_hidden(False)

        if saved == None:
            self.player.animate(400)
            self.move_to(*random.choice(self.positions))
        else:
            pos = saved[0].split()
            self.move_to(int(pos[0]), int(pos[1]))
        
        self.tag_raise("player", "all")
        self.tag_raise("vision", "all")
        self.last = None

        self.doorHides = self.check_doors()

        for cell in self.doorHides:
            if len(self.doorHides[cell]) > 0:
                self.itemconfigure(self.blocks[cell], fill=full, outline=full)
                
        for monster in self.monsters:
            if len(self.doorHides[monster]) > 0:
                self.monsters[monster][0].set_hidden(True)
        for chest in self.chests:
            if len(self.doorHides[chest]) > 0:
                self.chests[chest][0].set_hidden(True)
        for door in self.doors:
            if len(self.doorHides[door]) > 1:
                self.doors[door].set_hidden(True)

        self.bind("<Button-1>", self.click)
        self.bind("<Motion>", self.check_hand)
        self.paused = saved != None

    def string(self, problems):
        '''Maze.string(dict) -> str
        converts maze to str'''
        output = str(self.pos[0]) + " " + str(self.pos[1]) + "\n"

        # add maze
        for row in self.maze[:]:
            for cell in row:
                output += str(cell)
            output += " "
        output += "\n"

        # add chests
        for chest in self.chests:
            output += str(chest[0]) + "-" + str(chest[1]) + "-" + self.chests[chest][1]
            if len(self.chests[chest]) == 3:
                output += "-opened"
            else:
                output += "-closed"
            if chest in problems:
                output += "-{}-{}".format(*problems[chest].get_problem()).replace(" ", "_")
                
            output += " "
                
        output += "\n"

        # add doors
        for door in self.doors:
            output += str(door[0]) + "-" + str(door[1])
            if door in self.deadends:
                output += "-closed"
            else:
                output += "-open"
            if door in problems:
                output += "-{}-{}".format(*problems[door].get_problem()).replace(" ", "_")
                
            output += " "
        output += "\n"

        # add monsters
        for monster in self.monsters:
            output += str(monster[0]) + "-" + str(monster[1]) + "-" + str(self.monsters[monster][1])
            if monster in self.deadends:
                output += "-alive"
            else:
                output += "-dead"
            if monster in problems:
                output += "-{}-{}".format(*problems[monster].get_problem()).replace(" ", "_")
                
            output += " "
        
        return output

    def get_maze(self):
        '''Maze.get_maze() -> list
        returns the grid for the maze'''
        return self.maze

    def get_monsters(self):
        '''Maze.get_monsters() -> dict
        returns all the monsters'''
        return self.monsters

    def get_doors(self):
        '''Maze.get_doors() -> dict
        returns all the doors'''
        return self.doors

    def get_chests(self):
        '''Maze.get_chests() -> dict
        returns all the chests'''
        return self.chests

    def get_last(self):
        '''Maze.get_last() -> str
        returns the last item destroyed/opened'''
        return self.last

    def get_master(self):
        '''Maze.get_master() -> AMCMazeMaze
        returns the master'''
        return self.master

    def get_deadends(self):
        '''Maze.get_deadends() -> list
        returns a list of all deadends'''
        return self.deadends

    def pause(self):
        '''Maze.pause() -> None
        pauses the maze'''
        if self.paused:
            return
        
        for event in ("Up", "Right", "Down", "Left", "w", "d", "s", "a"):
            self.unbind_all(f"<Key-{event}>")

        self.unbind("<Button-1>")

        for monster in self.monsters:
            self.monsters[monster][0].stop()
        self.player.stop()
        self.paused = True

    def play(self):
        '''Maze.play() -> None
        starts up the maze'''
        if not self.paused:
            return

        self.bind_all("<Key-Up>", lambda e: self.move_dir(0))
        self.bind_all("<Key-Right>", lambda e: self.move_dir(1))
        self.bind_all("<Key-Down>", lambda e: self.move_dir(2))
        self.bind_all("<Key-Left>", lambda e: self.move_dir(3))
        self.bind_all("<Key-w>", lambda e: self.move_dir(0))
        self.bind_all("<Key-d>", lambda e: self.move_dir(1))
        self.bind_all("<Key-s>", lambda e: self.move_dir(2))
        self.bind_all("<Key-a>", lambda e: self.move_dir(3))
        self.bind("<Button-1>", self.click)

        for monster in self.monsters:
            if monster in self.deadends:
                self.monsters[monster][0].animate(self.speeds[self.monsters[monster][1]-1])
        self.player.animate(400)
        self.paused = False

    def activate_no_save(self):
        '''Maze.activate_no_save() -> None
        activates the maze with nothing saved'''
        self.bind_all("<Key-Up>", lambda e: self.move_dir(0))
        self.bind_all("<Key-Right>", lambda e: self.move_dir(1))
        self.bind_all("<Key-Down>", lambda e: self.move_dir(2))
        self.bind_all("<Key-Left>", lambda e: self.move_dir(3))
        self.bind_all("<Key-w>", lambda e: self.move_dir(0))
        self.bind_all("<Key-d>", lambda e: self.move_dir(1))
        self.bind_all("<Key-s>", lambda e: self.move_dir(2))
        self.bind_all("<Key-a>", lambda e: self.move_dir(3))

        # add monsters
        self.positions = self.good[:]
        for i in range(self.monsterNum):
            monster = random.choice(self.positions)
            self.positions.remove(monster)
            monsterType = random.randint(1,5)
            monsterfig = MazeImage(self, [f"monster{monsterType}_1.png", f"monster{monsterType}_2.png"],
                self.cells[monster], "cell", self.full, True)
            self.monsters[monster] = monsterfig, monsterType
            monsterfig.animate(self.speeds[monsterType-1])
            self.deadends.append(monster)

        # doors
        for i in range(self.doorNum):
            door = random.choice(self.positions)
            self.positions.remove(door)
            self.doors[door] = MazeImage(self, ["door_closed.png", "door_open.png"], self.cells[door], "cell", self.full, True)
            self.deadends.append(door)

        # lay chests
        for i in range(self.chestNum):
            chest = random.choice(self.positions)
            self.positions.remove(chest)
            self.chests[chest] = MazeImage(self, "chest_closed.png", self.cells[chest], "cell", self.full, True), \
                random.choice(["iron", "iron", "iron", "iron", "gold", "gold", "gold", "ruby",
                    "ruby", "emerald", "emerald", "sapphire", "sapphire", "diamond"])

    def activate_save(self, saved):
        '''Maze.activate_save(saved) -> None
        activates the maze with save'''
        # add chests
        for chest in saved[2].split():
            chest = chest.split("-")
            pos = int(chest[0]), int(chest[1])

            # closed chest
            if chest[3] == "closed":
                self.chests[pos] = MazeImage(self, "chest_closed.png", self.cells[pos], "cell", self.full, True), chest[2]
                
            # open chest
            else:
                self.chests[pos] = MazeImage(self, chest[2]+".png", self.cells[pos], "cell", self.full, True), chest[2], None

        # add doors
        for door in saved[3].split():
            door = door.split("-")
            pos = int(door[0]), int(door[1])
            
            # closed door
            if door[2] == "closed":
                self.doors[pos] = MazeImage(self, ["door_closed.png", "door_open.png"], self.cells[pos], "cell", self.full, True)
                self.deadends.append(pos)

            # open door
            else:
                self.doors[pos] = MazeImage(self, "door_open.png", self.cells[pos], "cell", self.full, True)

        # add monsters
        for monster in saved[4].split():
            monster = monster.split("-")
            pos = int(monster[0]), int(monster[1])
            monsterType = int(monster[2])
            monsterfig = MazeImage(self, [f"monster{monsterType}_1.png", f"monster{monsterType}_2.png"],
                self.cells[pos], "cell", self.full, True)
            self.monsters[pos] = monsterfig, monsterType

            if monster[3] == "alive":
                self.deadends.append(pos)
            else:
                monsterfig.display(f"monster{monsterType}_3.png")

    def generate(self, saved):
        '''Maze.generate(saved) -> None
        generates the maze'''
        if saved == None:
            self.generator.generate_maze()
            self.maze = self.generator.get_grid()
        else:
            self.maze = []
            for row in saved[1].split():
                mazeRow = []
                for cell in row:
                    mazeRow.append(int(cell))
                self.maze.append(mazeRow)
        
        self.width = len(self.maze[0])
        self.height = len(self.maze)
        startx = 200-self.width/2*self.size
        starty = 200-self.height/2*self.size
        self.cells = {}
        self.blocks = {}
        self.pos = self.width//2, self.height//2

        for y in range(len(self.maze[0])):
            for x in range(len(self.maze)):
                self.cells[x,y] = startx+x*self.size+self.size/2, starty+y*self.size+self.size/2
                color = self.empty
                if self.maze[x][y] == 0:
                    color = self.full
                self.blocks[x,y] = self.create_rectangle(startx+x*self.size, starty+y*self.size, startx+(x+1)*self.size,
                    starty+(y+1)*self.size, fill=color, outline=color, tag=(str(x)+" "+str(y), "cell", "maze"))

    def move_to(self, x, y):
        '''Maze.move_to(center) -> None
        moves the center to x,y'''
        xpos = int(-self.cells[x,y][0]+self.cells[self.pos][0])
        ypos = int(-self.cells[x,y][1]+self.cells[self.pos][1])
        self.move("cell", xpos, ypos)
        for monster in self.monsters:
            self.monsters[monster][0].move(xpos, ypos)
        for door in self.doors:
            self.doors[door].move(xpos, ypos)
        for chest in self.chests:
            self.chests[chest][0].move(xpos, ypos)
        self.pos = x,y

    def move_dir(self, direction):
        '''Maze.move_dir(direction) -> None
        moves the player to in direction'''
        if not 0 <= direction < 4:
            return

        x,y = None, None
        if direction == 0:
            x,y = self.pos[0], self.pos[1]-1
        elif direction == 1:
            x,y = self.pos[0]+1, self.pos[1]
            self.player.set_images([f"play{i+1}_right.png" for i in range(2)])
        elif direction == 2:
            x,y = self.pos[0], self.pos[1]+1
        else:
            x,y = self.pos[0]-1, self.pos[1]
            self.player.set_images([f"play{i+1}_left.png" for i in range(2)])
            
        if (x,y) in self.good and (x,y) not in self.deadends:
            self.move_to(x,y)

    def check_doors(self):
        '''Maze.doors() -> None
        checks if door between cells and player'''
        dirs = {}
        doorsAttached = {}
        for cell in self.good:
            dirs[cell] = self.get_dirs(cell)
            doorsAttached[cell] = []

        doors = []
        blocks = [self.pos]
        current = random.choice(dirs[self.pos])
        dirs[current].remove(self.pos)
        dirs[self.pos].remove(current)

        while True:
            if current in self.doors and current in self.deadends:
                doors.append(current)
            doorsAttached[current] = doors.copy()

            blocks.append(current)
            if len(blocks) == len(self.good):
                break
                
            if len(dirs[current]) == 0:
                for cell in blocks:
                    if len(dirs[cell]) > 0:
                        current = cell
                        doors = doorsAttached[current].copy()
                        break

            nextCell = random.choice(dirs[current])
            dirs[current].remove(nextCell)
            dirs[nextCell].remove(current)
            current = nextCell

        return doorsAttached

    def get_dirs(self, cell):
        '''Maze.get_dirs(cell) -> dict
        returns the directions branching off cell'''
        directions = []
        dirs = (cell[0]-1,cell[1]), (cell[0],cell[1]-1), (cell[0]+1,cell[1]), (cell[0],cell[1]+1)
        for i in range(4):
            if dirs[i] in self.good:
                directions.append(dirs[i])
        return directions

    def open_door(self, cell):
        '''Maze.open_door() -> None
        opens the door at cell'''
        if not (cell in self.doors and cell in self.deadends):
            return

        door = self.doors[cell]
        self.deadends.remove(cell)
        door.display("door_open.png")
        
        # unhide all cells
        for cell2 in self.doorHides:
            if cell in self.doorHides[cell2]:
                self.doorHides[cell2].remove(cell)

                if len(self.doorHides[cell2]) == 0:
                    self.itemconfigure(self.blocks[cell2], fill=self.empty, outline=self.empty)
                    
                    if cell2 in self.monsters and self.doors:
                        self.monsters[cell2][0].set_hidden(False)

                    elif cell2 in self.chests:
                        self.chests[cell2][0].set_hidden(False)

                elif len(self.doorHides[cell2]) == 1 and cell2 in self.doors:
                    self.itemconfigure(self.blocks[cell2], fill=self.empty, outline=self.empty)
                    self.doors[cell2].set_hidden(False)

        self.last = "door"
        self.command2(cell)

    def destroy_monster(self, cell):
        '''Maze.destroy_monster(cell) -> None
        destroys the monster at cell'''
        if not (cell in self.monsters and cell in self.deadends):
            return

        self.deadends.remove(cell)
        self.monsters[cell][0].display(f"monster{self.monsters[cell][1]}_3.png")
        self.last = self.monsterNames[self.monsters[cell][1]]
        self.command2(cell)

    def open_chest(self, cell):
        '''Maze.open_chest(cell) -> None
        opens the chest at cell'''
        if not (cell in self.chests and len(self.chests[cell][1]) != 3):
            return

        self.last = self.chests[cell][1]
        self.chests[cell][0].display(self.last+".png")
        self.chests[cell] = *self.chests[cell], None
        self.command2(cell)

    def click(self, event):
        '''Maze.click(event) -> (x,y)
        returns the row/column of click
        if click not on monster/chest/door returns None'''
        pos = event.x, event.y
        for cell in self.cells:
            if cell in self.doors and self.doors[cell].clicked(pos, cell, self.pos) and cell in self.deadends \
                and self.command(cell):
                self.open_door(cell)
            elif cell in self.monsters and self.monsters[cell][0].clicked(pos, cell, self.pos) and cell in self.deadends \
                 and self.command(cell):
                self.destroy_monster(cell)
            elif cell in self.chests and self.chests[cell][0].clicked(pos, cell, self.pos) and self.chests[cell][1] != None \
                 and self.command(cell):
                self.open_chest(cell)

    def check_hand(self, event):
        '''Maze.check_hand(event) -> None
        checks if hand is over item'''
        pos = event.x, event.y
        for door in self.doors:
            if door in self.deadends and self.doors[door].clicked(pos, door, self.pos):
                self["cursor"] = "hand2"
                return
            
        for chest in self.chests:
            if len(self.chests[chest]) != 3 and self.chests[chest][0].clicked(pos, chest, self.pos):
                self["cursor"] = "hand2"
                return
            
        for monster in self.monsters:
            if monster in self.deadends and self.monsters[monster][0].clicked(pos, monster, self.pos):
                self["cursor"] = "hand2"
                return

        self["cursor"] = ""

## Maze Generator
## Wilson's Loop Erased Random Walk Algorithm
## Author: CaptainFlint

"""
Wilson's Algorithm is an algorithm to generate a
uniform spanning tree using a loop erased random walk.
Algorithm:
1. Choose a random cell and add it to the visited list
2. Choose another random cell (Don’t add to visited list).
   This is the current cell.
3. Choose a random cell that is adjacent to the current cell
   (Don’t add to visited list). This is your new current cell.
4. Save the direction that you traveled on the previous cell.
5. If the current cell is not in the visited cells list:
   a. Go to 3
6. Else:
   a. Starting at the cell selected in step 2, follow the arrows
      and remove the edges that are crossed.
   b. Add all cells that are passed into the visited list
7. If all cells have not been visited
   a. Go to 2
Source: http://people.cs.ksu.edu/~ashley78/wiki.ashleycoleman.me/index.php/Wilson's_Algorithm.html
"""

import random

class WilsonMazeGenerator:
    """Maze Generator using Wilson's Loop Erased Random Walk Algorithm"""

    def __init__(self,maze,height,width):
        """WilsonMazeGenerator(maze,int,int) -> WilsonMazeGenerator
        Creates a maze generator with specified width and height.
        width: width of generated mazes
        height: height of generated mazes"""
        self.maze = maze
        self.width = 2*(width//2) + 1   # Make width odd
        self.height = 2*(height//2) + 1 # Make height odd

        # grid of cells
        self.grid = [[0 for j in range(self.width)] for i in range(self.height)]

        # declare instance variable
        self.visited = []    # visited cells
        self.unvisited = []  # unvisited cells
        self.path = dict()   # random walk path

        # valid directions in random walk
        self.directions = [(0,1),(1,0),(0,-1),(-1,0)]

        # indicates whether a maze is generated
        self.generated = False

        # shortest solution
        self.solution = []
        self.showSolution = False
        self.start = (self.height-1,0)
        self.end = (0,self.width-1)

    def __str__(self):
        """WilsonMazeGenerator.__str__() -> str
        outputs a string version of the grid"""
        out = "##"*(self.width+1)+"\n"
        for i in range(self.height):
            out += "#"
            for j in range(self.width):
                if self.grid[i][j] == 0:
                    out += "##"
                else:
                    if not self.showSolution:
                        out += "  "
                    elif (i,j) in self.solution:
                        out += "**"
                    else:
                        out += "  "
            out += "#\n"
        return out + "##"*(self.width+1)

    def get_grid(self):
        """WilsonMazeGenerator.get_grid() -> list
        returns the maze grid"""
        return self.grid

    def get_solution(self):
        """WilsonMazeGenerator.get_solution() -> list
        Returns the solution to the maze as a list
        of tuples"""
        return self.solution

    def show_solution(self,show):
        """WilsonMazeGenerator.show_solution(boolean) -> None
        Set whether WilsonMazeGenerator.__str__() outputs the
        solution or not"""
        self.showSolution = show
    
    def generate_maze(self):
        """WilsonMazeGenerator.generate_maze() -> None
        Generates the maze according to the Wilson Loop Erased Random
        Walk Algorithm"""
        # reset the grid before generation
        self.initialize_grid()

        # choose the first cell to put in the visited list
        # see Step 1 of the algorithm.
        current = self.unvisited.pop(random.randint(0,len(self.unvisited)-1))
        self.visited.append(current)
        self.cut(current)

        # loop until all cells have been visited
        while len(self.unvisited) > 0:
            # choose a random cell to start the walk (Step 2)
            first = self.unvisited[random.randint(0,len(self.unvisited)-1)]
            current = first
            # loop until the random walk reaches a visited cell
            while True:
                # choose direction to walk (Step 3)
                dirNum = random.randint(0,3)
                # check if direction is valid. If not, choose new direction
                while not self.is_valid_direction(current,dirNum):
                    dirNum = random.randint(0,3)
                # save the cell and direction in the path
                self.path[current] = dirNum
                # get the next cell in that direction
                current = self.get_next_cell(current,dirNum,2)
                if (current in self.visited): # visited cell is reached (Step 5)
                    break

            current = first # go to start of path
            # loop until the end of path is reached
            while True:
                # add cell to visited and cut into the maze
                self.visited.append(current)
                self.unvisited.remove(current) # (Step 6.b)
                self.cut(current)

                # follow the direction to next cell (Step 6.a)
                dirNum = self.path[current]
                crossed = self.get_next_cell(current,dirNum,1)
                self.cut(crossed) # cut crossed edge

                current = self.get_next_cell(current,dirNum,2)
                if (current in self.visited): # end of path is reached
                    self.path = dict() # clear the path
                    break
                
        self.generated = True

    def solve_maze(self, start=None, end=None):
        """WilsonMazeGenerator.solve_maze(start=None, end=None) -> None
        Solves the maze according to the Wilson Loop Erased Random
        Walk Algorithm"""
        # if there is no maze to solve, cut the method
        if not self.generated:
            return

        if start == None:
            start = self.start
        if end == None:
            end = self.end

        # initialize with empty path at starting cell
        self.path = dict()
        current = start
        last = -1

        # loop until the ending cell is reached
        while True:
            dirs = []
            for dirNum in range(4):                
                adjacent = self.get_next_cell(current,dirNum,1)
                if self.is_valid_direction(current,dirNum):
                    hasWall = (self.grid[adjacent[0]][adjacent[1]] == 0)
                    if not hasWall:
                        dirs.append(dirNum)
            if len(dirs) > 1:
                for dirNum in dirs:
                    if last == dirNum:
                        dirs.remove(dirNum)
                        break

            dirNum = random.choice(dirs)

            # add cell and direction to path
            self.path[current] = dirNum

            # get next cell
            current = self.get_next_cell(current,dirNum,2)
            last = (dirNum + 2)%4
            
            if current == end: 
                break # break if ending cell is reached

        # go to start of path
        self.solution = []
        current = start
        self.solution.append(current)
        # loop until end of path is reached
        while not (current == end):
            dirNum = self.path[current] # get direction
            # add adjacent and crossed cells to solution
            crossed = self.get_next_cell(current,dirNum,1)
            current = self.get_next_cell(current,dirNum,2)
            self.solution.append(crossed)
            self.solution.append(current)

        self.path = dict()
        return self.solution
                
    ## Private Methods ##
    ## Do Not Use Outside This Class ##
                
    def get_next_cell(self,cell,dirNum,fact):
        """WilsonMazeGenerator.get_next_cell(tuple,int,int) -> tuple
        Outputs the next cell when moved a distance fact in the the
        direction specified by dirNum from the initial cell.
        cell: tuple (y,x) representing position of initial cell
        dirNum: int with values 0,1,2,3
        fact: int distance to next cell"""
        dirTup = self.directions[dirNum]
        return (cell[0]+fact*dirTup[0],cell[1]+fact*dirTup[1])

    def is_valid_direction(self,cell,dirNum):
        """WilsonMazeGenerator(tuple,int) -> boolean
        Checks if the adjacent cell in the direction specified by
        dirNum is within the grid
        cell: tuple (y,x) representing position of initial cell
        dirNum: int with values 0,1,2,3"""
        newCell = self.get_next_cell(cell,dirNum,2)
        tooSmall = newCell[0] < 0 or newCell[1] < 0
        tooBig = newCell[0] >= self.height or newCell[1] >= self.width
        return not (tooSmall or tooBig)

    def initialize_grid(self):
        """WilsonMazeGenerator.initialize_grid() -> None
        Resets the maze grid to blank before generating a maze."""
        for i in range(self.height):
            for j in range(self.width):
                self.grid[i][j] = 0
                
        # fill up unvisited cells
        for r in range(self.height):
            for c in range(self.width):
                if r % 2 == 0 and c % 2 == 0:
                    self.unvisited.append((r,c))

        self.visited = []
        self.path = dict()
        self.generated = False

    def cut(self,cell):
        """WilsonMazeGenerator.cut(tuple) -> None
        Sets the value of the grid at the location specified by cell
        to 1
        cell: tuple (y,x) location of where to cut"""
        self.grid[cell[0]][cell[1]] = 1
