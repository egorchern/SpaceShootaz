# Copyright - Egor Chernyshev. SpaceShootaz - game made for University of Manchester python coursework
# DO NOT RESIZE THE WINDOW. Window initializes with correct size at start
import tkinter as tk
import math


class Utilities:
  # Class for utility functions, such as resolve angle and resolve point
  def __init__(self):
    pass

  def radians_to_degrees(self, radians: float) -> float:
    return radians * (180 / math.pi)

  def resolve_angle(self, x1: float, y1: float, x2: float, y2:float ) -> float:
    # Calculates angle between (x1, y1) and (x2, y2) relative to positive y-axis
    x_diff = x2 - x1
    y_diff = y2 - y1
    angle = 0

    if x_diff > 0 and y_diff < 0: 
      # If in upper right quodrant
      y_diff = abs(y_diff)
      angle = math.atan(x_diff / y_diff)
    elif x_diff > 0 and y_diff > 0: 
      # If in lower right quodrant
      angle = math.atan(y_diff / x_diff) + math.pi/2
    elif x_diff < 0 and y_diff > 0: 
      # If in lower left quodrant
      x_diff = abs(x_diff)
      angle = math.atan(x_diff / y_diff) + math.pi
    elif x_diff < 0 and y_diff < 0:
      # If in upper left quodrant
      x_diff = abs(x_diff)
      y_diff = abs(y_diff)
      angle = math.atan(y_diff / x_diff) + (3/2 * math.pi)
    elif x_diff == 0 and y_diff < 0:
      # if straight up
      angle = 0
    elif x_diff > 0 and y_diff == 0:
      # if staight right
      angle = math.pi / 2
    elif x_diff == 0 and y_diff > 0:
      # if straight down
      angle = 3/2 * math.pi
    elif x_diff < 0 and y_diff == 0:
      # if staight left
      angle = 2 * math.pi
    else:
      # if points are equal
      angle = 0
    return angle
  

class Game:
  # Class for the game, includes frame trigger, pause/resume functions and etc.
  def __init__(self, page_frame):
    self.canvas_dimensions = {
      "x": 1000,
      "y" : 850
    }
    self.canvas = tk.Canvas(
      master=page_frame,
      width=self.canvas_dimensions.get("x"),
      height=self.canvas_dimensions.get("y"),
      bg="white",
      relief="solid",
      borderwidth=1
    )
    self.canvas.grid(padx=5)
    self.canvas_centre_x = self.canvas_dimensions.get("x") // 2
    self.canvas_centre_y = self.canvas_dimensions.get("y") // 2
    self.utils = Utilities()
    self.canvas.bind("<Motion>", self.on_cursor_move)

  def on_cursor_move(self, event):
    x = event.x
    y = event.y
    angle = self.utils.resolve_angle(self.canvas_centre_x, self.canvas_centre_y, x, y)
    print(angle)


class Menu:
  # Class for the menu, includes load, cheat code enter and key remapping
  def __init__(self):
    pass

class Application: 
  # Class for the whole application, contains tkinter top window and etc.
  def __init__(self):
    self.main_window_dimensions = {
      "x": 1440,
      "y": 900
    }
    self.state = "game" # Game states: menu, game
    # Initialize the main window
    self.main_window = tk.Tk()
    self.main_window.title("SpaceShootaz")
    self.main_window.geometry(f"{self.main_window_dimensions.get('x')}x{self.main_window_dimensions.get('y')}")
    self.main_window.configure(bg='white')
    self.main_window.resizable(False, False)
    # Window should not be touched, so organise everything in a frame
    self.page_frame = tk.Frame(master=self.main_window, bg="white")

    self.on_app_state_change()
    self.page_frame.grid()
    self.main_window.mainloop()

  def on_app_state_change(self):
    # Destroy children widgets to reset the window on state change
    list = self.page_frame.grid_slaves()
    for l in list:
      l.destroy()
    
    if self.state == "game":
      game = Game(self.page_frame)
    pass

def main():
  app = Application()
  
  


if __name__ == "__main__":
  main()