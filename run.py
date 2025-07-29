import sys
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

class Game:
    
    def __init__(self):
        
        # Games variables
        self.current_move = 'O' 
        self.win = False
        self.buttons = dict()
        # Run widget, Run GUI
        self.root = Tk()
        self.root.withdraw()
        self.settings()
        self.root.resizable(False, False)
        # self.root.geometry('300x200')
        self.root.iconbitmap('images/XO.ico')
        self.root.title('')

        self.image_games()
        self.widget()
        self.create_button()
        self.root.mainloop()

 
    def window_in_the_center(self):
        # Wait for the final rendering, всех widgets
        self.root.update_idletasks()
         # Отобразить окно
        self.root.deiconify()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')


    def settings(self):
        self.settings_windows = Toplevel(bg='black')
        self.settings_windows.title('settings')
        self.settings_windows.geometry('300x200')
        self.settings_windows.config(bg='black')
        self.settings_windows.resizable(False, False)
        self.settings_windows.iconbitmap('images/settings.ico')
        self.settings_windows.protocol("WM_DELETE_WINDOW", lambda: None)
        self.windows_settings_display_center()
        self.settings_widgets()

    def windows_settings_display_center(self):
        # Hide window
        self.settings_windows.withdraw()
        # Display window centeredу
        width = self.settings_windows.winfo_width()
        height = self.settings_windows.winfo_height()
        x = (self.settings_windows.winfo_screenwidth() // 2) - (width // 2)
        y = (self.settings_windows.winfo_screenheight() // 2) - (height // 2)
        self.settings_windows.geometry(f'{width}x{height}+{x}+{y}')
        self.settings_windows.configure(bg='black')
        # Show window
        self.settings_windows.deiconify()

    def settings_widgets(self):
        Label(self.settings_windows, text="Do you want to play first?", font= ("Arial", 15), bg= 'black', fg= 'white').pack()

        Button(self.settings_windows, text= "Yes", command=self.start_game_as_x,
                bg= 'black', fg= 'white', activeforeground= 'white',activebackground= 'black'
                ).pack(fill="both", padx=5, pady=5, ipadx=5,ipady=5)
        Button(self.settings_windows, text= "No", command= self.start_game_as_o,
                bg= 'black', fg= 'white', activeforeground= 'white', activebackground='black'
                ).pack(fill='both', padx=5, pady=5, ipadx=5, ipady=5)
        Button(self.settings_windows, text= "Exit", command= sys.exit,
                bg= 'black', fg= 'white', activeforeground= 'white', activebackground= 'black'
                ).pack(fill='both', padx=5, pady=5, ipadx=5, ipady=5)

    def start_game_as_x(self):
        self.current_move = 'X'
        self.settings_windows.destroy()
        self.window_in_the_center()

    def start_game_as_o(self):
        self.current_move = 'O' 
        self.settings_windows.destroy()
        self.window_in_the_center()
        self.computer_move()    


    def image_games(self):
        img_x = Image.open('images/X.png')
        r_x_img = img_x.resize((100,100))
        self.button_x = ImageTk.PhotoImage(r_x_img)

        img_o = Image.open('images/O.png')
        r_o_img = img_o.resize((100,100))
        self.button_o = ImageTk.PhotoImage(r_o_img)

        img_f = Image.open('images/F.png')
        r_f_img = img_f.resize((100,100))
        self.button_f = ImageTk.PhotoImage(r_f_img)


    def widget(self):
        self.line1 = Frame(self.root)
        self.line1.pack(side='top', expand=YES)

    def create_button(self):
        for x in range (3):
            for y in range (3):
                btt = Button(self.line1,  image=self.button_f, bg='black',
                            command= lambda xx = x, yy= y: self.button_click(xx, yy),
                            )
                btt.grid(row= x, column= y, ipadx = 1, ipady= 1, padx=1, pady=1 )
                click = 'empty'
                self.buttons[(x,y)] = [btt,click]
    # The human move
    def button_click(self, x, y):
        if self.buttons[x, y][1] == 'empty':
            self.buttons[x, y][0]['image'] = self.button_x
            self.buttons[x, y][1] = 'x'
            self.current_move = 'O'
            self.computer_move()
            if self.check_win:
                if self.games_messages():
                    self.restart_game()
                else:
                    sys.exit()
    @property
    def check_win(self):
        COMB_WIN = (((0, 0), (0, 1), (0, 2)),
                    ((1, 0), (1, 1), (1, 2)),
                    ((2, 0), (2, 1), (2, 2)),
                    ((0, 0), (1, 1), (2, 2)),
                    ((0, 2), (1, 1), (2, 0)),
                    ((0, 0), (1, 0), (2, 0)),
                    ((0, 1), (1, 1), (2, 1)),
                    ((0, 2), (1, 2), (2, 2)),
                    )
        for i in COMB_WIN:
            if self.buttons[i[0]][1] == self.buttons[i[1]][1] == self.buttons[i[2]][1] != 'empty':
                return self.buttons[i[0]][1]
            if all(v[1] != 'empty' for v in self.buttons.values()):
                return 'draw'
    
    

    def computer_move(self):
        best_move = [(1,1), (0,0), (0,2), (2,0), (2,2), (0,1), (2,1), (1,0), (1,2)]
        move = self.logical_move
        if self.current_move == 'O':
            if move:
                self.buttons[move][1] = 'o'
                self.buttons[move][0]['image'] = self.button_o
                self.current_move = 'X'
                return
            
            for i in best_move:
                if self.buttons[i][1] == 'empty':
                    self.buttons[i][1] = 'o'
                    self.buttons[i][0]['image'] = self.button_o
                    self.current_move = 'X'
                    break
         
                    
    @property
    def logical_move (self):
        for k, v in self.buttons.items():
            if v[1] not in ('x', 'o'):
                original = v[1]
                v[1] = 'o'
                if self.check_win == 'o':
                    v[1] = original
                    return k
                v[1] = original
        
        for k, v in self.buttons.items():
            if v[1] not in ('x', 'o'):
                original = v[1]
                v[1] = 'x'
                if self.check_win == 'x':
                    v[1] = original
                    return k
                v[1] = original
        return None

    def games_messages(self):
        if self.check_win == 'x': #in  ('x', 'o', 'draw'):
            message = messagebox.askyesno(message="You Win \nDont you want to play again?",
                                           title='tic_tac_toe')
            return message
        
        elif self.check_win == 'o':
            message = messagebox.askyesno(message="You los \nDont you want to play again?",
                                           title='tic_tac_toe')
            return message
        
        else:
            message = messagebox.askyesno(message="DRAW \nDont you want to play again?",
                                           title='tic_tac_toe')
            return message

    
    def restart_game(self):
        self.root.withdraw()
        self.settings()
        self.buttons.clear()
        self.create_button()
        



if __name__ == '__main__':
    Game()