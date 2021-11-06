# Copyright - Egor Chernyshev. SpaceShootaz - game made for University of Manchester python coursework
# Window should not be resizable but still, DO NOT RESIZE THE WINDOW. Window initializes with correct size at start
import tkinter as tk
import math
import configparser
import pathlib
import random

utils = 0
# Points have last two elements as metadata, so thats why it is len(points) - 2
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
  
  def get_bounds_info(self, points: list) -> list:
    # Returns information about object bounds
    xs = [points[i] for i in range(0, len(points) - 2, 2)]
    # Get all X coordinates anc calc min and max
    min_x = min(xs)
    max_x = max(xs)
    # Get all Y coordinates and calc min and max
    ys = [points[i] for i in range(1, len(points) - 2, 2)]
    min_y = min(ys)
    max_y = max(ys)
    return [min_x, max_x, min_y, max_y]

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
  
  def is_fully_out_of_bounds(self, obj_min_x: float, obj_max_x: float, obj_min_y: float, obj_max_y: float, bounds_max_x: float, bounds_max_y: float) -> bool:
    # Similar to is_out_of_bounds but checks if object is completely out of viewable space
    if obj_max_x < 0:
      # If out from left
      return True
    elif obj_min_x > bounds_max_x:
      # If out from right
      return True
    elif obj_max_y < 0:
      # If out from top
      return True
    elif obj_min_y > bounds_max_y:
      # If out from bottom
      return True
    else:
      return False

  def transform(self, focal_point, angle, points, hitboxes) -> tuple:
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

  def do_hitboxes_collide(self, hitbox1: list, hitbox2: list) -> bool:
    # Calculate whether hitboxes collide using Separating Axis Theorem
    # Get all edge vectors
    vectors = [[hitbox1[0] - hitbox1[2], hitbox1[1] - hitbox1[3]], [hitbox1[2] - hitbox1[4], hitbox1[3] - hitbox1[5]], [hitbox1[4] - hitbox1[6], hitbox1[5] - hitbox1[7]], [hitbox1[6] - hitbox1[0], hitbox1[7] - hitbox1[1]], [hitbox1[0] - hitbox1[2], hitbox1[1] - hitbox1[3]], [hitbox1[2] - hitbox1[4], hitbox1[3] - hitbox1[5]], [hitbox2[4] - hitbox2[6], hitbox2[5] - hitbox2[7]], [hitbox2[6] - hitbox2[0], hitbox2[7] - hitbox2[1]]]
    for vector in vectors:
      # Get perpendicular edge vector
      normal_vector = [-vector[1], vector[0]]
      a_min = float("inf")
      a_max = float("-inf")
      b_min = float("inf")
      b_max = float("-inf")
      # Iterate through all points on hitbox1 and hitbox2 and set min max values to compare later
      for i in range(0, len(hitbox1) - 2, 2):
        x = hitbox1[i]
        y = hitbox1[i + 1]
        dot = ((x * normal_vector[0]) + (y * normal_vector[1]))
        a_min = min(a_min, dot)
        a_max = max(a_max, dot)
      
      for i in range(0, len(hitbox2) - 2, 2):
        x = hitbox2[i]
        y = hitbox2[i + 1]
        dot = ((x * normal_vector[0]) + (y * normal_vector[1]))
        b_min = min(b_min, dot)
        b_max = max(b_max, dot)
      
      # If no overlap found, there can be no collision according to the theorem
      if not (b_max >= a_min and b_min <= a_max):
        return False

    # If for all axis there is an overlap, then collision occurs
    return True

  def do_objects_collide(self, obj1, obj2) -> bool:
    hitboxes1 = obj1.hitboxes
    hitboxes2 = obj2.hitboxes
    for i in range(len(hitboxes1)):
      hitbox1 = hitboxes1[i]
      for j in range(len(hitboxes2)):
        hitbox2 = hitboxes2[j]
        do_collide = self.do_hitboxes_collide(hitbox1, hitbox2)
        if do_collide == True:
          return True

    return False


class Bullet:
  # Class for bullet, created by some ship, uses similar properties as ship, so refer to ship class for more documentation
  def __init__(self, canvas: tk.Canvas, canvas_dimensions: dict, width, height, focal_point, speed, damage, angle, fps, color, display_hitboxes):
    self.canvas = canvas
    self.canvas_dimensions = canvas_dimensions
    self.width = width
    self.height = height
    self.focal_point = focal_point
    self.speed = speed
    self.damage = damage
    self.angle = angle
    self.display_hitboxes = display_hitboxes
    self.color = color
    # Double sided triangle
    self.points = [
      self.focal_point[0],
      self.focal_point[1] - self.height / 2,
      self.focal_point[0] + self.width / 2,
      self.focal_point[1],
      self.focal_point[0],
      self.focal_point[1] + self.height / 2,
      self.focal_point[0] - self.width / 2,
      self.focal_point[1]

    ]
    self.hitboxes = [
      [
        self.focal_point[0] - self.width / 2,
        self.focal_point[1] - self.height / 2,
        self.focal_point[0] + self.width / 2,
        self.focal_point[1] - self.height / 2,
        self.focal_point[0] + self.width / 2,
        self.focal_point[1] + self.height / 2,
        self.focal_point[0] - self.width / 2,
        self.focal_point[1] + self.height / 2
      ]
    ]
    self.points = utils.calculate_points_metadata(self.points, self.focal_point)
    self.calculate_hitboxes_metadata()
    self.transform(self.angle)
    
  def transform(self, angle: float):
    # Driver code for transforming points using generic transform function
    self.angle = angle
    temp = utils.transform(self.focal_point, self.angle, self.points, self.hitboxes)
    self.points = temp[0]
    self.hitboxes = temp[1]
  
  def calculate_hitboxes_metadata(self):
    # Same as points metadata generation, but iterate throught every hitbox
    for i in range(len(self.hitboxes)):
      hitbox = utils.calculate_points_metadata(self.hitboxes[i], self.focal_point)
      self.hitboxes[i] = hitbox

  def move(self):
    # Moves in the current direction by incrementing focal point with speed and recalculating points
    temp = utils.resolve_point(self.focal_point[0], self.focal_point[1], self.speed, self.angle)
    self.focal_point[0] = temp[0]
    self.focal_point[1] = temp[1]
    self.transform(self.angle)
  
  def draw_hitboxes(self):
    # Draws the box via lines
    for hitbox in self.hitboxes:
      self.canvas.create_line(hitbox[0], hitbox[1], hitbox[2], hitbox[3])
      self.canvas.create_line(hitbox[2], hitbox[3], hitbox[4], hitbox[5])
      self.canvas.create_line(hitbox[4], hitbox[5], hitbox[6], hitbox[7])
      self.canvas.create_line(hitbox[6], hitbox[7], hitbox[0], hitbox[1])

  def draw(self):
    # Draws the bullet
    self.canvas.create_polygon(self.points[0:len(self.points) - 2], fill=self.color)
    # If hitboxes display is on, display hitboxes of the ship
    if self.display_hitboxes:
      self.draw_hitboxes()


class Ship:
  # Generic ship class, with functions like tilt
  def __init__(
      self,
      canvas: tk.Canvas,
      width: int,
      height: int,
      focal_point: list,
      angle: float,
      color: str,
      fps: int,
      canvas_dimensions: dict,
      speed_per_second: int,
      display_hitboxes: bool,
      display_hitbars: bool,
      bullet_width: int,
      bullet_height: int,
      bullet_speed_per_second: int,
      bullet_color: str,
      bullet_damage: int,
      shoot_rate_per_second: float,
      health: int
    ):
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
    self.fps = fps
    self.angle = angle
    self.color = color
    self.bullet_width = bullet_width
    self.bullet_height = bullet_height
    self.bullet_speed = bullet_speed_per_second / fps
    self.display_hitboxes = display_hitboxes
    self.display_hitbars = display_hitbars
    self.bullet_color = bullet_color
    self.shot_offset = 5
    self.bullet_damage = bullet_damage
    self.health = health
    self.max_health = self.health
    self.bullet_list: list[Bullet] = []
    self.shoot_rate = fps / shoot_rate_per_second
    self.last_shot_at = -self.fps
    # Calculate starting points, tkinter requires points to be in format: [x1,y1,x2,y2,...] so thats why they are like that and not [[x1, y1], [x2, y2]], last two are metadata
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
    self.points = utils.calculate_points_metadata(self.points, self.focal_point)
    self.calculate_hitboxes_metadata()
    self.transform(self.angle)

  def calc_bounds_info(self):
    self.bounds_info = utils.get_bounds_info(self.points)

  def move(self):
    # Moves in the current direction by incrementing focal point with speed and recalculating points
    temp = utils.resolve_point(self.focal_point[0], self.focal_point[1], self.speed, self.angle)
    
    # Check if the move will resolve in ship being out of bounds
    out_of_bounds = utils.is_out_of_bounds(self.bounds_info[0], self.bounds_info[1], self.bounds_info[2], self.bounds_info[3], self.canvas_dimensions.get("x"), self.canvas_dimensions.get("y"))
    if not out_of_bounds:
      # If not outside bounds then move in direction
      self.focal_point[0] = temp[0]
      self.focal_point[1] = temp[1]
      self.transform(self.angle)
  
  def shoot_bullet(self, frame_counter: int, seconds_elapsed: int):
    # Check whether ship allowed to shoot
    temp = frame_counter + seconds_elapsed * self.fps

    if temp > self.last_shot_at + self.shoot_rate:
      # Set last shot, to work out whether allowed to shoot on next func call
      self.last_shot_at = temp
      temp = utils.resolve_point(self.points[0], self.points[1], self.shot_offset, self.angle)
      # Create new bullet obj and add to bullet list
      bullet = Bullet(self.canvas, self.canvas_dimensions, self.bullet_width, self.bullet_height, list(temp), self.bullet_speed, self.bullet_damage, self.angle, self.fps, self.bullet_color, self.display_hitboxes)
      self.bullet_list.append(bullet)
    
  def calculate_hitboxes_metadata(self):
    # Same as points metadata generation, but iterate throught every hitbox
    for i in range(len(self.hitboxes)):
      hitbox = utils.calculate_points_metadata(self.hitboxes[i], self.focal_point)
      self.hitboxes[i] = hitbox
  
  def transform(self, angle: float):
    # Driver code for transforming points using generic transform function
    self.angle = angle
    temp = utils.transform(self.focal_point, self.angle, self.points, self.hitboxes)
    self.points = temp[0]
    self.hitboxes = temp[1]

  def draw_hitboxes(self):
    # Draws the box via lines
    for hitbox in self.hitboxes:
      self.canvas.create_line(hitbox[0], hitbox[1], hitbox[2], hitbox[3])
      self.canvas.create_line(hitbox[2], hitbox[3], hitbox[4], hitbox[5])
      self.canvas.create_line(hitbox[4], hitbox[5], hitbox[6], hitbox[7])
      self.canvas.create_line(hitbox[6], hitbox[7], hitbox[0], hitbox[1])

  def draw_healthbar(self):
    healthbar_height = 10
    healthbar_offset = 5
    health_present_color = "#44ff00"
    health_absent_color = "#ff0000"
    missing_health = self.max_health - self.health
    missing_health_percentage = missing_health / self.max_health
    # First, create present health rectangle using min_x and min_y as top left corner of rectangle, and max_x and min_y + healthbar_height as right bottom corner
    self.canvas.create_rectangle(self.bounds_info[0], self.bounds_info[2] - healthbar_offset - healthbar_height, self.bounds_info[1], self.bounds_info[2] - healthbar_offset, fill= health_present_color)
    # Only draw missing health if there is missing health
    if missing_health > 0:
      # Then, create missing health rectangle, calcl difference in min_x and max_x and multiply by missing_health percent to find needed width of missing health portion. Draw over present health bar
      self.canvas.create_rectangle(self.bounds_info[1] - missing_health_percentage * (self.bounds_info[1] - self.bounds_info[0]), self.bounds_info[2] - healthbar_offset - healthbar_height, self.bounds_info[1], self.bounds_info[2] - healthbar_offset, fill=health_absent_color)

  def delete_redundant_bullets(self):
    # Deletes entries from bullet list if the bullet is completely out of field
    delete_indexes = []
    for bullet_index in range(len(self.bullet_list)):
      bullet = self.bullet_list[bullet_index]
      bounds_info = utils.get_bounds_info(bullet.points)
      fully_out_of_bounds = utils.is_fully_out_of_bounds(bounds_info[0], bounds_info[1], bounds_info[2], bounds_info[3], self.canvas_dimensions.get("x"), self.canvas_dimensions.get("y"))
      # Check if the bullet is completely out of bounds
      if fully_out_of_bounds:
        delete_indexes.append(bullet_index)
    
    # Delete redundant bullets from bullet list
    for i in range(len(delete_indexes)):
      delete_index = delete_indexes[i]
      self.bullet_list.pop(delete_index)
      # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
      for j in range(len(delete_indexes)):
        if delete_indexes[j] > delete_index:
          delete_indexes[j] -= 1

  def handle_bullets(self):
    self.delete_redundant_bullets()
    # Move bullets 
    for i in range(len(self.bullet_list)):
      bullet = self.bullet_list[i]
      bullet.move()

  def draw(self):
    # Draw ship
    self.canvas.create_polygon(self.points[0:len(self.points) - 2], fill=self.color)
    # Driver code for drawing all bullets
    for i in range(len(self.bullet_list)):
      bullet = self.bullet_list[i]
      bullet.draw()
    # If hitboxes display is on, display hitboxes of the ship
    if self.display_hitboxes:
      self.draw_hitboxes()
    if self.display_hitbars:
      self.draw_healthbar()
  
  def on_frame(self):
    self.calc_bounds_info()
    self.handle_bullets()
    self.draw()
    

class Game:
  # Class for the game, includes frame trigger, pause/resume functions and etc.
  def __init__(self, main_window: tk.Tk, config: dict):
    self.canvas_dimensions = {
      "x": 1000,
      "y" : 850
    }
    self.main_window = main_window
    self.config = config
    self.controls = self.config.get("controls")
    self.game_config = self.config.get("game")
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
    # Tkinter can't handle 60 fps reliably
    self.fps = 45
    self.ms_interval = math.floor(1000 / self.fps)
    self.frame_counter = 1
    self.seconds_elapsed = 0
    self.angle = 0
    self.player_width = 45
    self.player_height = 50
    self.player_speed_per_second = 400
    self.player_bullet_width = 10
    self.player_bullet_height = 20
    self.player_bullet_speed_per_second = 500
    self.player_bullet_damage = 1
    self.player_color = "#41bfff"
    self.player_shoot_rate_per_second = 2.5
    self.player_health = 5
    self.enemy_ship_spawn_interval_seconds = 1
    self.enemy_ship_health = 2
    self.enemy_ship_bullet_speed_per_second = 150
    self.enemy_ship_bullet_damage = 1
    self.enemy_ship_color = "#ff0fcb"
    self.enemy_ship_width = 50
    self.enemy_ship_height = 55
    self.enemy_ship_bullet_width = 8
    self.enemy_ship_bullet_height = 18
    self.no_enemy_spawn_around_player_radius = 300
    self.enemy_ship_speed_per_second = 100
    self.enemy_ship_shoot_rate_per_second_min = 0.5
    self.enemy_ship_shoot_rate_per_second_max = 0.7
    self.min_distance_between_bounds = 5
    self.enemy_ships_list = []
    self.max_enemies_on_screen = 1
    self.display_hitboxes = self.game_config.get("display_hitboxes") == "True"
    self.display_hitbars = self.game_config.get("display_hitbars") == "True"
    # Used for determining state of game (paused or not) and for pausing the canvas after
    self.next_frame_after_id = 0
    # Initialize player ship object
    self.player = Ship(
      self.canvas,
      self.player_width,
      self.player_height,
      [self.canvas_centre_x, self.canvas_centre_y],
      self.angle,
      self.player_color,
      self.fps,
      self.canvas_dimensions,
      self.player_speed_per_second,
      self.display_hitboxes,
      self.display_hitbars,
      self.player_bullet_width,
      self.player_bullet_height,
      self.player_bullet_speed_per_second,
      self.player_color,
      self.player_bullet_damage,
      self.player_shoot_rate_per_second,
      self.player_health
    )
    # Bind events
    self.canvas.bind("<Motion>", self.on_cursor_move)
    self.main_window.bind("<Key>", self.on_key_press)
    self.canvas.bind("<Button-1>", self.on_click)
    self.next_frame_after_id = self.canvas.after(self.ms_interval, self.on_frame)
  
  def is_point_usable(self, x, y):
    # Check that point generated is valid, i.e  not occupied by anything
    # Check that point is not within no spawn radius around player
    distance_to_player = utils.calculate_length(x, y, self.player.focal_point[0], self.player.focal_point[1])
    if distance_to_player < self.no_enemy_spawn_around_player_radius + max(self.player.ship_width, self.player.ship_height):
      return False
    
    # Check that point is not occupied by any other enemy ship
    for enemy_ship in self.enemy_ships_list:
      distance_to_enemy_ship = utils.calculate_length(x, y, enemy_ship.focal_point[0], enemy_ship.focal_point[1])
      if distance_to_enemy_ship < max(enemy_ship.ship_width, enemy_ship.ship_height) + self.min_distance_between_bounds:
        return False

    return True

  def generate_random_point(self):
    # Generate a random point not occupied by anything
    min_x = math.ceil(self.enemy_ship_width / 2 + self.min_distance_between_bounds)
    max_x = math.ceil(self.canvas_dimensions.get("x") - self.enemy_ship_width / 2 - self.min_distance_between_bounds)
    min_y = math.ceil(self.enemy_ship_height / 2 + self.min_distance_between_bounds)
    max_y = math.ceil(self.canvas_dimensions.get("y") - self.enemy_ship_height / 2 - self.min_distance_between_bounds)
    point_x = random.randint(min_x, max_x)
    point_y = random.randint(min_y, max_y)
    # While point is occupied by something, keep generating new random points
    while self.is_point_usable(point_x, point_y) == False:
      point_x = random.randint(min_x, max_x)
      point_y = random.randint(min_y, max_y)

    return [point_x, point_y]
      
  def spawn_enemy_ship(self):
    # Spawn a new enemy ship in a valid random position
    if len(self.enemy_ships_list) < self.max_enemies_on_screen:
      
      spawn_point = self.generate_random_point()
      # Calc angle to player, to avoid bug with user not moving mouse and ships are forever stuck shooting away from player
      angle_to_player = utils.resolve_angle(spawn_point[0], spawn_point[1], self.player.focal_point[0], self.player.focal_point[1])
      enemy_ship = Ship(
        self.canvas,
        self.enemy_ship_width,
        self.enemy_ship_height,
        spawn_point,
        angle_to_player,
        self.enemy_ship_color,
        self.fps,
        self.canvas_dimensions,
        self.enemy_ship_speed_per_second,
        self.display_hitboxes,
        self.display_hitbars,
        self.enemy_ship_bullet_width,
        self.enemy_ship_bullet_height,
        self.enemy_ship_bullet_speed_per_second,
        self.enemy_ship_color,
        self.enemy_ship_bullet_damage,
        random.uniform(self.enemy_ship_shoot_rate_per_second_min, self.enemy_ship_shoot_rate_per_second_max),
        self.enemy_ship_health
      )
      self.enemy_ships_list.append(enemy_ship)

  def handle_timed_events(self):
    if self.seconds_elapsed % self.enemy_ship_spawn_interval_seconds == 0:
      self.spawn_enemy_ship()
    pass

  def handle_enemy_ships(self):
    for enemy_ship in self.enemy_ships_list:
      enemy_ship.shoot_bullet(self.frame_counter, self.seconds_elapsed)
      enemy_ship.on_frame()
      self.handle_enemy_bullets_collisions(enemy_ship)

  def on_frame(self):
    # Deletes everything from the canvas
    self.canvas.delete("all")
    # Call onframe function of player
    self.player.on_frame()
    self.handle_player_bullets_collisions()
    self.handle_enemy_ships()
    # Increase ingame time variables
    self.frame_counter += 1
    if(self.frame_counter > self.fps):
      self.frame_counter = 1
      self.seconds_elapsed += 1
      self.handle_timed_events()
    
    self.next_frame_after_id = self.canvas.after(self.ms_interval, self.on_frame)
    pass
  
  def point_enemy_ships_to_player(self):
    # Points all enemy ship towards player
    for enemy_ship in self.enemy_ships_list:
      # Calculate angle from enemy ship to the player ship
      angle_to_player = utils.resolve_angle(enemy_ship.focal_point[0], enemy_ship.focal_point[1], self.player.focal_point[0], self.player.focal_point[1])
      enemy_ship.transform(angle_to_player)

  def on_cursor_move(self, event):
    # Adjusts angle variable depending on where user points the cursor
    x = event.x
    y = event.y
    self.angle = utils.resolve_angle(self.player.focal_point[0], self.player.focal_point[1], x, y)
    self.player.transform(self.angle)
    self.point_enemy_ships_to_player()
  
  def on_key_press(self, event):
    # Handles key presses
    key = event.char
    # Movement key events trigger, trigger if game is not paused
    if self.controls.get("move") == key and self.next_frame_after_id != 0:
      self.player.move()
      # Fix for a bug where ships won't point at player if he just moves without moving mouse around
      self.point_enemy_ships_to_player()
    elif self.controls.get("pause/unpause") == key:
      # If game is paused, resume
      if self.next_frame_after_id == 0:
        self.resume()
      # If not paused, pause
      else:
        self.pause()
  
  def on_click(self, event):
    self.player.shoot_bullet(self.frame_counter, self.seconds_elapsed)
  
  def resume(self):
    # Assign next after id and assign after
    self.next_frame_after_id = self.canvas.after(self.ms_interval, self.on_frame)

  def pause(self):
    # Cancel canvas after and assign after id = 0
    self.canvas.after_cancel(self.next_frame_after_id)
    self.next_frame_after_id = 0
    self.canvas.create_text(self.canvas_centre_x, self.canvas_centre_y, font="Arial 35 bold", text="Paused")
  
  def gameover(self):
    pass

  def handle_enemy_bullets_collisions(self, enemy_ship: Ship):
    delete_indexes = []
    # Iterate through enemy bullets
    for i in range(len(enemy_ship.bullet_list)):
      bullet = enemy_ship.bullet_list[i]
      # If bullet collides with player do:
      does_collide_with_player = utils.do_objects_collide(bullet, self.player)
      if does_collide_with_player:
        # Reduce players health with bullet damage
        self.player.health -= bullet.damage
        # If players health is less than or equal to 0, trigget gameover func
        if self.player.health <= 0:
          self.gameover()
        delete_indexes.append(i)

    # Delete redundant bullets from bullet list
    for i in range(len(delete_indexes)):
      delete_index = delete_indexes[i]
      enemy_ship.bullet_list.pop(delete_index)
      # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
      for j in range(len(delete_indexes)):
        if delete_indexes[j] > delete_index:
          delete_indexes[j] -= 1
  
  def handle_player_bullets_collisions(self):
    delete_indexes_player_bullets = []
    delete_indexes_enemy_bullets = []
    delete_indexes_ships = []
    # Iterate through all player bullets
    for i in range(len(self.player.bullet_list)):
      bullet = self.player.bullet_list[i]
      # Iterate through all enemy ships
      for j in range(len(self.enemy_ships_list)):
        enemy_ship = self.enemy_ships_list[j]
        # Iterate through all enemy bullets
        for k in range(len(enemy_ship.bullet_list)):
          enemy_bullet = enemy_ship.bullet_list[k]
          # If player bullet and enemy bullet collide do
          do_collide = utils.do_objects_collide(bullet, enemy_bullet)
          if do_collide:
            # Reduce players bullet damage by enemy bullet damage and vice versa
            temp = enemy_bullet.damage
            enemy_bullet.damage -= self.player.bullet_damage
            bullet.damage -= temp
            # If any bullet has less or equal to 0 damage, mark them for deletion
            if enemy_bullet.damage <= 0:
              # Since we need to know from which ship the bullet came from, add j - index of the ship with k - index of bullet
              delete_indexes_enemy_bullets.append([j, k])
            if bullet.damage <= 0:
              delete_indexes_player_bullets.append(i)
        # If player bullet collides with enemy ship
        do_collide = utils.do_objects_collide(bullet, enemy_ship)
        if do_collide:
          # Reduce enemy ship health with bullet damage
          enemy_ship.health -= bullet.damage
          # If enemy ships health is less than or equal to 0, mark it for deletion
          if enemy_ship.health <= 0:

            delete_indexes_ships.append(j)
          delete_indexes_player_bullets.append(i)
          break

    # Delete everything that is marked for deletion
    # Delete redundant enemy ships from ships list
    for i in range(len(delete_indexes_ships)):
      delete_index = delete_indexes_ships[i]
      self.enemy_ships_list.pop(delete_index)
      # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
      for j in range(len(delete_indexes_ships)):
        if delete_indexes_ships[j] > delete_index:
          delete_indexes_ships[j] -= 1
    
    # Delete redundant player bullets from bullet list
    for i in range(len(delete_indexes_player_bullets)):
      delete_index = delete_indexes_player_bullets[i]
      self.player.bullet_list.pop(delete_index)
      # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
      for j in range(len(delete_indexes_player_bullets)):
        if delete_indexes_player_bullets[j] > delete_index:
          delete_indexes_player_bullets[j] -= 1

    # Delete redundant enemy bullets from bullet lists
    for i in range(len(delete_indexes_enemy_bullets)):
      delete_index = delete_indexes_enemy_bullets[i]
      # Get enemy ship index from delete index elem and pop bullet at second arg
      self.enemy_ships_list[delete_index[0]].bullet_list.pop(delete_index[1])
      # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
      for j in range(len(delete_indexes_enemy_bullets)):
        if delete_indexes_enemy_bullets[j][0] == delete_index[0] and delete_indexes_enemy_bullets[j][1] > delete_index[1]:
          delete_indexes_enemy_bullets[j][1] -= 1
      
      
    
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
    self.parse_config()
    self.on_app_state_change()
    self.main_window.mainloop()

  def create_new_config(self):
    # Creates a new config.ini file with standard settings below
    parser = configparser.ConfigParser()
    parser.add_section("IDENTITY")
    parser.set("IDENTITY", "Name", "Bob the Builder")
    parser.add_section("GAME")
    parser.set("GAME", "Display_Hitboxes", "False")
    parser.set("GAME", "Display_Hitbars", "True")
    parser.add_section("CONTROLS")
    parser.set("CONTROLS", "Move", "w")
    parser.set("CONTROLS", "Pause/Unpause", "space")
    parser.set("CONTROLS", "Boss_Key", "p")
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
      self.config = {}
      controls = {}
      game_config = {}
      # Parse config by sections
      for sect in parser.sections():
        for k, v in parser.items(sect):
          if sect == "IDENTITY":
            self.config["identity"] = v
          elif sect == "GAME":
            game_config[k] = v
          elif sect == "CONTROLS":
            # Tkinter treats space characters as " " thats why it is here
            if v == "space":
              v = " "
            controls[k] = v

      self.config["controls"] = controls
      self.config["game"] = game_config
  
  def on_app_state_change(self):
    # Destroy children widgets to reset the window on state change
    list = self.main_window.grid_slaves()
    for l in list:
      l.destroy()
    
    if self.state == "game":
      game = Game(self.main_window, self.config)
    pass
  
  

def main():
  global utils
  utils = Utilities()
  app = Application()
  
  

if __name__ == "__main__":
  main()