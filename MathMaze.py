# Name: MathMaze (AMC Problem Generator)
# Author: G.G.Otto
# Version: 1.0
# Date: 3/13/21

from tkinter import *
from tkinter import messagebox as msg
import d617468204d617a65 as maze
import random

class ScrolledCanvas(Frame):
    '''represents a scrolled canvas'''

    def __init__(self, master, owidth, oheight, iwidth, iheight, **args):
        '''ScrolledCanvas(master, owidth, oheight, iwidth, iheight, **args) -> ScrolledCanvas
        constructs the scrolled canvas with outer-width/height and inner-width/height'''
        Frame.__init__(self, master, bg="white")
        
        scrollregion = 0, 0, max(owidth, iwidth), max(oheight, iheight)
        self.canvas = Canvas(self, scrollregion=scrollregion, width=owidth-20, height=oheight-20, **args)
        self.canvas.grid(row=0, column=0)

        self.oheight = oheight
        self.owidth = owidth
        self.iheight = iheight
        self.iwidth = iwidth
        
        if iwidth > owidth:
            self.xscroll = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview, width=20)
            self.canvas["xscrollcommand"] = self.xscroll.set
            self.xscroll.grid(row=1, column=0, sticky=E+W)
        else:
            self.canvas["height"] = int(self.canvas["height"])+20

        if iheight > oheight:
            self.yscroll = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=20)
            self.canvas["yscrollcommand"] = self.yscroll.set
            self.yscroll.grid(row=0, column=1, sticky=N+S)
        else:
            self.canvas["width"] = int(self.canvas["width"])+20
        
    def get_canvas(self):
        '''ScrolledCanvas.get_canvas() -> Canvas
        returns the canvas'''
        return self.canvas

class MathMazeButton(Button):
    '''represents a submit button'''

    def __init__(self, master, image, hover, command=None, bg="#f00", **kwargs):
        '''MathMazeButton(master, image, hover, **kwargs) -> MathMazeButton
        constructs the submit button'''
        self.normImage = PhotoImage(file=image)
        self.hover = PhotoImage(file=hover)
        Button.__init__(self, master, image=self.normImage, relief=FLAT, overrelief=FLAT, bg=bg,
            command=command, cursor="hand2", bd=0, **kwargs, highlightthickness=0)

        self.bind("<Enter>", self.enter)
        self.bind("<Leave>", self.leave)

    def enter(self, event):
        '''MathMazeButton.enter(event) -> None
        deals with image change for hover'''
        self.config(image=self.hover)
        self.image = self.hover

    def leave(self, event):
        '''MathMazeButton.leave(event) -> None
        deals with image change not on hover'''
        self.config(image=self.normImage)
        self.image = self.normImage

class MathMazeMazeSection(Canvas):
    '''represents a section in the maze list'''

    def __init__(self, master, width, height):
        '''MathMazeMazeSection(master) -> MathMazeMazeSection
        constructs the section for maze in maze list'''
        Canvas.__init__(self, master, highlightthickness=0, bg="#333", width=width, height=height)
        self.master = master

        self.create_text(width/2, 100, font=("Arial", 40, "bold"), text="", fill="#222", tags=("h1","text"))
        self.create_text(width/2, 140, font=("Arial", 14, "italic"), text="", fill="#222", tags=("h2","text"))
        self.create_text(width/2, 220, font=("Arial", 16, "bold"), text="", fill="#222", tags=("body","text"))
        self.create_text(width/2, int(self["height"])-13, font=("Arial", 11), fill="#333", text="delete", tag="delete")
        self.tag_bind("delete", "<Button-1>", self.delete_section)

        self.activated = False

    def configure_section(self, h1=None, h2=None, body=None, bg=None, image=None):
        '''MathMazeMazeSection.configure_section(index, h1, h2, body, bg) -> None
        configures the maze list at section'''
        if bg != None:
            self["bg"] = bg
        if h1 != None:
            self.itemconfigure("h1", text=h1)
        if h2 != None:
            self.itemconfigure("h2", text=h2)
        if body != None:
            self.itemconfigure("body", text=body)
        if image != None:
            if image:
                self.image = PhotoImage(file="assests/images/maze_image.png")
                self.create_image(int(self["width"])/2, int(self["height"])/2, image=self.image, tag="image")
                self.tag_raise("text", "image")
            else:
                self.delete("image")

        self.tag_raise("delete", "image")
            
    def is_activated(self):
        '''MathMazeMazeSection.is_activated() -> bool
        returns if section is activated'''
        return self.activated

    def activate(self):
        '''MathMazeMazeSection.activate() -> None
        activates for event use'''
        self.button = MathMazeButton(self, "assests/images/continue.png", "assests/images/continue_hover.png",
            lambda: self.master.button_push(self), "#222")
        self.create_window(int(self["width"])/2, int(self["height"])-40, window=self.button, tag="button")
        self.activated = True

    def delete_section(self, event=None):
        '''MathMazeMazeSection.delete_section(event) -> None
        deletes the section'''
        if not self.activated or not msg.askyesno("MathMaze", message="Are you sure you want to delete this?"):
            return

        self.delete("all")
        self["bg"] = "#333"
        self.create_text(int(self["width"])/2, int(self["height"])/2, text="Deleting...", fill="#2f4", font=("Arial", 20, "italic"))
        self.after(1000, lambda: self.master.delete_section(self))

class MathMazeMazeList(Canvas):
    '''represents a list of mazes on the maze homepage'''

    def __init__(self, master, page):
        '''MathMazeMazeList(master, page) -> MathMazeMazeList
        constructs the maze list for master and mazes'''
        Canvas.__init__(self, master, bg="#222", width=1000, height=400, highlightthickness=0)
        self.page = page
        maxSections = 12
        columns = 3

        self.sections = []
        self.mazes = {}
        self.currentPage = 0
        self.active = 0
        self.pages = 1
        self.columns = columns
        self.navi = [Label(self, text=text[0], anchor=text[1], font=("Arial", 11, "italic"), bg="#222", fg="#2f5") \
            for text in (("<< Previous", W), ("Next >>", E), ("Page 1 of 1", CENTER))]

        self.navi[0]["cursor"] = "hand2"
        self.navi[1]["cursor"] = "hand2"

        self.width, self.height = 280, 300
        for i in range(maxSections):
            section = MathMazeMazeSection(self, self.width, self.height)
            self.sections.append(section)
        self.configure_sections()

        self.navDisabled = [False, False, False]

        # bindings
        self.navi[0].bind("<Button-1>", self.back)
        self.navi[1].bind("<Button-1>", self.next)

        # navigation bar
        self.create_window(100, 375, window=self.navi[0])
        self.create_window(900, 375, window=self.navi[1])
        self.create_window(500, 375, window=self.navi[2])

    def __len__(self):
        '''len(MathMazeMazeList) -> int
        returns the number of mazes in list'''
        return len(self.mazes)

    def get_page(self):
        '''MathMazeMazeList.get_page() -> MathMazeMazeHome
        returns the homepage for the list'''
        return self.page

    def get_mazes(self):
        '''MathMazeMazeList.get_mazes() -> list
        returns a list of mazes'''
        output = []
        for section in self.sections:
            if section in self.mazes:
                output.append(self.mazes[section])
        return output

    def button_push(self, section):
        '''MathMazeMazeList.button_push(section) -> None
        deals with a button push'''
        self.page.switch(self.mazes[section])
        self.pull_up(section)
        self.set_page(0)

    def __add__(self, maze):
        '''MathMazeMazeList + maze -> MathMazeMazeList
        adds a new maze to the list'''
        index = None
        for section in self.sections:
            if not section.is_activated():
                index = self.sections.index(section)
                break

        if index == None: return
        if self.active%3 == 0 and self.active != 0: self.pages += 1
        
        maze.add_to_list(section)
        self.mazes[section] = maze
        section.activate()
        self.pull_up(section)
        self.active += 1
        self.set_page(0)
        return self

    def set_nav_disable(self, index, boolean):
        '''MathMazeMazeList.set_nav_disable(index, boolean) -> None
        sets disable of button on navbar'''
        if boolean == self.navDisabled[index]:
            return

        self.navDisabled[index] = boolean

        if boolean:
            self.navi[index]["fg"] = "#bfb"
        else:
            self.navi[index]["fg"] = "#8f9"

    def configure_sections(self):
        '''MathMazeMazeList.configure_sections() -> None
        configures the first three sections'''
        self.delete("sections")
        for i in range(3):
            width, height = 280, 300
            gap = (1000-width*self.columns)/(self.columns+1)
            self.create_window(width/2+gap+(width+gap)*i, height/2+10, window=self.sections[(i+(self.currentPage)*3)%12], tag="sections")

        # get number of valid pages
        self.navi[2]["text"] = f"Page {self.currentPage+1} of {self.pages}"
        self.numPages = self.active//self.columns+1

    def pull_up(self, section, config=True):
        '''MathMazeMazeList.pull_up(section, config=True) -> None
        places section at the front and configures'''
        self.sections.remove(section)
        self.sections.insert(0, section)
        if config:
            self.configure_sections()

    def set_page(self, page):
        '''MathMazeMazeList.set_page(page) -> None
        sets the page to page'''
        self.currentPage = page
        self.configure_sections()

    def next(self, event=None):
        '''MathMazeMazeList.next(event) -> None
        goes to next page'''
        self.set_page((self.currentPage+1)%self.pages)

    def back(self, event=None):
        '''MathMazeMazeList.back() -> None
        moves to the previous page'''
        self.set_page((self.currentPage-1)%self.pages)

    def delete_section(self, section):
        '''MathMazeMazeList.delete_section(MathMazeMazeSection) -> None
        deletes section from the list'''
        if self.active%3 == 1 and self.pages != 1:
            self.pages -= 1
        self.active -= 1

        if self.currentPage + 1 > self.pages:
            self.back()

        self.page.subtract_maze(self.mazes[section])
        self.mazes.pop(section)

        self.sections.remove(section)
        self.sections.append(MathMazeMazeSection(self, self.width, self.height))
        self.configure_sections()
        
class MathMazeMazeHome(Frame):
    '''represents a frame for the maze menu'''

    def __init__(self, master):
        '''MathMazeMazeHome(master) -> MathMazeMazeHome
        constructs the maze menu frame'''
        Frame.__init__(self, master)
        self.master = master
        self.mazes = []

        self.home = Frame(self, bg="#222")
        self.header = Canvas(self.home, width=1000, height=180, highlightthickness=0, bg="#222")
        self.header.grid(row=0, column=0)

        # create header
        self.header.create_text(500, 35, fill="#4f5", text="MathMaze", tags="header",
            font=("Arial", 25, "bold", "italic"))
        self.plus = Label(self.header, text="+", font=("Arial", 60), bg="#222", fg="#4f2", cursor="hand2")
        self.header.create_window(960, 35, window=self.plus, tags="plus")
        self.header.create_text((500, 90), font=("Arial",14), fill="#8f9", text=master.get_descs()["maze"])
        self.header.create_text(120, 160, font=("Arial", 16, "bold"), text=f"Ongoing Mazes ({len(self.mazes)}):",
            fill="#2f4", tags="ongoing")
        self.hoverplus = Label(self.header, text="Maximum reached", font=("Arial", 11), bg="#222", fg="#8f9")
        self.maxMazes = 12

        # ongoing mazes
        self.pages = MathMazeMazeList(self.home, self)
        self.pages.grid(row=1, column=0)

        self.plus.bind("<Enter>", self.plus_hover)
        self.plus.bind("<Leave>", self.plus_unhover)
        self.plus.bind("<Button-1>", self.add_maze)
                             
        self.frame = self.home
        self.gridded = False
        self.plusVar = StringVar()
        self.numMazes = len(self.mazes)

        self.saved = False

    def saved_mazes(self):
        '''MathMazeMazeHome.saved_mazes() -> None
        adds all the sazed mazes to the page'''
        for maze in self.master.get_mazes():
            self.add_maze(None, False, maze, self.master.get_mazes()[maze])

    def get_master(self):
        '''MathMazeMazeHome.get_master() -> MathMazeFrame
        returns the main game object'''
        return self.master

    def grid(self, **attr):
        '''MathMazeMazeHome.grid(**dict) -> None
        overrides the Frame's grid method'''
        if not self.gridded:
            self.gridded = True
            self.frame.grid()
            Frame.grid(self, **attr)

    def grid_remove(self):
        '''MathMazeMazeHome.grid_remove() -> None
        overrides the Frame's grid method'''
        if self.gridded:
            self.gridded = False
            self.frame.grid_remove()
            Frame.grid_remove(self)

    def plus_hover(self, event=None):
        '''MathMazeMazeHome.plus_hover(event) -> None
        on hover of the plus button'''
        self.plus["fg"] = "#afa"
        if len(self.mazes) == self.maxMazes:
            self.header.create_window(870, 35, window=self.hoverplus, tags="hoverplus")

    def plus_unhover(self, event=None):
        '''MathMazeMazeHome.plus_unhover(event) -> None
        on unhover of the plus button'''
        self.plus["fg"] = "#4f2"
        self.header.delete("hoverplus")

    def add_maze(self, event=None, switch=True, num=None, maze=None):
        '''MathMazeMazeHome.add_maze(event, bool, int, str) -> None
        adds a new maze to the list'''
        if len(self.mazes) == self.maxMazes or (switch and self.plusVar.get() == "wait"):
            return

        # get maze number
        if num == None:
            num = 0
            for mazeNum in self.mazes:
                if mazeNum.get_num() > num:
                    num = mazeNum.get_num()
            num += 1

        self.plusVar.set("wait")
        self.after(500, lambda: self.plusVar.set("go"))
        maze = MathMazeMaze(self.master, self, num, saved=maze, switch=switch)
        self.mazes.append(maze)
        self.numMazes += 1
        self.pages + maze

        self.header.itemconfigure("ongoing", text=f"Ongoing Mazes ({self.numMazes}):")

    def switch(self, frame):
        '''MathMazeMazeHome.switch(frame) -> None
        switchs grid to frame'''
        self.frame.grid_remove()
        self.frame = frame
        self.frame.grid()

    def go_home(self, event=None):
        '''MathMazeMazeHome.go_home(event) -> None
        goes to the home page'''
        self.switch(self.home)

    def subtract_maze(self, maze):
        '''MathMazeMazeHome.subtract_maze(maze) -> None
        removes a maze from the list'''
        self.mazes.remove(maze)
        self.numMazes -= 1
        self.header.itemconfigure("ongoing", text=f"Ongoing Mazes ({self.numMazes}):")

    def save_all_mazes(self, event=None, repeat=False):
        '''MathMazeMazeHome.save_all_mazes() -> None
        saves all the mazes'''
        self.master.get_mazes().clear()
        self.master.save_mazes(True)
        mazes = self.pages.get_mazes()
        mazes.reverse()
        for maze in mazes: self.master.get_mazes()[maze.get_num()] = maze.string()
        self.master.save_mazes()
        if repeat: self.after(5000, lambda: self.save_all_mazes(None, True))
                
class MathMazeMazeProblem(Frame):
    '''represents a problem frame for the maze'''

    def __init__(self, master, maze, problem):
        '''MathMazeMazeProblem(master, maze, problem) -> MathMazeMazeProblem
        constructs the problem on master'''
        Frame.__init__(self, maze.get_home(), bg="white")
        self.master = master
        self.image = PhotoImage(file=f"assests/problems/{problem[0]}/{problem[1]}.png")
        self.scrolled = ScrolledCanvas(self, owidth=1000, oheight=470, iwidth=self.image.width()+30,
            iheight=self.image.height()+55, highlightthickness=0, bg="white")
        self.scrolled.grid(row=1, column=0, columnspan=4)
        self.canvas = self.scrolled.get_canvas()
        self.canvas.create_image((max(int(self.canvas["width"])/2, self.image.width()/2+20), self.image.height()/2+30),
            image=self.image, tag="problem")

        self.current = self.master.get_problems()[problem[0]][problem[1]-1]
        self.maze = maze
        self.problem = problem

        # top bar of problem
        topbarBg = "#00d51a"
        self.topbar = Canvas(self, width=1000, height=30, highlightthickness=0, bg=topbarBg, cursor="hand2")
        self.topbar.grid(row=0, column=0, columnspan=4)
        self.topbar.bind("<Button-1>", self.back_to_maze)

        # problem xp and number
        self.number = self.master.get_problem_num(problem)
        self.numberLabel = Entry(self.topbar, highlightthickness=0, relief=FLAT, fg="black", font=("Arial", 14, "bold"),
            textvariable=StringVar(value=self.number), state="readonly", readonlybackground=topbarBg, width=7)
        self.topbar.create_window((953, 15), window=self.numberLabel)

        # back to maze button
        self.back = Label(self.topbar, text="<< Back to Maze", font=("Arial", 14, "bold"), bg=topbarBg, fg="black", cursor="hand2")
        self.topbar.create_window(85, 15, window=self.back)
        self.back.bind("<Button-1>", self.back_to_maze)
        
        # buttons and textarea
        self.entry = Entry(self, font=("Arial", 18), highlightthickness=2, highlightbackground="#f4f4f4",
            highlightcolor="#eee", bg="white")
        self.entry.grid(row=2, column=1, sticky=E)
        self.submit = MathMazeButton(self, "assests/images/submit_green.png",
            "assests/images/submit_green_hover.png", self.submit, bg="#0c2")
        self.submit.grid(row=2, column=2, sticky=W)

        self.gridded = False
        self.onMaze = True

    def get_problem(self):
        '''MathMazeMazeProblem.get_problem() -> (str, int)
        returns the problem exam and number'''
        return self.problem

    def submit(self, event=None):
        '''MathMazeMazeProblem.submit() -> None
        submits the current problem'''
        if self.entry.get().upper() not in ("A", "B", "C", "D", "E"):
            self.master.flyin("assests/images/error.png", "Invalid Response", "Answer must be A, B, C, D, or E", "#fbb", 3000)
            return

        correct = self.entry.get().upper() == self.current
        self.submit.grid_remove()
        self.entry.grid_remove()
        if correct:
            Label(self, text="Correct", fg="green", font=("Arial", 25), bg="white"
                ).grid(row=2, column=0, columnspan=4)
            self.maze.get_killed().set("yes")
        else:
            Label(self, text="Incorrect", fg="red", font=("Arial", 25), bg="white"
                ).grid(row=2, column=0, columnspan=4)
            self.maze.get_killed().set("no")
            
        Label(self, text=f"Response: {self.entry.get()}  Answer: {self.current}",
            font=("Arial", 11), bg="white").grid(row=3, column=0, columnspan=4)

        #self.master.get_root().after(3000, self.back_to_maze)
                       
    def back_to_maze(self, event=None):
        '''MathMazeMazeProblem.back_to_maze(event) -> None
        goes back to the maze'''
        if not self.onMaze:
            self.onMaze = True
            self.maze.get_home().switch(self.maze)
            self.maze.get_back().set("back")

    def grid(self, **attr):
        '''MathMazeMazeProblem.grid(**dict) -> None
        overrides the Frame's grid method'''
        if not self.gridded:
            self.gridded = True
            self.onMaze = False
            Frame.grid(self, **attr)

    def grid_remove(self):
        '''MathMazeMazeProblem.grid_remove() -> None
        overrides the Frame's grid method'''
        if self.gridded:
            self.gridded = False
            Frame.grid_remove(self)
        
class MathMazeMaze(Canvas):
    '''represents the maze application for the game'''

    def __init__(self, master, home, num, saved=None, section=None, switch=False):
        ''''MathMazeMaze(master, num) -> MathMazeMaze
        constructs the maze on master'''
        Canvas.__init__(self, home, width=1000, height=580, highlightthickness=0, bg="#222")
        self.master = master
        self.gridded = False
        self.maze = None

        self.size = [random.randint(15,35) for i in range(2)]
        avg = int(sum(self.size)/2)
        self.num = num
        self.ongoing = "Ongoing"
        chests, doors, monsters = int(avg/2)+random.randrange(5), int(avg*2/3)+random.randrange(5), \
            int(avg/2)+random.randrange(5)
        
        # add maze to screen
        self.create_text((500,580/2), text="Loading...", fill="#2f4", font=("Arial", 60, "bold", "italic"), tags="loading")
        self.loading = StringVar(value="yes")
        if switch:
            home.switch(self)
            home.update()

        self.master.get_root().after(2000, lambda: self.stop_loading(saved))

        self.maze = maze.Maze(self, *self.size, 50, self.fight, self.advance, "#c9986b",
            '#916135', chests, doors, monsters, saved=saved)
        self.home = home
 
        self.monsterTypes = {"":"", "skeleton":"monster1_1", "bat":"monster2_1", "troll":"monster3_2",
            "crab":"monster4_1", "frog":"monster5_2", "door":"door_closed"}
        
        self.chests = []
        self.monsters = []

        # problems
        self.problems = {}
        if saved == None:
            for monster in self.maze.get_monsters():
                self.problems[monster] = MathMazeMazeProblem(self.master, self,
                    self.master.random_problem())
            for door in self.maze.get_doors():
                self.problems[door] = MathMazeMazeProblem(self.master, self,
                    self.master.random_problem())
            for chest in self.maze.get_chests():
                self.problems[chest] = MathMazeMazeProblem(self.master, self,
                    self.master.random_problem())
        else:
            data = saved.split("\n")
            for monster in data[4].split():
                monster = monster.split("-")
                self.problems[int(monster[0]), int(monster[1])] = MathMazeMazeProblem(self.master, self,
                    (monster[4].replace("_", " "), int(monster[5])))
            for door in data[3].split():
                door = door.split("-")
                self.problems[int(door[0]), int(door[1])] = MathMazeMazeProblem(self.master, self,
                    (door[3].replace("_", " "), int(door[4])))
            for chest in data[2].split():
                chest = chest.split("-")
                self.problems[int(chest[0]), int(chest[1])] = MathMazeMazeProblem(self.master, self,
                    (chest[4].replace("_", " "), int(chest[5])))

        self.killed = StringVar()
        self.backToMaze = StringVar()
        self.incorrect = 0
        self.correct = 0
        self.score = 0
        self.section = section
        self.scores = self.master.get_scores()
        
        # widgets
        self.title = Label(self, text=f"MathMaze {self.num}: Ongoing", font=("Arial", 22, "bold", "italic"), bg="#222", fg="#4f5")
        self.accuracy = Label(self, text="Accuracy: NA", font=("Arial", 14), bg="#222", fg="#4f2")
        self.back = Label(self, text="<< Back", font=("Arial", 14), bg="#222", fg="#4f2", anchor=W, cursor="hand2")
        self.numChests = Label(self, text=f"Chests Opened: {len(self.chests)}",
            font=("Arial", 15, "bold"), bg="#222", fg="#4f2")
        self.numMonsters = Label(self, text=f"Obstacles Overcome: {len(self.monsters)}",
            font=("Arial", 15, "bold"), bg="#222", fg="#4f2")

        self.after(20, lambda: self.configure_labels(saved))
       
    def save_maze(self, again=False):
        '''MathMazeMaze.save_maze(bool) -> None
        saves the maze every minute'''
        self.master.get_mazes()[self.num] = self.string()
        self.master.save_mazes()
        if again: self.after(60000, self.save_maze)

    def configure_labels(self, saved):
        '''MathMazeMaze.configure_labels(str) -> None
        configures the labels if saved'''
        if saved == None: return
        
        # add chests to maze
        for chest in self.maze.get_chests():
            if len(self.maze.get_chests()[chest]) == 3:
                self.add_chest(self.maze.get_chests()[chest][1], False)
        # add doors to maze
        for door in self.maze.get_doors():
            if door not in self.maze.get_deadends():
                self.add_monster("door")
        # add monsters to maze
        for monster in self.maze.get_monsters():
            if monster not in self.maze.get_deadends():
                self.add_monster(list(self.monsterTypes)[self.maze.get_monsters()[monster][1]])

        stats = saved.split("\n")[5].split()
        self.correct = int(stats[0])
        self.incorrect = int(stats[1])

        if self.correct + self.incorrect != 0:
            self.accuracy["text"] = "Accuracy: " + str(round(self.correct/(self.incorrect+self.correct)*100)) + "%"

    def string(self):
        '''MathMazeMaze.string() -> str
        converts the maze to the file version'''
        return f"{self.maze.string(self.problems)}\n{self.correct} {self.incorrect} {self.score}"

    def get_num(self):
        '''MathMazeMaze.get_num() -> int
        returns the number of the maze'''
        return self.num

    def add_to_list(self, section):
        '''MathMazeMaze.add_to_list(section) -> None
        adds self to mazeList'''
        self.section = section
        section.configure_section(f"Maze {self.num}", self.ongoing, self.numChests["text"], "#0a1", True)

    def stop_loading(self, saved):
        '''MathMazeMaze.stop_loading(str) -> None
        stops loading the maze'''
        # num chests and obstacles
        self.create_window(150, 90, window=self.numChests)
        self.create_window(850, 90, window=self.numMonsters)
        
        # text on screen
        self.create_window(500, 50, window=self.title)
        self.create_window(500, 97, window=self.accuracy)
        self.create_window(335, 97, window=self.back)
        self.back.bind("<Button-1>", self.home.go_home)
        
        self.loading.set("no")
        self.delete("loading")
        self.create_window((500,313), window=self.maze)

        self.save_maze()

    def get_killed(self):
        '''MathMazeMaze.get_killed() -> StringVar
        returns the string var for killed'''
        return self.killed

    def get_back(self):
        '''MathMazeMaze.get_back() -> StringVar
        returns the string var for back to maze'''
        return self.backToMaze

    def get_home(self):
        '''MathMazeMaze.get_home() -> MathMazeMazeHome
        returns the home page for the maze'''
        return self.home
                                
    def fight(self, cell):
        '''MathMazeMaze.fight(cell) -> bool
        returns whether player has won or lost fight (True/False)'''    
        self.killed = StringVar(value="yes")
        if cell in self.problems:
            self.home.switch(self.problems[cell])

        self.master.get_root().wait_variable(self.killed)

        # correct or incorrect
        value = self.killed.get()
        self.killed.set("")
        if value == "yes":
            self.correct += 1
            output = True
        else:
            self.problems[cell] = MathMazeMazeProblem(self.master, self, self.master.random_problem())
            self.incorrect += 1
            output = False

        self.accuracy["text"] = "Accuracy: " + str(round(self.correct/(self.incorrect+self.correct)*100)) + "%"
        return output

    def advance(self, cell):
        '''MathMazeMaze.advance(cell) -> None
        advances to the next obstacle'''
        if self.maze.get_last() in ("ruby", "sapphire", "gold", "iron", "diamond", "emerald"):
            self.add_chest(self.maze.get_last())
        else:
            self.add_monster(self.maze.get_last())

    def add_chest(self, chest, popup=True):
        '''MathMazeMaze.add_chest(str, bool) -> None
        adds a chest to the list'''
        self.delete("chest")
        self.chests.append(PhotoImage(file=f"assests/images/maze/{chest}.png"))

        if len(self.chests) <= 28:
            iterates = range(len(self.chests))
        else:
            iterates = range(len(self.chests)-28,len(self.chests))

        y = 85
        iterations = 0
        for i in iterates:
            if iterations%4 == 0:
                y += 55
            x = iterations%4*55+67.5
            self.create_image(x, y, image=self.chests[i], tag="chest")
            iterations += 1

        self.numChests["text"] = f"Chests Found: {len(self.chests)}"
        self.section.configure_section(body=self.numChests["text"])

        if popup:
            self.wait_variable(self.backToMaze)
        self.backToMaze.set("")

        # winning
        if len(self.chests) == len(self.maze.get_chests()):
            self.section.configure_section(h2="Completed!")
            self.title["text"] = f"MathMaze {self.num}: Completed!"
            if popup: self.master.flyin("assests/images/cup.png", "Maze Completed", "Congratulations! - You have completed this maze.", "#bfb", 6000)

    def add_monster(self, monster):
        '''MathMazeMaze.add_monster(str) -> None
        adds a monster to the list'''
        self.delete("monster")
        self.monsters.append(PhotoImage(file=f"assests/images/maze/{self.monsterTypes[monster]}.png"))

        if len(self.monsters) <= 28:
            iterates = range(len(self.monsters))
        else:
            iterates = range(len(self.monsters)-28,len(self.monsters))

        y = 85
        iterations = 0
        for i in iterates:
            if iterations%4 == 0:
                y += 55
            x = iterations%4*55+767.5
            self.create_image(x, y, image=self.monsters[i], tag="monster")
            iterations += 1

        self.numMonsters["text"] = f"Obstacles Overcome: {len(self.monsters)}"

    def get_master(self):
        '''MathMazeMaze.get_master() -> MathMazeFrame
        returns the game frame'''
        return self.master

    def grid(self, **attr):
        '''MathMazeMaze.grid(**dict) -> None
        overrides the Frame's grid method'''
        if not self.gridded:
            self.gridded = True
            if self.maze != None: self.maze.play()
            Frame.grid(self, **attr)

    def grid_remove(self):
        '''MathMazeMaze.grid_remove() -> None
        overrides the Frame's grid method'''
        if self.gridded:
            self.gridded = False
            if self.maze != None: self.maze.pause()
            Frame.grid_remove(self)

class MathMazeTabBar(Canvas):
    '''represents the tabbar for the application'''

    def __init__(self, master):
        '''MathMazeTabBar(master) -> MathMazeTabBar
        constructs the tabbar for the game'''
        Canvas.__init__(self, master, width=1000, height=70, highlightthickness=0)
        self.grid(row=0, column=0)
        self.tabs = []
        self.current = None
        self.flyins = []
        self.currentAfter = None
        self.logo = PhotoImage(file="assests/images/MathMazeLogo_maze.png")
        self.create_image(500, 35, image=self.logo)

    def __add__(self, tab):
        '''MathMazeTabBar + (text, frame) -> MathMazeTabBar
        adds a new tab to the tabbar'''
        self.add_tab(*tab)
        return self

    def get_tabs(self):
        '''MathMaze.get_tabs() -> list
        returns a list of all tabs'''
        return self.tabs

    def get_current(self):
        '''MathMazeTabBar.get_current() -> MathMazeTab
        returns the current tab'''
        return self.current

    def activate(self):
        '''MathMazeTabBar.activate() -> None
        activates the tabbar'''
        self.flyinCanvas = Canvas(self, highlightthickness=0, height=60, width=500)
        self.exitCanvas = Canvas(self, highlightthickness=0, height=22, width=22, cursor="hand2")
        self.exitCanvas.create_oval(1, 1, 21, 21, fill="#bbb", outline="#bbb", tag="exit")
        self.exitCanvas.create_line(7, 7, 15, 15, fill="black", width=2)
        self.exitCanvas.create_line(7, 15, 15, 7, fill="black", width=2)
        self.flyinHeader = Label(self.flyinCanvas, font=("Arial", 11, "bold"), anchor=W, width=100)
        self.flyinCanvas.create_window(515, 20, window=self.flyinHeader)
        self.flyinBody = Label(self.flyinCanvas, font=("Arial", 11), anchor=W, width=100)
        self.flyinCanvas.create_window(515, 40, window=self.flyinBody)
        self.exitCanvas.bind("<Button-1>", self.exit)
        
        self.create_window(500, -65, window=self.flyinCanvas, tag="flyin")
        self.flyinCanvas.create_window(475, 30, window=self.exitCanvas, tag="exit")

    def switch(self, tab):
        '''MathMazeTabBar.switch(tab) -> None
        switches to current tab'''
        if self.current != None:
            self.current.switch_off()
        self.current = tab

    def add_tab(self, text, frame=None, logo="MathMazeLogo.png", closedcolor="#e2e2e2", opencolor="white"):
        '''MathMazeTabBar.add_tab(text, frame, logo="MathMazeLogo.png") -> None
        creates a tab and returns its tabs'''
        x = 260+120*len(self.tabs)+60
        self.tabs.append(MathMazeTab(self, (x,49), text, frame, logo, closedcolor, opencolor))

    def flyin(self, image, header, body, bg, ms):
        '''MathMazeTabBar.flyin(str, str, str, str, int) -> None
        shows a flyin for ms milliseconds'''
        self.flyins.append((image, header, body, ms, bg))

        if len(self.flyins) == 1:
            self.do_flyin(image, header, body, ms, bg)

    def do_flyin(self, image, header, body, ms, bg):
        '''MathMazeTabBar.do_flyin(image, header, bosy, ms, bg) -> None
        shows the flyin and closes it after ms milliseconds'''
        self.flyinCanvas["bg"] = bg
        self.exitCanvas["bg"] = bg
        self.flyinHeader["bg"] = bg
        self.flyinHeader["text"] = header
        self.flyinBody["bg"] = bg
        self.flyinBody["text"] = body

        self.flyinCanvas.delete("image")
        if image != "":
            self.flyinImage = PhotoImage(file=image)
            self.flyinCanvas.create_image(30, 30, image=self.flyinImage)
        
        self.move("flyin", 0, 100)
        self.currentAfter = self.after(ms, self.end_flyin)

    def end_flyin(self):
        '''MathMazeTabBar.end_flyin() -> None
        ends the current flyin'''
        if len(self.flyins) == 0:
            return

        self.move("flyin", 0, -100)
        self.flyins.pop(0)

        if len(self.flyins) > 0:
            self.after(500, lambda: self.do_flyin(*self.flyins[0]))

    def exit(self, event=None):
        '''MathMazeTabBar.exit(event) -> None
        exits the popup if open'''
        if len(self.flyins) > 0:
            if self.currentAfter != None: self.after_cancel(self.currentAfter)
            self.currentAfter = None
            self.end_flyin()

class MathMazeFrame(Frame):
    '''represents the frame for the game'''

    def __init__(self, master):
        '''MathMazeFrame(master) -> MathMazeFrame
        constructs the main frame for the game'''
        Frame.__init__(self, master, bg="white")
        self.grid()

        # get problems
        inFile = open("assests/text/answers.txt")
        self.problems = {}
        for line in inFile:
            line = line.replace("\n","").split(": ")
            self.problems[line[0]] = line[1].split()
        inFile.close()

        # get descriptions
        inFile = open("assests/text/descriptions.txt")
        self.descriptions = {}
        for desc in inFile.read().split("\n===\n"):
            desc = desc.split("::")
            self.descriptions[desc[0]] = desc[1]
        inFile.close()

        # get scores
        inFile = open("assests/text/scores.txt")
        self.scores = {}
        for score in inFile:
            score = score.split()
            self.scores[score[0]] = int(score[1]), int(score[2])
        inFile.close()

        # get exams
        inFile = open("assests/text/exams.txt")
        self.exams = {}
        for exam in inFile:
            exam = exam.split(": ")
            self.exams[exam[0]] = exam[1].split()
        inFile.close()

        # get mazes
        inFile = open("assests/text/mazes.txt")
        self.mazes = {}
        for maze in inFile.read().split("\n==="):
            if len(maze) < 2: continue
            maze = maze.split(": ")
            self.mazes[int(maze[0])] = maze[1]
        inFile.close()

        # loading canvas
        self.loading = Canvas(self.master, width=1000, height=650, highlightthickness=0, bg="#222")
        self.loading.create_text(500, 650/2, text="Loading...", fill="#2f4", font=("Arial", 60, "bold", "italic"), tags="loading")
        self.loading.grid()

        self.problemIter = 0

    def __str__(self):
        '''str(MathMazeFrame) -> "MathMazeFrame"
        for testing purposes'''
        return "MathMazeFrame"

    def get_problem_num(self, problem):
        '''MathMazeFrame.get_problem_num(problem) -> int
        returns the problem number'''
        num = str(problem[1]).zfill(2)
        return "#" + num[1] + problem[0][3] + self.exams[problem[0][5:]][0] + problem[0][2] + num[0]

    def get_maze_page(self):
        '''MathMazeFrame.get_maze_page() -> MathMazeMazeHome
        returns the page for the mazes'''
        return self.maze

    def get_mazes(self):
        '''MathMazeFrame.get_mazes() -> dict
        returns the maze info'''
        return self.mazes

    def get_exams(self):
        '''MathMazeFrame.get_exams() -> dict
        returns the exam info'''
        return self.exams

    def get_problems(self):
        '''MathMazeFrame.get_problems() -> dict
        returns the answer key for all problems'''
        return self.problems

    def get_descs(self):
        '''MathMazeFrame.get_descs() -> dict
        returns a dictionary with descriptions'''
        return self.descriptions

    def get_scores(self):
        '''MathMazeFrame.get_scores() -> dict
        returns a dictionary with scores'''
        return self.scores

    def get_root(self):
        '''MathMazeFrame.get_root() -> Tk
        returns the root window'''
        return self.master

    def random_problem(self):
        '''MathMazeFrame.random_problem() -> (str, int)
        returns a random problem'''
        test = random.choice(list(self.problems))
        problem = random.randrange(len(self.problems[test]))+1
        self.problemIter += 1
        return test, problem

    def get_problem_xp(self, problem):
        '''MathMazeFrame.get_problem_xp((str, int)) -> int
        returns the XP of the problem'''
        return random.randint(20,100)

    def save_mazes(self, clear=False):
        '''MathMazeFrame.save_maze(bool) -> None
        saves a maze with mazeStr at mazeNum'''
        if clear:
            outFile = open("assests/text/mazes.txt", "w")
            outFile.write("")
            outFile.close()
            return
        
        text = ""
        for maze in self.mazes:
            text += str(maze) + ": " + self.mazes[maze] + "\n==="

        outFile = open("assests/text/mazes.txt", "w")
        outFile.write(text)
        outFile.close()

    def activate(self):
        '''MathMazeFrame.activate() -> None
        activates maze section'''
        self.maze = MathMazeMazeHome(self)
        self.loading.destroy()
        self.tabs = MathMazeTabBar(self)
        self.maze.grid(row=1, column=0)        
        self.tabs.activate()
        self.maze.saved_mazes()
        self.maze.save_all_mazes(None, True)
        #self.master.protocol("WM_DELETE_WINDOW", self.maze.save_all_mazes)

    def flyin(self, *args):
        '''MathMazeFrame.flyin(image, header, body, ms, bg) -> None
        shows a popup for ms milliseconds'''
        self.tabs.flyin(*args)

root = Tk()

willContinue = True
try:
    photo = PhotoImage(file="assests/images/gold.png")
except:
    willContinue = False
    print("Program Interrupted. Try again.")
    input()

if willContinue:
    root.configure(bg="white")
    root.title("MathMaze")
    root.resizable(False, False)
    root.iconphoto(True, photo)
    root.geometry("1000x650+10+5")
    app = MathMazeFrame(root)
    root.after(1000, app.activate)
    mainloop()
