# Copyright - Egor Chernyshev. SpaceShootaz - game made for University of Manchester python coursework
# Window should not be resizable but still, DO NOT RESIZE THE WINDOW. Window initializes with correct size at start
import tkinter as tk
import math
import configparser
import pathlib


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

  def is_out_of_bounds(self, obj_min_x: float, obj_max_x: float, obj_min_y: float, obj_max_y: float, bounds_max_x: float, bounds_max_y: float) -> bool:
    # Calculates if the object is out of bounds using the box model
    if(obj_min_x < 0):
      # If left of object is out of bounds
      return True
    elif(obj_max_x > bounds_max_x):
      # If right of object is out of bounds
      return True
    elif(obj_min_y < 0):
      # If top of object is out of bounds
      return True
    elif(obj_max_y > bounds_max_y):
      # If bottom of object is out of bounds
      return True
    else:
      # If inside bounds
      return False
  
  def transform(self, focal_point, angle, points, hitboxes):
    # Tilts points by given angle 
    for i in range(0, len(points) - 2, 2):
      # Resolves the new point, when the current point is tilted at current angle
      temp = self.resolve_point(focal_point[0], focal_point[1], points[-2][i // 2], points[-1][i // 2] + angle)
      points[i] = temp[0]
      points[i + 1] = temp[1]
    # Tilts hitboxes
    for j in range(len(hitboxes)):
      hitbox = hitboxes[j]
      for i in range(0, len(hitbox) - 2, 2):
        # Resolve the same as with object points, just do for every hitbox
        temp = self.resolve_point(focal_point[0], focal_point[1], hitbox[-2][i // 2], hitbox[-1][i // 2] + angle)
        hitbox[i] = temp[0]
        hitbox[i + 1] = temp[1]

    return (points, hitboxes)

  def calculate_points_metadata(self, points: list, focal_point: list) -> list:
    # Calculates reference angles for using them to offset tilt calculation
    lengths = []
    angles = []
    for i in range(0, len(points), 2):
      x = points[i]
      y = points[i + 1]
      length = self.calculate_length(focal_point[0], focal_point[1], x, y)
      lengths.append(length)
      angle = self.resolve_angle(focal_point[0], focal_point[1], x, y)
      angles.append(angle)
    points.append(lengths)
    points.append(angles)
    return points
  

class Ship:
  # Generic ship class, with functions like tilt
  def __init__(self, canvas: tk.Canvas, width: int, height: int, focal_point: list, angle: float, color: str, fps: int, canvas_dimensions: dict, speed_per_second: int):
    self.canvas = canvas
    self.canvas_dimensions = canvas_dimensions
    self.ship_width = width
    self.ship_height = height
    self.focal_point = focal_point
    self.top_ship_section_percentage = 0.85
    self.speed_per_second = speed_per_second
    self.speed = self.speed_per_second / fps
    self.body_height_percentage = 0.45
    self.head_width_percentage = 0.3
    self.wing_flap_width_percentage = 0.4
    self.angle = angle
    self.utils = Utilities()
    self.color = color
    self.display_hitboxes = True
    # Calculate starting points, tkinter requires points to be in format: [x1,y1,x2,y2,...] so thats why they are like that and not [[x1, y1], [x2, y2]]
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
    # Hitboxes have format: [[top_left, top_right, bottom_right, bottom_left]]
    self.hitboxes = [
      [
        self.focal_point[0] - self.head_width_percentage * (width / 2),
        self.focal_point[1] - self.top_ship_section_percentage * height,
        self.focal_point[0] + self.head_width_percentage * (width / 2),
        self.focal_point[1] - self.top_ship_section_percentage * height,
        self.focal_point[0] + self.head_width_percentage * (width / 2),
        self.focal_point[1] - self.top_ship_section_percentage * height * self.body_height_percentage,
        self.focal_point[0] - self.head_width_percentage * (width / 2),
        self.focal_point[1] - self.top_ship_section_percentage * height * self.body_height_percentage,
      ],
      [
        self.focal_point[0] - width / 2,
        self.focal_point[1] - self.top_ship_section_percentage * height * self.body_height_percentage,
        self.focal_point[0] + width / 2,
        self.focal_point[1] - self.top_ship_section_percentage * height * self.body_height_percentage,
        self.focal_point[0] + width / 2,
        self.focal_point[1] + (1 - self.top_ship_section_percentage) * height,
        self.focal_point[0] - width / 2,
        self.focal_point[1] + (1 - self.top_ship_section_percentage) * height
      ]
    ]
    # Calculate lengths angles from focal to points, used in tilt point calculation
    self.points = self.utils.calculate_points_metadata(self.points, self.focal_point)
    self.calculate_hitboxes_metadata()
    self.transform(self.angle)

  def move(self):
    # Moves in the current direction by incrementing focal point with speed and recalculating points
    temp = self.utils.resolve_point(self.focal_point[0], self.focal_point[1], self.speed, self.angle)
    # Get all X coordinates anc calc min and max
    xs = [self.points[i] for i in range(0, len(self.points) - 2, 2)]
    min_x = min(xs)
    max_x = max(xs)
    # Get all Y coordinates and calc min and max
    ys = [self.points[i] for i in range(1, len(self.points) - 2, 2)]
    min_y = min(ys)
    max_y = max(ys)
    # Check if the move will resolve in ship being out of bounds
    out_of_bounds = self.utils.is_out_of_bounds(min_x, max_x, min_y, max_y, self.canvas_dimensions.get("x"), self.canvas_dimensions.get("y"))
    if not out_of_bounds:
      # If not outside bounds then move in direction
      self.focal_point[0] = temp[0]
      self.focal_point[1] = temp[1]
      self.transform(self.angle)
  
  def calculate_hitboxes_metadata(self):
    # Same as points metadata generation, but iterate throught every hitbox
    for i in range(len(self.hitboxes)):
      hitbox = self.utils.calculate_points_metadata(self.hitboxes[i], self.focal_point)
      self.hitboxes[i] = hitbox
  
  def transform(self, angle: float):
    # Driver code for transforming points using generic transform function
    self.angle = angle
    temp = self.utils.transform(self.focal_point, self.angle, self.points, self.hitboxes)
    self.points = temp[0]
    self.hitboxes = temp[1]

  def draw_hitboxes(self):
    # Draws the box via lines
    for hitbox in self.hitboxes:
      self.canvas.create_line(hitbox[0], hitbox[1], hitbox[2], hitbox[3])
      self.canvas.create_line(hitbox[2], hitbox[3], hitbox[4], hitbox[5])
      self.canvas.create_line(hitbox[4], hitbox[5], hitbox[6], hitbox[7])
      self.canvas.create_line(hitbox[6], hitbox[7], hitbox[0], hitbox[1])

  def draw(self):
    self.canvas.create_polygon(self.points[0:len(self.points) - 2], fill=self.color)
    if self.display_hitboxes:
      self.draw_hitboxes()
    

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
    self.player_width = 45
    self.player_height = 50
    self.player_speed_per_second = 500
    self.player_color = "#41bfff"
    # Initialize player ship object
    self.player = Ship(self.canvas, self.player_width, self.player_height, [self.canvas_centre_x, self.canvas_centre_y], self.angle, self.player_color, self.fps, self.canvas_dimensions, self.player_speed_per_second)
    # Bind events
    self.parse_config()
    self.canvas.bind("<Motion>", self.on_cursor_move)
    self.main_window.bind("<Key>", self.on_key_press)
    self.canvas.after(self.ms_interval, self.on_frame)
  
  def create_new_config(self):
    # Creates a new config.ini file with standard settings below
    parser = configparser.ConfigParser()
    parser.add_section("IDENTITY")
    parser.set("IDENTITY", "Name", "Bob the Builder")
    parser.add_section("CONTROLS")
    parser.set("CONTROLS", "Move", "w")
    parser.set("CONTROLS", "Pause", "space")
    parser.set("CONTROLS", "Boss_key", "p")
    file = open("config.ini", "w")
    parser.write(file)
    file.close()

  def parse_config(self):
    # Checks whether there is a config file
    file_exists = pathlib.Path("config.ini").exists()
    if not file_exists:
      # If no config, create new and read again
      self.create_new_config()
      self.parse_config()
    else:
      parser = configparser.ConfigParser()
      parser.read("config.ini")
      self.controls = {}
      # Parse config by sections
      for sect in parser.sections():
        for k, v in parser.items(sect):
          if sect == "IDENTITY":
            self.identity = v
          elif sect == "CONTROLS":
            # Tkinter treats space characters as " " thats why it is here
            if v == "space":
              v = " "
            self.controls[k] = v
      
  def on_frame(self):
    # Deletes everything from the canvas
    self.canvas.delete("all")
    self.player.draw()
    self.canvas.after(self.ms_interval, self.on_frame)
    print(self.frame_counter)
    self.frame_counter += 1
    if(self.frame_counter > self.fps):
      self.frame_counter = 1
    pass

  def on_cursor_move(self, event):
    # Adjusts angle variable depending on where user points the cursor
    x = event.x
    y = event.y
    self.angle = self.utils.resolve_angle(self.player.focal_point[0], self.player.focal_point[1], x, y)
    self.player.transform(self.angle)
  
  def on_key_press(self, event):
    # Handles key presses
    key = event.char
    if self.controls.get("move") == key:
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