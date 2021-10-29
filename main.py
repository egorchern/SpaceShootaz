# Copyright - Egor Chernyshev. SpaceShootaz - game made for University of Manchester python coursework
# DO NOT RESIZE THE WINDOW. Window initializes with correct size at start
import tkinter as tk


class Utilities: # Class for utility functions, such as resolve angle and resolve point
  def __init__(self):
    pass


class Game: # Class for the game, includes frame trigger, pause/resume functions and etc.
  def __init__(self):
    pass


class Application: # Class for the whole application, contains tkinter top window and etc.
  def __init__(self):
    self.main_window_dimensions = {
      "x": 1440,
      "y": 900
    }
    self.main_window = tk.Tk()
    self.main_window.title("SpaceShootaz")
    self.main_window.geometry(f"{self.main_window_dimensions.get('x')}x{self.main_window_dimensions.get('y')}")
    self.main_window.configure(bg='white')
    self.main_window.mainloop()

def main():
  app = Application()

if __name__ == "__main__":
  main()