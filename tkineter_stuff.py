from Tkinter import *
import time

class court_animation():
    def __init__(self, sequence):
        self.root = Tk()
        self.canvas = Canvas(self.root, width=600, height=480, bg='blue')
        self.sequence = sequence
        self.map = []
        self.frame_count = 0
        self.animate()
        self.root.mainloop()
    
    '''def populate_map(self, dict):
        for x in range(15):
            row = []
            for y in range(12):
                row.append(dict[x,y])
            self.map.append(row)'''
            
            
    def animate(self):
        if self.frame_count < len(self.sequence):
            self.map = self.sequence[self.frame_count]
        
            x_count = 0
            y_count = 0
            for row in self.map:
                y_count = 0
                for column in row:
                    if column == 'Th':
                        color = 'white'
                    elif column == 'B':
                        color = 'red'
                    elif column == 0:
                        color ='blue'
                    else:
                        color = 'green'
                    self.canvas.create_rectangle(40*x_count, 40*y_count, 40*(x_count+1), 40*(y_count+1), outline=color, fill=color)
                    self.canvas.pack(fill=BOTH, expand=1)
                    y_count += 1
                x_count += 1
            self.frame_count += 1
            self.root.after(1000, self.animate)