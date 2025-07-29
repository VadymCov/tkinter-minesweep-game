import tkinter as tk
from tkinter import messagebox
import random


class DifficultyLevel:
    def __init__(self):
        self.root = tk.Tk()

        
class GameWidgets:

    def __init__(self):
        # Game settings
        self.root = tk.Tk()
        self.root.withdraw() # Скрыть окно
        self.root.resizable(False,False)
        self.root.title('Miner game')
        self.root.iconbitmap('image/boom.ico')


        self.size_field = 9
        self.number_mines = 30
        self.game_field()
        self.game_widgets_menu()
        self.buttons_config()
        self.mines_field()
        self.window_in_the_center()
        self.root.mainloop()
    
    def window_in_the_center(self):
        # Wait for the final rendering of all widgets
        self.root.update_idletasks()
        # Show window
        self.root.deiconify()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def game_field(self):
        self.top_margin = tk.Frame(self.root)
        self.top_margin.pack(fill='both')
        self.playing_field = tk.Frame(self.root)
        self.playing_field.pack(fill='both', expand=True)

    def game_widgets_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        # tearoff=False Turns off the dotted line at the beginning of the menu ❗
        game_menu = tk.Menu(menubar, tearoff=False)
        game_level = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(menu=game_menu, label='Game')
        menubar.add_cascade(menu=game_level, label='Level')

        game_menu.add_command(label='New games', command= self.restart_game)
        game_menu.add_command(label='Exit games', command= self.root.destroy)

        game_level.add_command(label=f'Easy 9/30 min', command= lambda f = 9, m = 30: self.handler_cmd(f ,m))
        game_level.add_command(label=f'Medium 15/50 min', command= lambda f = 15, m = 50: self.handler_cmd(f ,m))
        game_level.add_command(label=f'Difficult 18/80 min', command= lambda f = 18, m = 80: self.handler_cmd(f ,m))


    def handler_cmd(self, f, m):
        # Hide window
        self.root.withdraw()
        # Kills all widgets on the field 💥
        for widget in self.playing_field.winfo_children():
            widget.destroy()
        self.size_field = f
        self.number_mines = m
        # Clear all previous coordinates
        self.buttons.clear()
        self.clicked.clear()    
        self.mines.clear()
        # Redraw button widgets, generate mines
        self.buttons_config()
        self.mines_field()
        # Knocks down the window geometry to re-draw it
        self.root.geometry('')
        self.window_in_the_center()
        # Wait for the final rendering of all widgets
        self.root.update_idletasks()
        # Show window
        self.root.deiconify()


    def buttons_config(self):
        self.clicked = {}
        self.buttons = []
        for i in range(self.size_field):
            buttons = []
            for j in range(self.size_field):
                # left click
                btt = tk.Button(self.playing_field, width=3, text=' ', bg='#C1CDCD')
                btt.config(command=lambda x=i, y=j: self.left_click(x, y))
                btt.grid( row=i, column=j)
                # right click
                btt.bind('<Button-3>', lambda event, x=i, y=j: self.right_click(x, y))
                buttons.append(btt)
                self.clicked[(i,j)] = False
            self.buttons.append(buttons)

    # The function determines the coordinates of the mines on the field
    def mines_field(self):
        self.mines = set()
        while len(self.mines) < self.number_mines:
            i = random.randint(0,self.size_field - 1)
            j = random.randint(0,self.size_field - 1)
            self.mines.add((i,j))

    def left_click(self, x, y):
        self.check_lose(x,y)
        self.reveal_cell(x, y)
        self.check_win()

    def reveal_cell(self, x, y):
        mines = self.nearest_mines(x, y)
        if not (0 <= x < self.size_field and 0 <= y < self.size_field):
            return
        if self.clicked.get((x,y),False):
            return
        self.buttons[x][y].config(text=str(mines) if mines > 0 else ' ' , bg='#FAEBD7', state="disable" )
        self.clicked[(x, y)] = True
        if mines == 0:
            coordinates = [0,-1],[0,1],[-1,-1],[-1,0],[-1,1],[1,-1],[1,0],[1,1]
            for n in coordinates:
                nx = n[1]
                ny = n[0]
                if nx != 0 or ny != 0:
                    self.reveal_cell(x+ nx, y+ ny)

    # This function counts the number of mines around a cell
    def nearest_mines(self, x, y):
        count = 0
        coordinate = ([0,-1],[0,1],[-1,-1],[-1,0],[-1,1],[1,-1],[1,0],[1,1])
        for n in coordinate:
            nx = x + n[0] 
            ny = y + n[1]
            # Check that the coordinates of the playing field do not go beyond the boundaries of the playing field
            if 0 <= nx < self.size_field and 0 <= ny < self.size_field:
                if (nx,ny) in self.mines:
                    count += 1
        return count

    def right_click(self, x, y):
        btt = self.buttons[x][y]
        if  not self.clicked.get((x,y),False):
            current_text = btt.cget('text')
            if current_text == ' ':
                btt['text'] = '🚩'
                btt['bg'] = 'yellow'
            else:
                btt['text'] = ' '
                btt['bg'] = '#838B8B'

        # Ends the game if the entire board is open
    def check_win(self):
        count = list()
        for k in self.clicked.keys():
            if self.clicked[k] == False:
                count.append(k)
        # Leads to mines
        if len(count) == self.number_mines:
            for x,y in count:
                self.buttons[x][y].config(text='💣', bg='red')
            # Let's play yes/no again
            message_los = messagebox.askyesno(message="You WIN\nDo you want to play again?", title='  Miner')
            if message_los:
                self.restart_game() 
            else:
                self.root.destroy()

    def check_lose(self, x, y):
        if (x, y) in self.mines:
            self.open_field(x, y)
            for  m_c in self.mines:
                self.buttons[m_c[0]][m_c[1]].config(text='💣', bg='red', state='normal')
            message_los = messagebox.askyesno(message="You los\nDo you want to play again?", title='  Miner')
            if message_los:
                self.restart_game()
            else:
                self.root.destroy()

    def open_field(self, x, y):
        for k,v in self.clicked.items():
            if v == False:
                mines = self.nearest_mines(k[0],k[1])
                self.buttons[k[0]][k[1]].config(text= str(mines) if mines > 0 else ' ' , bg='#FAEBD7', state="disable")
                self.clicked[k] = True
    

    def restart_game(self):
        self.root.destroy()
        if __name__ == '__main__':
            GameWidgets()




        






if __name__ == '__main__':
    GameWidgets()
