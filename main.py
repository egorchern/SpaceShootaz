# Copyright - Egor Chernyshev. SpaceShootaz - game made for University of Manchester python coursework
# Window should not be resizable but still, DO NOT RESIZE THE WINDOW. Window initializes with correct size at start
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
      angle =  math.pi
    elif x_diff < 0 and y_diff == 0:
      # if staight left
      angle = 3/2 * math.pi
    else:
      # if points are equal
      angle = 0
    return angle
  
  def resolve_point(self, x1: float, y1: float, length: float, angle: float) -> tuple:
    # Calculates (x2, y2) point translated using angle with given angle, length and a reference point.
    # Reduces angle to optimal range
    while(angle >= 2 * math.pi):
      angle -= 2 * math.pi

    x_offset = 0
    y_offset = 0
    if angle == 0:
      # if staight top
      y_offset = -length
    elif angle < math.pi/2:
      # if in top right quodrant
      x_offset = math.sin(angle) * length
      y_offset = -math.cos(angle) * length
    elif angle == math.pi/2:
      # if staight right
      x_offset = length
    elif angle > math.pi/2 and angle < math.pi:
      # if in bottom right quodrant
      angle -= math.pi/2
      x_offset = math.cos(angle) * length
      y_offset = math.sin(angle) * length
    elif angle == math.pi:
      # if staight down
      y_offset = length
    elif angle > math.pi and angle < 3/2 * math.pi:
      # if in bottom left quodrant
      angle -= math.pi
      x_offset = -math.sin(angle) * length
      y_offset = math.cos(angle) * length
    elif angle == 3/2 * math.pi:
      # if staight left
      x_offset = -length
    elif angle > 3/2 * math.pi:
      # if in top left quodrant
      angle -= 3/2 * math.pi
      x_offset = -math.cos(angle) * length
      y_offset = -math.sin(angle) * length
    
    return (x1 + x_offset, y1 + y_offset)

  def calculate_length(self, x1: float, y1: float, x2: float, y2: float) -> float:
    # calculates length between two points
    return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

class Ship:
  # Generic ship class, with functions like tilt
  def __init__(self, canvas: tk.Canvas, width: int, height: int, focal_point: list, angle: float, color: str, fps: int):
    self.canvas = canvas
    self.ship_width = width
    self.ship_height = height
    self.focal_point = focal_point
    self.top_ship_section_percentage = 0.85
    self.speed_per_second = 400
    self.speed = self.speed_per_second / fps
    self.body_height_percentage = 0.45
    self.head_width_percentage = 0.3
    self.wing_flap_width_percentage = 0.4
    self.angle = angle
    self.utils = Utilities()
    self.color = color
    # Calculate starting points
    self.points = [
      self.focal_point[0],
      self.focal_point[1] - self.top_ship_section_percentage * height,
      self.focal_point[0] + self.head_width_percentage * (width / 2),
      self.focal_point[1] - self.top_ship_section_percentage * height * self.body_height_percentage,
      self.focal_point[0] + width / 2,
      self.focal_point[1],
      self.focal_point[0] + width / 2,
      self.focal_point[1] + (1 - self.top_ship_section_percentage) * height,
      self.focal_point[0] + (1 - self.wing_flap_width_percentage) * width / 2,
      self.focal_point[1],
      self.focal_point[0] - (1 - self.wing_flap_width_percentage) * width / 2,
      self.focal_point[1],
      self.focal_point[0] - width / 2,
      self.focal_point[1] + (1 - self.top_ship_section_percentage) * height,
      self.focal_point[0] - width / 2,
      self.focal_point[1],
      self.focal_point[0] - self.head_width_percentage * (width / 2),
      self.focal_point[1] - self.top_ship_section_percentage * height * self.body_height_percentage
    ]
    self.standard_lengths = []
    self.standard_angles = []
    self.calculate_standard_lengths_and_angles()

  def move(self):
    # Moves in the current direction by incrementing focal point with speed and recalculating points
    temp = self.utils.resolve_point(self.focal_point[0], self.focal_point[1], self.speed, self.angle)
    self.focal_point[0] = temp[0]
    self.focal_point[1] = temp[1]
    self.transform_points(self.angle)

  def calculate_standard_lengths_and_angles(self):
    # Calculates reference angles for using them to offset tilt calculation
    for i in range(0, len(self.points), 2):
      x = self.points[i]
      y = self.points[i + 1]
      length = self.utils.calculate_length(self.focal_point[0], self.focal_point[1], x, y)
      self.standard_lengths.append(length)
      angle = self.utils.resolve_angle(self.focal_point[0], self.focal_point[1], x, y)
      self.standard_angles.append(angle)
  
  def transform_points(self, angle: float):
    # Tilts points by given angle 
    self.angle = angle
    for i in range(0, len(self.points), 2):
      # Resolves the new point, when the current point is tilted at current angle
      temp = self.utils.resolve_point(self.focal_point[0], self.focal_point[1], self.standard_lengths[i // 2], self.standard_angles[i // 2] + self.angle)
      self.points[i] = temp[0]
      self.points[i + 1] = temp[1]

  def draw(self):
    self.canvas.create_polygon(self.points, fill=self.color)
    

class Game:
  # Class for the game, includes frame trigger, pause/resume functions and etc.
  def __init__(self, main_window):
    self.canvas_dimensions = {
      "x": 1000,
      "y" : 850
    }
    self.main_window = main_window
    self.canvas = tk.Canvas(
      master=main_window,
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
    self.fps = 60
    self.ms_interval = math.floor(1000 / self.fps)
    self.frame_counter = 1
    self.angle = 0
    self.player_width = 50
    self.player_height = 50
    self.player_color = "#41bfff"
    # Initialize player ship object
    self.player = Ship(self.canvas, self.player_width, self.player_height, [self.canvas_centre_x, self.canvas_centre_y], self.angle, self.player_color, self.fps)
    self.canvas.bind("<Motion>", self.on_cursor_move)
    self.main_window.bind("<Key>", self.on_key_press)
    self.canvas.after(self.ms_interval, self.on_frame)
    

  def on_frame(self):
    # Deletes everything from the canvas
    self.canvas.delete("all")
    self.player.draw()
    self.canvas.after(self.ms_interval, self.on_frame)
    pass

  def on_cursor_move(self, event):
    # Adjusts angle variable depending on where user points the cursor
    x = event.x
    y = event.y
    self.angle = self.utils.resolve_angle(self.player.focal_point[0], self.player.focal_point[1], x, y)
    self.player.transform_points(self.angle)
  
  def on_key_press(self, event):
    # Handles key presses
    key = event.char
    # TODO remapable keys
    if key == "w":
      self.player.move()
  
    


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
    self.on_app_state_change()
    self.main_window.mainloop()

  def on_app_state_change(self):
    # Destroy children widgets to reset the window on state change
    list = self.main_window.grid_slaves()
    for l in list:
      l.destroy()
    
    if self.state == "game":
      game = Game(self.main_window)
    pass

def main():
  app = Application()
  
  


if __name__ == "__main__":
  main()