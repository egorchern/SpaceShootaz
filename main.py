"""Copyright - Egor Chernyshev 27/11/2021. SpaceShootaz - game made for University of Manchester 16321 Python coursework
Window size: 1600 x 900
Window should not be resizable but still, DO NOT RESIZE THE WINDOW. Window initializes with correct size at start
"""
import tkinter as tk
import math
import configparser
import pathlib
import os
import random
import re
import pickle
from tkinter import filedialog
from tkinter import messagebox

utils = 0
bullet_volley_offset = 6
main_window = None
Canvas = None
thread_count = 2
# Points have last two elements as metadata, so thats why it is len(points) - 2
# On frame is a function that triggers every frame


class Utilities:
    """Class for utility functions, such as resolve angle and resolve point"""

    def __init__(self):
        pass

    def radians_to_degrees(self, radians: float) -> float:
        """Converts radians to degrees"""
        return radians * (180 / math.pi)

    def resolve_angle(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculates angle between (x1, y1) and (x2, y2) relative to positive y-axis"""
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
            angle = math.pi
        elif x_diff < 0 and y_diff == 0:
            # if staight left
            angle = 3/2 * math.pi
        else:
            # if points are equal
            angle = 0
        return angle

    def resolve_point(self, x1: float, y1: float, length: float, angle: float) -> list:
        """Calculates (x2, y2) point translated using angle with given angle, length and a reference point."""
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

        return [x1 + x_offset, y1 + y_offset]

    def calculate_length(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """calculates length between two points"""
        return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

    def get_bounds_info(self, points: list) -> list:
        """Returns information about object bounds"""
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
        """Calculates if the object is out of bounds using the box model"""
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
        """Similar to is_out_of_bounds but checks if object is completely out of viewable space"""
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

    def transform(self, focal_point: list, angle: float, points: list, hitboxes: list) -> list:
        """Tilts points by given angle and returns the points array"""
        for i in range(0, len(points) - 2, 2):
            # Resolves the new point, when the current point is tilted at current angle
            temp = self.resolve_point(
                focal_point[0], focal_point[1], points[-2][i // 2], points[-1][i // 2] + angle)
            points[i] = temp[0]
            points[i + 1] = temp[1]
        # Tilts hitboxes
        for j in range(len(hitboxes)):
            hitbox = hitboxes[j]
            for i in range(0, len(hitbox) - 2, 2):
                # Resolve the same as with object points, just do for every hitbox
                temp = self.resolve_point(
                    focal_point[0], focal_point[1], hitbox[-2][i // 2], hitbox[-1][i // 2] + angle)
                hitbox[i] = temp[0]
                hitbox[i + 1] = temp[1]

        return [points, hitboxes]

    def calculate_points_metadata(self, points: list, focal_point: list) -> list:
        """Calculates reference angles for using them to offset tilt calculation"""
        lengths = []
        angles = []
        for i in range(0, len(points), 2):
            x = points[i]
            y = points[i + 1]
            length = self.calculate_length(
                focal_point[0], focal_point[1], x, y)
            lengths.append(length)
            angle = self.resolve_angle(focal_point[0], focal_point[1], x, y)
            angles.append(angle)
        points.append(lengths)
        points.append(angles)
        return points

    def do_hitboxes_collide(self, hitbox1: list, hitbox2: list) -> bool:
        """Calculate whether hitboxes collide using Separating Axis Theorem"""
        # Get all edge vectors
        #vectors = [[hitbox1[0] - hitbox1[2], hitbox1[1] - hitbox1[3]], [hitbox1[2] - hitbox1[4], hitbox1[3] - hitbox1[5]], [hitbox1[4] - hitbox1[6], hitbox1[5] - hitbox1[7]], [hitbox1[6] - hitbox1[0], hitbox1[7] - hitbox1[1]], [hitbox1[0] - hitbox1[2], hitbox1[1] - hitbox1[3]], [hitbox1[2] - hitbox1[4], hitbox1[3] - hitbox1[5]], [hitbox2[4] - hitbox2[6], hitbox2[5] - hitbox2[7]], [hitbox2[6] - hitbox2[0], hitbox2[7] - hitbox2[1]]]

        vectors = [
            [hitbox1[0] - hitbox1[2], hitbox1[1] - hitbox1[3]],
            [hitbox1[2] - hitbox1[4], hitbox1[3] - hitbox1[5]],
            [hitbox2[0] - hitbox2[2], hitbox2[1] - hitbox2[3]],
            [hitbox2[2] - hitbox2[4], hitbox2[3] - hitbox2[5]]
        ]
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
        """Generic object collision driver function, iterates through hitboxes of first object and compares with each hitbox in second object"""
        hitboxes1 = obj1.hitboxes
        hitboxes2 = obj2.hitboxes
        for i in range(len(hitboxes1)):
            hitbox1 = hitboxes1[i]
            for j in range(len(hitboxes2)):
                hitbox2 = hitboxes2[j]
                do_collide = self.do_hitboxes_collide(hitbox1, hitbox2)
                if do_collide == True:
                    # If at least pair of hitboxes collide, return True
                    return True

        # If no hitboxes collide, then objects don't collide, return False
        return False

    # def separate_list_into_index_parts(self, lst: list, parts: int) -> list[list]:
    #   """Separates a list into n lists, with excess elements going equally into first lists"""
    #   output = []
    #   part_count = len(lst) // parts
    #   i = 0
    #   for k in range(parts):
    #     current_count = 0
    #     current_list = []
    #     while current_count < part_count:
    #       current_list.append(i)
    #       i += 1
    #       current_count += 1
    #     output.append(current_list)
    #   counter = 0
    #   while i < len(lst):
    #     output[counter].append(i)
    #     counter += 1
    #     i += 1
    #   return output

    def get_leaderboard_data(self, file_path: str) -> list:
        """Gets leaderboard data from a file_path and returns a processed list"""
        def extract_info(string: str):
            info = []
            temp = re.search("\d+\) (?P<name>[^:]+):(?P<score>.*)", string)
            score = float(temp.group("score"))
            name = temp.group("name")
            info.append(name)
            info.append(score)
            return info
        output = []
        file = open(file_path, "r+")
        lines = file.readlines()
        for line in lines:
            info = extract_info(line)
            output.append(info)
        return output

    def display_leaderboard(self, file_path: str) -> None:
        """Displays the leaderboard via tk messagebox"""
        file = open(file_path, "r")
        to_write = file.read()
        tk.messagebox.showinfo("Leaderboard", to_write)


class Bomb:
    """Generic class for bomb"""

    def __init__(
        self,
        focal_point: list,
        blast_delay_in_seconds: float,
        blast_radius: float,
        blast_radius_color: str,
        blast_damage: float,
        fps: int,
        show_blast_seconds: float
    ):
        self.focal_point = focal_point

        self.blast_radius = blast_radius
        self.blast_radius_color = blast_radius_color
        self.blast_damage = blast_damage
        self.fps = fps
        self.image_paths = ["images/bomb_1_r.png", "images/bomb_2_r.png",
                            "images/bomb_3_r.png", "images/bomb_4_r.png"]
        self.len_image_paths = len(self.image_paths)
        self.blast_counter = 0
        self.blast_delay = blast_delay_in_seconds * self.fps
        self.show_blast_frames = show_blast_seconds * self.fps
        self.blast_radius_rectangle = [self.focal_point[0] - self.blast_radius, self.focal_point[1] -
                                       self.blast_radius, self.focal_point[0] + self.blast_radius, self.focal_point[1] + self.blast_radius]
        self.blast_radius_width = 1
        # 5 stages, last one is actual damage taken
        self.bomb_stage = -1
        self.is_different_stage = False
        self.bomb_image = None

    def is_redundant(self):
        """Determines if a bomb is redundant"""
        if self.blast_counter > self.blast_delay + self.show_blast_frames:
            return True
        else:
            False

    def on_frame(self):
        """On frame event for bomb"""
        self.blast_counter += 1
        if self.blast_counter <= self.blast_delay + self.show_blast_frames:
            stage_percentage = self.blast_counter / self.blast_delay
            temp = math.floor(stage_percentage * self.len_image_paths)
            if temp != self.bomb_stage:
                self.is_different_stage = True
                self.bomb_stage = temp
            else:
                self.is_different_stage = False

            # self.draw()

    def draw(self):
        """Draws the bomb on the canvas"""
        # Optimization to only instantiate new image if the stage is different
        # if self.is_different_stage and self.bomb_stage < self.len_image_paths or self.bomb_image == None and self.bomb_stage < self.len_image_paths:
        if (self.is_different_stage or self.bomb_image == None) and self.bomb_stage < self.len_image_paths:
            self.bomb_image = tk.PhotoImage(
                file=self.image_paths[self.bomb_stage])

        if self.bomb_stage < self.len_image_paths:
            # Instantiate image data

            # Draw the bomb itself
            canvas.create_image(
                self.focal_point[0], self.focal_point[1], image=self.bomb_image)
            # Draw blast radius
            canvas.create_oval(self.blast_radius_rectangle[0], self.blast_radius_rectangle[1], self.blast_radius_rectangle[2],
                               self.blast_radius_rectangle[3], outline=self.blast_radius_color, width=self.blast_radius_width)
        else:
            # If bomb has exploded, fill explosion radius to indicate blast
            canvas.create_oval(self.blast_radius_rectangle[0], self.blast_radius_rectangle[1], self.blast_radius_rectangle[2],
                               self.blast_radius_rectangle[3], outline=self.blast_radius_color, fill=self.blast_radius_color, width=self.blast_radius_width)


class Bullet:
    """Class for bullet, created by some ship, uses similar properties as ship, so refer to ship class for more documentation"""

    def __init__(self, canvas_dimensions: dict, width, height, focal_point, speed, damage, angle, fps, color, display_hitboxes):
        canvas_dimensions = canvas_dimensions
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
        self.points = utils.calculate_points_metadata(
            self.points, self.focal_point)
        self.calculate_hitboxes_metadata()
        self.transform(self.angle)

    def transform(self, angle: float):
        """Driver code for transforming points using generic transform function"""
        self.angle = angle
        temp = utils.transform(
            self.focal_point, self.angle, self.points, self.hitboxes)
        self.points = temp[0]
        self.hitboxes = temp[1]

    def calculate_hitboxes_metadata(self):
        """Same as points metadata generation, but iterate throught every hitbox"""
        for i in range(len(self.hitboxes)):
            hitbox = utils.calculate_points_metadata(
                self.hitboxes[i], self.focal_point)
            self.hitboxes[i] = hitbox

    def move(self):
        """Moves in the current direction by incrementing focal point with speed and recalculating points"""
        temp = utils.resolve_point(
            self.focal_point[0], self.focal_point[1], self.speed, self.angle)
        self.focal_point[0] = temp[0]
        self.focal_point[1] = temp[1]
        self.transform(self.angle)

    def draw_hitboxes(self):
        """Draws the box via lines"""
        for hitbox in self.hitboxes:
            canvas.create_line(hitbox[0], hitbox[1], hitbox[2], hitbox[3])
            canvas.create_line(hitbox[2], hitbox[3], hitbox[4], hitbox[5])
            canvas.create_line(hitbox[4], hitbox[5], hitbox[6], hitbox[7])
            canvas.create_line(hitbox[6], hitbox[7], hitbox[0], hitbox[1])

    def draw(self):
        """Draws the bullet"""
        canvas.create_polygon(
            self.points[0:len(self.points) - 2], fill=self.color)
        # If hitboxes display is on, display hitboxes of the ship
        if self.display_hitboxes:
            self.draw_hitboxes()


class Ship:
    """Generic ship class, with functions like tilt"""

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
        bullets_per_volley: int,
        health: int
    ):

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
        self.bullets_per_volley = bullets_per_volley
        self.volley_bullets_offset = bullet_volley_offset + self.bullet_width
        self.bullet_damage = bullet_damage
        self.health = health
        self.max_health = self.health
        self.bullet_list: list[Bullet] = []
        self.shoot_rate_per_second = shoot_rate_per_second
        self.shoot_rate = fps / shoot_rate_per_second
        self.last_shot_at = -self.fps
        # Calculate starting points, tkinter requires points to be in format: [x1,y1,x2,y2,...] so thats why they are like that and not [[x1, y1], [x2, y2]], last two are metadata
        self.points = [
            self.focal_point[0],
            self.focal_point[1] - self.top_ship_section_percentage * height,
            self.focal_point[0] + self.head_width_percentage * (width / 2),
            self.focal_point[1] - self.top_ship_section_percentage *
            height * self.body_height_percentage,
            self.focal_point[0] + width / 2,
            self.focal_point[1],
            self.focal_point[0] + width / 2,
            self.focal_point[1] +
            (1 - self.top_ship_section_percentage) * height,
            self.focal_point[0] +
            (1 - self.wing_flap_width_percentage) * width / 2,
            self.focal_point[1],
            self.focal_point[0] -
            (1 - self.wing_flap_width_percentage) * width / 2,
            self.focal_point[1],
            self.focal_point[0] - width / 2,
            self.focal_point[1] +
            (1 - self.top_ship_section_percentage) * height,
            self.focal_point[0] - width / 2,
            self.focal_point[1],
            self.focal_point[0] - self.head_width_percentage * (width / 2),
            self.focal_point[1] - self.top_ship_section_percentage *
            height * self.body_height_percentage
        ]
        # Hitboxes have format: [[top_left, top_right, bottom_right, bottom_left]]
        self.hitboxes = [
            [
                self.focal_point[0] - self.head_width_percentage * (width / 2),
                self.focal_point[1] -
                self.top_ship_section_percentage * height,
                self.focal_point[0] + self.head_width_percentage * (width / 2),
                self.focal_point[1] -
                self.top_ship_section_percentage * height,
                self.focal_point[0] + self.head_width_percentage * (width / 2),
                self.focal_point[1] - self.top_ship_section_percentage *
                height * self.body_height_percentage,
                self.focal_point[0] - self.head_width_percentage * (width / 2),
                self.focal_point[1] - self.top_ship_section_percentage *
                height * self.body_height_percentage,
            ],
            [
                self.focal_point[0] - width / 2,
                self.focal_point[1] - self.top_ship_section_percentage *
                height * self.body_height_percentage,
                self.focal_point[0] + width / 2,
                self.focal_point[1] - self.top_ship_section_percentage *
                height * self.body_height_percentage,
                self.focal_point[0] + width / 2,
                self.focal_point[1] +
                (1 - self.top_ship_section_percentage) * height,
                self.focal_point[0] - width / 2,
                self.focal_point[1] +
                (1 - self.top_ship_section_percentage) * height
            ]
        ]
        # Calculate lengths angles from focal to points, used in tilt point calculation
        self.points = utils.calculate_points_metadata(
            self.points, self.focal_point)
        self.calculate_hitboxes_metadata()
        self.calc_bounds_info()
        self.transform(self.angle)

    def shoot_volley(self, frame_counter: int, seconds_elapsed: int):
        """Shoots a volley of bullets_per_volley num of bullets if is allowed to shoot"""
        # Check whether ship allowed to shoot
        temp = frame_counter + seconds_elapsed * self.fps
        if temp > self.last_shot_at + self.shoot_rate:
            # Set last shot, to work out whether allowed to shoot on next func call
            self.last_shot_at = temp
            # Work out initial shooting point
            initial_focal = utils.resolve_point(
                self.points[0], self.points[1], self.shot_offset, self.angle)
            bullets_remaining = self.bullets_per_volley
            # If bullets num is odd, shoot one from initial point
            if bullets_remaining % 2 == 1:
                self.shoot_bullet(initial_focal)
                bullets_remaining -= 1
            offset_coef = 1
            # If bullets num was initially even, then make offset shorter to avoid having one bullet space blank
            if bullets_remaining == self.bullets_per_volley:
                offset_coef = 0.5
            while bullets_remaining > 0:
                # Work out focal points for left bullet and right bullet, multiply offset by coefficient to move focal point along the shooting line, and shoot bullets
                left_focal = utils.resolve_point(
                    initial_focal[0], initial_focal[1], self.volley_bullets_offset * offset_coef, 3/2 * math.pi + self.angle)
                right_focal = utils.resolve_point(
                    initial_focal[0], initial_focal[1], self.volley_bullets_offset * offset_coef, 1/2 * math.pi + self.angle)
                self.shoot_bullet(left_focal)
                self.shoot_bullet(right_focal)
                bullets_remaining -= 2
                offset_coef += 1

    def calc_bounds_info(self):
        """Calculate bound info such as min_x and etc"""
        self.bounds_info = utils.get_bounds_info(self.points)

    def move(self):
        """Moves in the current direction by incrementing focal point with speed and recalculating points"""
        temp = utils.resolve_point(
            self.focal_point[0], self.focal_point[1], self.speed, self.angle)

        # Check if the move will resolve in ship being out of bounds
        out_of_bounds = utils.is_out_of_bounds(self.bounds_info[0], self.bounds_info[1], self.bounds_info[2],
                                               self.bounds_info[3], self.canvas_dimensions.get("x"), self.canvas_dimensions.get("y"))
        if not out_of_bounds:
            # If not outside bounds then move in direction
            self.focal_point[0] = temp[0]
            self.focal_point[1] = temp[1]
            self.transform(self.angle)

    def shoot_bullet(self, focal_point: list):
        """Simply creates a new bullet at some focal_point and adds it to the bullet list"""
        bullet = Bullet(self.canvas_dimensions, self.bullet_width, self.bullet_height, focal_point,
                        self.bullet_speed, self.bullet_damage, self.angle, self.fps, self.bullet_color, self.display_hitboxes)
        self.bullet_list.append(bullet)

    def calculate_hitboxes_metadata(self):
        """Same as points metadata generation, but iterate throught every hitbox"""
        for i in range(len(self.hitboxes)):
            hitbox = utils.calculate_points_metadata(
                self.hitboxes[i], self.focal_point)
            self.hitboxes[i] = hitbox

    def transform(self, angle: float):
        """Driver code for transforming points using generic transform function"""
        self.angle = angle
        temp = utils.transform(
            self.focal_point, self.angle, self.points, self.hitboxes)
        self.points = temp[0]
        self.hitboxes = temp[1]

    def draw_hitboxes(self):
        """Draws the box via lines"""
        for hitbox in self.hitboxes:
            canvas.create_line(hitbox[0], hitbox[1], hitbox[2], hitbox[3])
            canvas.create_line(hitbox[2], hitbox[3], hitbox[4], hitbox[5])
            canvas.create_line(hitbox[4], hitbox[5], hitbox[6], hitbox[7])
            canvas.create_line(hitbox[6], hitbox[7], hitbox[0], hitbox[1])

    def draw_healthbar(self):
        """Draws healthbar"""
        healthbar_height = 10
        healthbar_offset = 5
        health_present_color = "#44ff00"
        health_absent_color = "#ff0000"
        missing_health = self.max_health - self.health
        missing_health_percentage = missing_health / self.max_health
        # First, create present health rectangle using min_x and min_y as top left corner of rectangle, and max_x and min_y + healthbar_height as right bottom corner
        canvas.create_rectangle(self.bounds_info[0], self.bounds_info[2] - healthbar_offset - healthbar_height,
                                self.bounds_info[1], self.bounds_info[2] - healthbar_offset, fill=health_present_color)
        # Only draw missing health if there is missing health
        if missing_health > 0:
            # Then, create missing health rectangle, calcl difference in min_x and max_x and multiply by missing_health percent to find needed width of missing health portion. Draw over present health bar
            canvas.create_rectangle(self.bounds_info[1] - missing_health_percentage * (self.bounds_info[1] - self.bounds_info[0]), self.bounds_info[2] -
                                    healthbar_offset - healthbar_height, self.bounds_info[1], self.bounds_info[2] - healthbar_offset, fill=health_absent_color)

    def delete_redundant_bullets(self):
        """Deletes entries from bullet list if the bullet is completely out of field"""
        delete_indexes = []
        for bullet_index in range(len(self.bullet_list)):
            bullet = self.bullet_list[bullet_index]
            bounds_info = utils.get_bounds_info(bullet.points)
            fully_out_of_bounds = utils.is_fully_out_of_bounds(
                bounds_info[0], bounds_info[1], bounds_info[2], bounds_info[3], self.canvas_dimensions.get("x"), self.canvas_dimensions.get("y"))
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
        """Handles all the bullets, such as moving the bullets and deleting redundant ones"""
        self.delete_redundant_bullets()
        # Move bullets
        for i in range(len(self.bullet_list)):
            bullet = self.bullet_list[i]
            bullet.move()

    def draw(self):
        """Draw ship"""
        canvas.create_polygon(
            self.points[0:len(self.points) - 2], fill=self.color)
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
        """On frame for ship"""
        self.calc_bounds_info()
        self.handle_bullets()
        # self.draw()


class Game:
    """ Class for the game, includes frame trigger, pause/resume functions and etc. """

    def __init__(self, main_window_dimensions: dict, config: dict, change_app_state):
        self.change_app_state = change_app_state
        # main_window.columnconfigure(0, weight=1)
        # main_window.columnconfigure(1, weight=1)
        self.config = config
        self.save_file_path = self.config["save_file_path"]
        self.leaderboard_file_path = self.config["game"]["leaderboard_file_path"]
        self.identity = self.config["game"]["name"]
        self.main_window_dimensions = main_window_dimensions
        self.controls = self.config.get("controls")
        self.game_config = self.config.get("game")
        self.spreadsheet_overlay = None
        self.canvas_dimensions = {
            "x": self.main_window_dimensions.get("x") - 440,
            "y": self.main_window_dimensions.get("y") - 20
        }
        global canvas
        canvas = tk.Canvas(
            master=main_window,
            width=self.canvas_dimensions.get("x"),
            height=self.canvas_dimensions.get("y"),
            bg="white",
            relief="solid",
            borderwidth=1
        )
        canvas.grid(padx=5, pady=5, sticky="WE")

        self.canvas_centre_x = self.canvas_dimensions.get("x") // 2
        self.canvas_centre_y = self.canvas_dimensions.get("y") // 2
        # Tkinter can't handle 60 fps reliably
        self.fps = 40
        self.ms_interval = math.floor(1000 / self.fps)
        self.frame_counter = 1
        self.seconds_elapsed = 0
        self.angle = 0
        self.min_distance_between_bounds = 5
        self.enemy_ships_list: list[Ship] = []
        self.display_hitboxes = self.game_config.get(
            "display_hitboxes") == "True"
        self.display_hitbars = self.game_config.get(
            "display_hitbars") == "True"
        # 0 - in progress, 1 - ended, 2 - upgrading,
        self.game_state = 0
        # Used for determining state of game (paused or not) and for pausing the canvas after
        self.next_frame_after_id = 0
        self.remnant_bullets: list[Bullet] = []

        self.enemy_bomb_list: list[Bomb] = []
        # Call initial variables initializers
        self.define_player_initial_variables()
        self.define_enemy_initial_variables()
        self.define_bomb_initial_variables()
        self.define_player_scaling_variables()
        self.define_enemy_scaling_variables()
        self.define_bomb_scaling_variables()
        self.define_score_variables()
        self.instantiate_player()
        # Spawn enemy ship straight away, otherwise it is too boring at the start
        self.spawn_enemy_ship()
        # Doesn't work if in a function
        # If there is a save_file in parameters then Load the saved game via pickle
        if self.save_file_path != "":
            file = open(self.save_file_path, 'rb')
            self: Game = pickle.load(file)
            file.close()
        self.process_cheats()
        self.create_right_menu()
        # Bind events
        canvas.bind("<Motion>", self.on_cursor_move)
        main_window.bind("<Key>", self.on_key_press)
        canvas.bind("<Button-1>", self.on_click)
        self.next_frame_after_id = canvas.after(
            self.ms_interval, self.on_frame)
        # Draw everything and pause
        self.draw_everything()
        self.pause()

    def create_right_menu(self):
        """Creates initial Tkinter elements of the right menu"""
        self.right_menu = {

        }
        self.right_menu["right_menu"] = tk.Frame(
            master=main_window, bg="white")
        button_font = "Arial 13"
        score_font = "Arial 24"
        # Define buttons
        self.right_menu["back_button"] = tk.Button(
            master=self.right_menu["right_menu"], text="Back to Menu", height=3, font=button_font)
        self.right_menu["save_button"] = tk.Button(
            master=self.right_menu["right_menu"], text="Save game", height=3, font=button_font)
        self.right_menu["back_button"].grid(
            row=0, column=0, columnspan=1, padx=10, sticky="EW")
        self.right_menu["save_button"].grid(
            row=0, column=1, columnspan=1, padx=10, sticky="WE")
        self.right_menu["right_menu"].columnconfigure(0, weight=1)
        self.right_menu["right_menu"].columnconfigure(1, weight=1)

        # Define player name label
        self.right_menu["player_name"] = tk.Label(
            master=self.right_menu["right_menu"], text=f"Name: {self.identity}", font=score_font, bg="white")
        self.right_menu["player_name"].grid(
            row=1, column=0, columnspan=2, pady=10, sticky="EW")
        # Define score labels
        score_row = tk.Frame(self.right_menu["right_menu"], bg="white")
        self.right_menu["score_label"] = tk.Label(
            score_row, text=f"Score: {self.score}", font=score_font, pady=10, bg="white")
        self.right_menu["score_label"].grid(
            row=0, column=0, columnspan=2, sticky="EW")

        self.right_menu["score_per_second_label"] = tk.Label(
            score_row, text=f"Score/sec: {self.score_per_second}", font=button_font, pady=5, padx=4, bg="white")
        self.right_menu["score_per_second_label"].grid(row=1, column=0)

        self.right_menu["score_per_enemy_label"] = tk.Label(
            score_row, text=f"Score/enemy: {self.score_per_enemy}", font=button_font, pady=5, padx=4, bg="white")
        self.right_menu["score_per_enemy_label"].grid(row=1, column=1)

        score_row.grid(row=2, column=0, columnspan=2)

        player_info_row = tk.Frame(self.right_menu["right_menu"], bg="white")
        # Need: hp, regen, atk_speed, damage, speed
        # Define player info labels
        self.right_menu["player_label"] = tk.Label(
            player_info_row, bg="white", text=f"Player stats (upgr_in: {self.player_upgrade_interval_seconds - (self.seconds_elapsed % self.player_upgrade_interval_seconds)})", font=score_font)
        self.right_menu["player_label"].grid(
            row=0, column=0, columnspan=5, pady=5, sticky="NEWS")

        self.right_menu["self.player_health_label"] = tk.Label(
            player_info_row, text=f"Hp: {self.player.health}/{self.player.max_health}", bg="white", font=button_font)
        self.right_menu["self.player_health_label"].grid(row=1, column=0)

        self.right_menu["player_regen_label"] = tk.Label(
            player_info_row, text=f"Regen: {self.player_hp_regen_interval - (self.seconds_elapsed % self.player_hp_regen_interval)}", bg="white", font=button_font)
        self.right_menu["player_regen_label"].grid(row=1, column=1, padx=2)

        self.right_menu["player_shoot_rate_label"] = tk.Label(
            player_info_row, text=f"Sht_rate: {self.player.shoot_rate_per_second}", bg="white", font=button_font)
        self.right_menu["player_shoot_rate_label"].grid(
            row=1, column=2, padx=2)

        self.right_menu["player_damage_label"] = tk.Label(
            player_info_row, text=f"Dmg: {self.player.bullet_damage}", bg="white", font=button_font)
        self.right_menu["player_damage_label"].grid(row=1, column=3, padx=2)

        self.right_menu["player_speed_label"] = tk.Label(
            player_info_row, text=f"Spd: {self.player.speed_per_second}", bg="white", font=button_font)
        self.right_menu["player_speed_label"].grid(row=1, column=4, padx=2)

        player_info_row.grid(row=3, column=0, columnspan=2, pady=10)

        # Define Enemy info labels
        # Need: hp, atk_speed, damage, respawn_interval, max_on_screen

        enemy_info_row = tk.Frame(self.right_menu["right_menu"], bg="white")

        self.right_menu["enemy_label"] = tk.Label(
            enemy_info_row, text=f"Enemy stats (upgr_in: {self.enemy_upgrade_interval_seconds - (self.seconds_elapsed % self.enemy_upgrade_interval_seconds)})", bg="white", font=score_font)
        self.right_menu["enemy_label"].grid(
            row=0, column=0, columnspan=5, pady=5, sticky="NEWS")

        self.right_menu["enemy_health_label"] = tk.Label(
            enemy_info_row, text=f"Hp: {self.enemy_ship_health}", bg="white", font=button_font)
        self.right_menu["enemy_health_label"].grid(row=1, column=0, padx=2)

        self.right_menu["enemy_shoot_rate_label"] = tk.Label(
            enemy_info_row, text=f"Sht_rate: {self.enemy_ship_shoot_rate_per_second_min}-{self.enemy_ship_shoot_rate_per_second_max}", bg="white", font=button_font)
        self.right_menu["enemy_shoot_rate_label"].grid(row=1, column=1, padx=2)

        self.right_menu["enemy_damage_label"] = tk.Label(
            enemy_info_row, text=f"Dmg: {self.enemy_ship_bullet_damage}", bg="white", font=button_font)
        self.right_menu["enemy_damage_label"].grid(row=1, column=2, padx=2)

        self.right_menu["enemy_respawn_label"] = tk.Label(
            enemy_info_row, text=f"Rsp_in: {self.enemy_ship_spawn_interval_seconds - self.seconds_elapsed % self.enemy_ship_spawn_interval_seconds}", bg="white", font=button_font)
        self.right_menu["enemy_respawn_label"].grid(row=1, column=3, padx=2)

        self.right_menu["enemy_max_on_screen_label"] = tk.Label(
            enemy_info_row, text=f"Max: {self.max_enemies_on_screen}", bg="white", font=button_font)
        self.right_menu["enemy_max_on_screen_label"].grid(
            row=1, column=4, padx=2)

        enemy_info_row.grid(row=4, column=0, columnspan=2, pady=10)

        # Define bomb info labels
        # Need delay, radius, damage, respawn_interval, max
        bomb_info_row = tk.Frame(self.right_menu["right_menu"], bg="white")

        self.right_menu["bomb_labell"] = tk.Label(
            bomb_info_row, text=f"Bomb stats (upgr_in: {self.bomb_upgrade_interval_seconds - self.seconds_elapsed % self.bomb_upgrade_interval_seconds})", bg="white", font=score_font)
        self.right_menu["bomb_labell"].grid(
            row=0, column=0, columnspan=5, pady=5)

        self.right_menu["bomb_blast_delay_label"] = tk.Label(
            bomb_info_row, text=f"Delay: {self.bomb_blast_delay}", bg="white", font=button_font)
        self.right_menu["bomb_blast_delay_label"].grid(row=1, column=0, padx=2)

        self.right_menu["bomb_blast_radius_label"] = tk.Label(
            bomb_info_row, text=f"Radius: {self.bomb_blast_radius}", bg="white", font=button_font)
        self.right_menu["bomb_blast_radius_label"].grid(
            row=1, column=1, padx=2)

        self.right_menu["bomb_blast_damage_labell"] = tk.Label(
            bomb_info_row, text=f"Dmg: {self.bomb_blast_damage}", bg="white", font=button_font)
        self.right_menu["bomb_blast_damage_labell"].grid(
            row=1, column=2, padx=2)

        self.right_menu["bomb_respawn_label"] = tk.Label(
            bomb_info_row, text=f"Rsp_in: {self.bomb_spawn_interval - self.seconds_elapsed % self.bomb_spawn_interval}", bg="white", font=button_font)
        self.right_menu["bomb_respawn_label"].grid(row=1, column=3, padx=2)

        self.right_menu["bomb_max_on_screen_label"] = tk.Label(
            bomb_info_row, text=f"Max: {self.max_bombs_on_screen}", bg="white", font=button_font)
        self.right_menu["bomb_max_on_screen_label"].grid(
            row=1, column=4, padx=2)

        bomb_info_row.grid(row=5, column=0, columnspan=2, pady=10)

        self.right_menu["right_menu"].grid(
            row=0, column=1, sticky="NEWS", padx=10, pady=10)

        # Bind save game button
        self.right_menu["save_button"].bind("<Button-1>", self.save_game)
        self.right_menu["back_button"].bind(
            "<Button-1>", lambda a: self.change_app_state("menu"))

    def update_right_menu(self):
        """Updates labels in the right menu"""
        # Update score lables
        self.right_menu["score_label"]["text"] = f"Score: {self.score}"
        self.right_menu["score_per_second_label"][
            "text"] = f"Score/sec: {self.score_per_second}"
        self.right_menu["score_per_enemy_label"][
            "text"] = f"Score/enemy: {self.score_per_enemy}"
        # Update player labels
        self.right_menu["player_label"][
            "text"] = f"Player stats (upgr_in: {self.player_upgrade_interval_seconds - (self.seconds_elapsed % self.player_upgrade_interval_seconds)})"
        self.right_menu["self.player_health_label"][
            "text"] = f"Hp: {self.player.health}/{self.player.max_health}"
        self.right_menu["player_regen_label"][
            "text"] = f"Regen: {self.player_hp_regen_interval - (self.seconds_elapsed % self.player_hp_regen_interval)}"
        self.right_menu["player_shoot_rate_label"][
            "text"] = f"Sht_rate: {self.player.shoot_rate_per_second}"
        self.right_menu["player_damage_label"]["text"] = f"Dmg: {self.player.bullet_damage}"
        self.right_menu["player_speed_label"]["text"] = f"Spd: {self.player.speed_per_second}"
        # Update enemy labels
        self.right_menu["enemy_label"][
            "text"] = f"Enemy stats (upgr_in: {self.enemy_upgrade_interval_seconds - (self.seconds_elapsed % self.enemy_upgrade_interval_seconds)})"
        self.right_menu["enemy_health_label"]["text"] = f"Hp: {self.enemy_ship_health}"
        self.right_menu["enemy_shoot_rate_label"][
            "text"] = f"Sht_rate: {self.enemy_ship_shoot_rate_per_second_min}-{self.enemy_ship_shoot_rate_per_second_max}"
        self.right_menu["enemy_damage_label"]["text"] = f"Dmg: {self.enemy_ship_bullet_damage}"
        self.right_menu["enemy_respawn_label"][
            "text"] = f"Rsp_in: {self.enemy_ship_spawn_interval_seconds - self.seconds_elapsed % self.enemy_ship_spawn_interval_seconds}"
        self.right_menu["enemy_max_on_screen_label"][
            "text"] = f"Max: {self.max_enemies_on_screen}"
        # Update bomb labels
        self.right_menu["bomb_labell"][
            "text"] = f"Bomb stats (upgr_in: {self.bomb_upgrade_interval_seconds - self.seconds_elapsed % self.bomb_upgrade_interval_seconds})"
        self.right_menu["bomb_blast_delay_label"]["text"] = f"Delay: {self.bomb_blast_delay}"
        self.right_menu["bomb_blast_radius_label"][
            "text"] = f"Radius: {self.bomb_blast_radius}"
        self.right_menu["bomb_blast_damage_labell"][
            "text"] = f"Dmg: {self.bomb_blast_damage}"
        self.right_menu["bomb_respawn_label"][
            "text"] = f"Rsp_in: {self.bomb_spawn_interval - self.seconds_elapsed % self.bomb_spawn_interval}"
        self.right_menu["bomb_max_on_screen_label"][
            "text"] = f"Max: {self.max_bombs_on_screen}"

    def increase_score(self, amount: float):
        """Increases score by amount in parameter"""
        self.score += amount
        # Round the score to 1 d.p
        self.score = round(self.score, 1)

    def deal_damage_to_player(self, damage):
        """Deals damage to player and handles game over checks"""
        # Too tired to put gameover checks after any damage instance to player, so created dedicated function
        # This prevents health bar from becoming wacky, since health can't get less than 0
        if self.player.health - damage < 0:
            self.player.health = 0
        else:
            self.player.health -= damage

        # If health is at 0, call gameover
        if self.player.health == 0:
            self.game_state = 1

    def instantiate_player(self):
        """Create an instance of ship class named player"""
        self.player = Ship(
            canvas,
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
            self.player_bullets_per_volley,
            self.player_health
        )

    def define_player_initial_variables(self):
        """Defines player variables"""
        self.player_width = 45
        self.player_height = 50
        self.player_speed_per_second = 335
        self.player_bullet_width = 10
        self.player_bullet_height = 20
        self.player_bullet_speed_per_second = 500
        self.player_bullet_damage = 1
        self.player_color = "#41bfff"
        self.player_shoot_rate_per_second = 1.6
        self.player_health = 5
        self.player_bullets_per_volley = 1
        self.no_enemy_spawn_around_player_radius = 300
        self.player_hp_regen_interval = 30

    def define_enemy_initial_variables(self):
        """defines enemy variables"""
        self.max_enemies_on_screen = 2
        self.enemy_ship_spawn_interval_seconds = 8
        self.absolute_max_enemies_on_screen = 8
        self.absolute_min_ship_spawn_interval_seconds = 2
        self.enemy_ship_health = 3
        self.enemy_ship_bullet_speed_per_second = 150
        self.enemy_ship_bullet_damage = 1
        self.enemy_ship_color = "#ff0fcb"
        self.enemy_ship_width = 50
        self.enemy_ship_height = 55
        self.enemy_ship_bullet_width = 8
        self.enemy_ship_bullet_height = 18
        self.enemy_ship_speed_per_second = 100
        self.enemy_ship_shoot_rate_per_second_min = 0.5
        self.enemy_ship_shoot_rate_per_second_max = 0.7
        self.enemy_ship_bullets_per_volley = 1

    def define_bomb_initial_variables(self):
        """Defines all bomb variables"""
        self.show_blast_seconds = 0.3
        self.bomb_blast_delay = 4
        self.bomb_blast_radius = 80
        self.bomb_blast_radius_color = "red"
        self.bomb_blast_damage = 2
        self.bomb_spawn_interval = 8
        self.bomb_spawn_offset_from_player = 12
        self.max_bombs_on_screen = 2
        self.max_bombs_gain = 1
        self.absolute_max_bombs_on_screen = 8

    def define_player_scaling_variables(self):
        """Defines all player scaling variables"""
        self.player_upgrade_interval_seconds = 15
        self.player_upgrade_choices = 4
        self.player_health_gain = 3
        self.player_damage_gain = 1
        self.player_bullets_per_volley_gain = 1
        self.player_shoot_rate_gain = 0.5
        self.player_speed_gain = 35
        self.player_hp_regen_interval_reduction = 7
        self.player_hp_regen_interval_absolute_min = 1
        self.player_bullet_size_gain = 3

    def define_enemy_scaling_variables(self):
        """Defines enemy scaling variables, like shoot rate gain"""
        self.enemy_upgrade_interval_seconds = 12
        self.enemy_upgrades_per_interval = 2
        self.enemy_health_gain = 1
        self.enemy_damage_gain = 1
        self.enemy_bullets_per_volley_gain = 1
        self.enemy_absolute_max_bullets_per_volley = 3
        self.enemy_shoot_rate_gain = 0.25
        self.enemy_absolute_max_shoot_rate = 2.5
        self.enemy_bullet_width_gain = 1.5
        self.enemy_bullet_speed_per_second_gain = 15
        self.max_enemies_on_screen_gain = 1
        self.enemy_ship_spawn_interval_decrease = 2

    def define_bomb_scaling_variables(self):
        """Defines bomb scaling variables like damage gain"""
        self.bomb_upgrade_interval_seconds = 12
        self.bomb_upgrades_per_interval = 2
        self.bomb_blast_delay_decrease = 0.3
        self.bomb_absolute_min_blast_delay = 2
        self.bomb_blast_radius_gain = 20
        self.bomb_absolute_max_blast_radius = 700
        self.bomb_blast_damage_gain = 1
        self.bomb_absolute_max_blast_damage = 4
        self.bomb_spawn_interval_decrease = 1
        self.bomb_absolute_min_spawn_interval = 2

    def define_score_variables(self):
        """Defines initial variables for score processing"""
        self.score = 0
        self.score_per_enemy = 20
        self.score_per_enemy_base = self.score_per_enemy
        self.score_per_second = 1
        self.score_per_second_gain = 0.5
        self.score_enemy_multiplier = 1

    def process_cheats(self):
        """Activates cheats in the config.cheatcodes"""
        # Cheatcodes:
        # infi - Infinite player health
        # aezkami - Infinite player damage
        # quortli - player scaling increased by factor of 2
        # junji - bombs deal no damage
        # scrcheat - score gain is multiplied by 2
        # uionjs - enemies scale slower by factor of 2
        cheat_list = self.config["game"]["cheat_list"]
        for cheat in cheat_list:
            # Infinite player health
            if cheat == "infi":
                self.player.health = float("inf")
                self.player.max_health = float("inf")
            # Infinite damage
            elif cheat == "aezkami":
                self.player.bullet_damage = float("inf")
            # Player scaling two times faster
            elif cheat == "quortli":
                self.player_health_gain *= 2
                self.player_damage_gain *= 2
                self.player_bullets_per_volley_gain *= 2
                self.player_shoot_rate_gain *= 2
                self.player_speed_gain *= 2
                self.player_hp_regen_interval_reduction *= 2
                self.player_bullet_size_gain *= 2
            # Bombs do no damage
            elif cheat == "junji":
                self.bomb_blast_damage = 0
                self.bomb_blast_damage_gain = 0
            # Double score gain
            elif cheat == "scrcheat":
                self.score_per_second_gain *= 2
                self.score_enemy_multiplier *= 2
            # Enemies scale two times slower
            elif cheat == "uionjs":
                self.enemy_upgrades_per_interval = max(
                    1, self.enemy_upgrades_per_interval // 2)
                self.enemy_health_gain = max(1, self.enemy_health_gain // 2)
                self.enemy_damage_gain = max(1, self.enemy_damage_gain // 2)
                self.enemy_bullets_per_volley_gain = max(
                    1, self.enemy_bullets_per_volley_gain // 2)
                self.enemy_shoot_rate_gain /= 2
                self.enemy_bullet_width_gain /= 2
                self.enemy_bullet_speed_per_second_gain /= 2
                self.max_enemies_on_screen_gain = max(
                    1, self.max_enemies_on_screen_gain // 2)
                self.enemy_ship_spawn_interval_decrease = max(
                    1, self.enemy_ship_spawn_interval_decrease // 2)

    def is_point_usable(self, x: float, y: float):
        """Check that point generated is valid, i.e  not occupied by anything"""
        # Check that point is not within no spawn radius around player
        distance_to_player = utils.calculate_length(
            x, y, self.player.focal_point[0], self.player.focal_point[1])
        if distance_to_player < self.no_enemy_spawn_around_player_radius + max(self.player.ship_width, self.player.ship_height):
            return False

        # Check that point is not occupied by any other enemy ship
        for enemy_ship in self.enemy_ships_list:
            distance_to_enemy_ship = utils.calculate_length(
                x, y, enemy_ship.focal_point[0], enemy_ship.focal_point[1])
            if distance_to_enemy_ship < max(enemy_ship.ship_width, enemy_ship.ship_height) + self.min_distance_between_bounds:
                return False

        return True

    def is_player_in_bomb_radius(self, bomb: Bomb):
        """Determines whether any player's hitbox points are within the given bombs blast radius"""
        for hitbox in self.player.hitboxes:
            for i in range(0, len(hitbox) - 2, 2):
                x = hitbox[i]
                y = hitbox[i + 1]
                # Calc dist to bomb centre
                dist_to_bomb_centre = utils.calculate_length(
                    x, y, bomb.focal_point[0], bomb.focal_point[1])
                # Compare to blast radius, if less than, then hitbox is in blast radius
                if dist_to_bomb_centre <= bomb.blast_radius:
                    return True
        # If no hitbox points are within blast radius, then player is not in blast radius
        return False

    def generate_random_point(self):
        """Generate a random point not occupied by anything"""
        min_x = math.ceil(self.enemy_ship_width / 2 +
                          self.min_distance_between_bounds)
        max_x = math.ceil(self.canvas_dimensions.get(
            "x") - self.enemy_ship_width / 2 - self.min_distance_between_bounds)
        min_y = math.ceil(self.enemy_ship_height / 2 +
                          self.min_distance_between_bounds)
        max_y = math.ceil(self.canvas_dimensions.get(
            "y") - self.enemy_ship_height / 2 - self.min_distance_between_bounds)
        point_x = random.randint(min_x, max_x)
        point_y = random.randint(min_y, max_y)
        # While point is occupied by something, keep generating new random points
        while self.is_point_usable(point_x, point_y) == False:
            point_x = random.randint(min_x, max_x)
            point_y = random.randint(min_y, max_y)

        return [point_x, point_y]

    def spawn_enemy_ship(self):
        """Spawn a new enemy ship in a valid random position"""
        if len(self.enemy_ships_list) < self.max_enemies_on_screen:

            spawn_point = self.generate_random_point()
            # Calc angle to player, to avoid bug with user not moving mouse and ships are forever stuck shooting away from player
            angle_to_player = utils.resolve_angle(
                spawn_point[0], spawn_point[1], self.player.focal_point[0], self.player.focal_point[1])
            enemy_ship = Ship(
                canvas,
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
                random.uniform(self.enemy_ship_shoot_rate_per_second_min,
                               self.enemy_ship_shoot_rate_per_second_max),
                self.enemy_ship_bullets_per_volley,
                self.enemy_ship_health
            )
            self.enemy_ships_list.append(enemy_ship)

    def spawn_enemy_bomb(self):
        """Spawns a new bomb near player"""
        def difference():
            temp = random.randint(0, 1)
            if temp == 0:
                return -self.bomb_spawn_offset_from_player
            else:
                return self.bomb_spawn_offset_from_player

        if len(self.enemy_bomb_list) < self.max_bombs_on_screen:
            spawn_point = [self.player.focal_point[0] +
                           difference(), self.player.focal_point[1] + difference()]
            bomb = Bomb(
                spawn_point.copy(),
                self.bomb_blast_delay,
                self.bomb_blast_radius,
                self.bomb_blast_radius_color,
                self.bomb_blast_damage,
                self.fps,
                self.show_blast_seconds
            )
            self.enemy_bomb_list.append(bomb)

    def regenerate_player_hp(self):
        """Only regen health if not at full health"""
        if self.player.health < self.player.max_health:
            self.player.health += 1

    def handle_timed_events(self):
        """Check and run all timed events if interval is met"""

        if self.seconds_elapsed % self.bomb_spawn_interval == 0:
            self.spawn_enemy_bomb()
        if self.seconds_elapsed % self.enemy_ship_spawn_interval_seconds == 0:
            self.spawn_enemy_ship()
        if self.seconds_elapsed % self.player_upgrade_interval_seconds == 0:
            self.generate_upgrades()
        if self.seconds_elapsed % self.player_hp_regen_interval == 0:
            self.regenerate_player_hp()
        if self.seconds_elapsed % self.enemy_upgrade_interval_seconds == 0:
            self.upgrade_enemies()
        if self.seconds_elapsed % self.bomb_upgrade_interval_seconds == 0:
            self.upgrade_bombs()
        # Increment scope per second
        self.score_per_second += self.score_per_second_gain
        # Increase score
        self.increase_score(self.score_per_second)
        # Increase reward for enemies destroyed as more time pass, round to 1 d.p
        self.score_per_enemy = round(
            self.score_per_enemy_base + self.seconds_elapsed * self.score_enemy_multiplier, 1)
        # Update side menu every second
        self.update_right_menu()

    def handle_enemy_ships(self):
        """Iterate through all enemy ships all handle events with them"""
        for i in range(len(self.enemy_ships_list)):
            enemy_ship = self.enemy_ships_list[i]
            # Attempt to shoot valley every frame, whether is allowed to shoot will be handled in the inner method
            enemy_ship.shoot_volley(self.frame_counter, self.seconds_elapsed)
            enemy_ship.on_frame()
            self.handle_enemy_bullets_collisions(i)

    def handle_bombs(self):
        """Function to do everything on bombs"""
        delete_indexes = []
        for i in range(len(self.enemy_bomb_list)):
            bomb = self.enemy_bomb_list[i]
            bomb.on_frame()
            if bomb.blast_counter == bomb.blast_delay:
                if self.is_player_in_bomb_radius(bomb):
                    self.deal_damage_to_player(bomb.blast_damage)
            is_redundant = bomb.is_redundant()
            if is_redundant:
                delete_indexes.append(i)

        # Dispose redundant bombs (bombs that are already exploded fully)
        self.delete_redundant_bombs(delete_indexes)

    def on_frame(self):
        """Function for everything that happens every frame"""
        # Deletes everything from the canvas
        canvas.delete("all")
        # ORDER IS IMPORTANT
        # first handle bombs, since player moves outside of frames, no problems with frame desync. Also to allow player to be over the bomb texture
        self.handle_bombs()
        # second handle player, it has to be above enemy ships, since it also calls function to handle all bullets
        self.player.on_frame()
        # third handle enemy ships
        self.handle_enemy_ships()
        self.handle_player_bullets_collisions()
        self.handle_remnant_bullets()
        self.handle_player_enemy_ship_collision()
        # Draw everything separately
        self.draw_everything()
        if self.game_state == 1:
            self.gameover()
        # Increase ingame time variables
        self.frame_counter += 1
        if(self.frame_counter > self.fps):
            self.frame_counter = 1
            self.seconds_elapsed += 1
            self.handle_timed_events()

        # Fix desync issues, where depending on timing, pause would be ignored

        if self.next_frame_after_id != 0:
            self.next_frame_after_id = canvas.after(
                self.ms_interval, self.on_frame)

    def point_enemy_ships_to_player(self):
        """Points all enemy ships towards the player"""

        # Points all enemy ship towards player
        for enemy_ship in self.enemy_ships_list:
            # Calculate angle from enemy ship to the player ship
            angle_to_player = utils.resolve_angle(
                enemy_ship.focal_point[0], enemy_ship.focal_point[1], self.player.focal_point[0], self.player.focal_point[1])
            enemy_ship.transform(angle_to_player)

    def on_cursor_move(self, event):
        """Adjusts angle variable depending on where user points the cursor"""
        # Fix bug where ships will be pointing when paused
        if self.next_frame_after_id != 0:
            x = event.x
            y = event.y
            self.angle = utils.resolve_angle(
                self.player.focal_point[0], self.player.focal_point[1], x, y)
            self.player.transform(self.angle)
            self.point_enemy_ships_to_player()

    def on_key_press(self, event):
        """Handles key presses"""
        key = event.char
        # Movement key events trigger, trigger if game is not paused
        if self.controls.get("move") == key and self.next_frame_after_id != 0:
            self.player.move()
            # Fix for a bug where ships won't point at player if he just moves without moving mouse around
            self.point_enemy_ships_to_player()
        # Pause/unpause key event trigger, only process if game not ended
        elif self.controls.get("pause/unpause") == key and self.game_state == 0:
            # If game is paused, resume
            if self.next_frame_after_id == 0:
                self.resume()
            # If not paused, pause
            else:
                self.pause()

        elif self.controls.get("boss_key") == key:
            # If not in the boss key, pause and display spreadsheet
            if self.spreadsheet_overlay == None:
                self.display_spreadsheet_image()
                self.pause()
            # If in boss key, return to normal game operation
            else:
                self.delete_spreadsheet_image()
                # self.resume()

        # If key is a number and the game is in upgrading state, call upgrade function with key pressed
        elif key in [str(number) for number in range(1, self.player_upgrade_choices + 1)] and self.game_state == 2:
            # Need to take 1 away, because upgrade choices array is 0 based
            self.upgrade_player(int(key) - 1)

    def on_click(self, event):
        """Only process click if the game is not paused"""
        if self.next_frame_after_id != 0:
            self.player.shoot_volley(self.frame_counter, self.seconds_elapsed)

    def resume(self):
        """Assign next after id and assign after"""
        self.next_frame_after_id = canvas.after(
            self.ms_interval, self.on_frame)

    def pause(self):
        """Pause the game"""
        if self.next_frame_after_id != 0:
            # Cancel canvas after and assign after id = 0
            canvas.after_cancel(self.next_frame_after_id)
            self.next_frame_after_id = 0
        # If paused while game not ended or not upgrading, show paused text
        if self.game_state == 0:
            canvas.create_text(
                self.canvas_centre_x, self.canvas_centre_y, font="Arial 35 bold", text="Paused")

    def draw_everything(self):
        """Draws everything"""
        # draw enemy ships
        for enemy_ship in self.enemy_ships_list:
            enemy_ship.draw()
        # draw bomb
        for bomb in self.enemy_bomb_list:
            bomb.draw()
        # Draw player on top of everything else
        # draw player
        self.player.draw()

    def gameover(self):
        """Function that handles what happens after players health is 0"""

        self.pause()
        # This allows the frames to settle, so no missing staff
        # canvas.delete("all")
        # self.draw_everything()
        self.update_right_menu()
        canvas.create_text(self.canvas_centre_x, self.canvas_centre_y,
                           font="Arial 35 bold", text="Game Over!")
        self.record_in_leaderboard()
        utils.display_leaderboard(self.leaderboard_file_path)

    def handle_enemy_bullets_collisions(self, enemy_ship_index: int):
        """Checks collsion of enemy bullets with the player ship and processes if collision detected"""
        enemy_ship = self.enemy_ships_list[enemy_ship_index]
        delete_indexes = []
        # Iterate through enemy bullets
        for i in range(len(enemy_ship.bullet_list)):
            bullet = enemy_ship.bullet_list[i]
            # If bullet collides with player do:
            does_collide_with_player = utils.do_objects_collide(
                bullet, self.player)
            if does_collide_with_player:
                self.deal_damage_to_player(bullet.damage)

                delete_indexes.append([enemy_ship_index, i])

        self.delete_redundant_enemy_bullets(delete_indexes)

    def delete_redundant_enemies(self, delete_indexes: list):
        """Delete redundant enemy ships from ships list, and add bullets to remnant list, so that they don't dissapear"""
        for i in range(len(delete_indexes)):
            delete_index = delete_indexes[i]
            # Add bullets from the destroyed ship to the remnant bullets
            self.add_bullets_to_remnant_list(
                self.enemy_ships_list[delete_index])
            # Add points to score for destroying the ship
            self.increase_score(self.score_per_enemy)
            self.enemy_ships_list.pop(delete_index)
            # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
            for j in range(len(delete_indexes)):
                if delete_indexes[j] > delete_index:
                    delete_indexes[j] -= 1

    def delete_redundant_player_bullets(self, delete_indexes: list):
        """Delete redundant player bullets from bullet list"""
        for i in range(len(delete_indexes)):
            delete_index = delete_indexes[i]
            self.player.bullet_list.pop(delete_index)
            # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
            for j in range(len(delete_indexes)):
                if delete_indexes[j] > delete_index:
                    delete_indexes[j] -= 1

    def delete_redundant_enemy_bullets(self, delete_indexes: list):
        """Delete redundant enemy bullets from bullet lists"""
        for i in range(len(delete_indexes)):
            delete_index = delete_indexes[i]
            # Get enemy ship index from delete index elem and pop bullet at second arg
            self.enemy_ships_list[delete_index[0]
                                  ].bullet_list.pop(delete_index[1])
            # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
            for j in range(len(delete_indexes)):
                if delete_indexes[j][0] == delete_index[0] and delete_indexes[j][1] > delete_index[1]:
                    delete_indexes[j][1] -= 1

    def delete_redundant_remnant_bullets(self, delete_indexes: list):
        """Delete redundant player bullets from bullet list"""
        for i in range(len(delete_indexes)):
            delete_index = delete_indexes[i]
            self.remnant_bullets.pop(delete_index)
            # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
            for j in range(len(delete_indexes)):
                if delete_indexes[j] > delete_index:
                    delete_indexes[j] -= 1

    def delete_redundant_bombs(self, delete_indexes: list):
        """Delete redundant bombs from bombs list"""
        for i in range(len(delete_indexes)):
            delete_index = delete_indexes[i]
            self.enemy_bomb_list.pop(delete_index)
            # When something is deleted, indexes to the right shift to left, so need to adjust delete indexes bigget than deleted index
            for j in range(len(delete_indexes)):
                if delete_indexes[j] > delete_index:
                    delete_indexes[j] -= 1

    def handle_remnant_bullets(self):
        """Handle all events to do with remnant bullets (bullets from ships that were destroyed)"""
        delete_indexes_remnant = []
        delete_indexes_player_bullets = []
        for i in range(len(self.remnant_bullets)):
            bullet = self.remnant_bullets[i]
            bullet.move()
            bullet.draw()
            # Calculate if the bullet is fully out of bounds, if so mark for deletion
            bounds_info = utils.get_bounds_info(bullet.points)
            fully_out_of_bounds = utils.is_fully_out_of_bounds(
                bounds_info[0], bounds_info[1], bounds_info[2], bounds_info[3], self.canvas_dimensions.get("x"), self.canvas_dimensions.get("y"))
            if fully_out_of_bounds:
                delete_indexes_remnant.append(i)

            # handle collision with player
            do_collide = utils.do_objects_collide(bullet, self.player)
            if do_collide:
                self.deal_damage_to_player(bullet.damage)
                delete_indexes_remnant.append(i)

            # handle collision with player bullets
            for j in range(len(self.player.bullet_list)):
                player_bullet = self.player.bullet_list[j]
                do_collide = utils.do_objects_collide(player_bullet, bullet)
                if do_collide:
                    temp = player_bullet.damage
                    player_bullet.damage -= bullet.damage
                    bullet.damage -= temp
                    if player_bullet.damage <= 0 and j not in delete_indexes_player_bullets:
                        delete_indexes_player_bullets.append(j)
                    if bullet.damage <= 0 and i not in delete_indexes_remnant:
                        delete_indexes_remnant.append(i)

        # Delete everything marked for deletion
        self.delete_redundant_player_bullets(delete_indexes_player_bullets)
        self.delete_redundant_remnant_bullets(delete_indexes_remnant)

    def add_bullets_to_remnant_list(self, enemy_ship: Ship):
        """Function to add dead ships bullets to remnant list, to prevent bullets from dissapearing"""
        self.remnant_bullets += enemy_ship.bullet_list

    def handle_player_bullets_collisions(self):
        """Checks player bullets collision with enemy bullets or enemy ships. Processes if collission is detected"""
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
                        if enemy_bullet.damage <= 0 and [j, k] not in delete_indexes_enemy_bullets:
                            # Since we need to know from which ship the bullet came from, add j - index of the ship with k - index of bullet
                            delete_indexes_enemy_bullets.append([j, k])
                        if bullet.damage <= 0 and i not in delete_indexes_player_bullets:

                            delete_indexes_player_bullets.append(i)
                # If player bullet collides with enemy ship
                do_collide = utils.do_objects_collide(bullet, enemy_ship)
                if do_collide:
                    # Reduce enemy ship health with bullet damage
                    enemy_ship.health -= bullet.damage
                    # If enemy ships health is less than or equal to 0, mark it for deletion
                    # Fixed bug where a ship is struck by more than one bullet at the same time which resulted in multiple entries in delete ship
                    if enemy_ship.health <= 0 and j not in delete_indexes_ships:
                        delete_indexes_ships.append(j)
                    if i not in delete_indexes_player_bullets:
                        delete_indexes_player_bullets.append(i)
                    break

        # Delete redundant enemy bullets
        self.delete_redundant_enemy_bullets(delete_indexes_enemy_bullets)
        # Delete redundant player bullets
        self.delete_redundant_player_bullets(delete_indexes_player_bullets)

        # Delete destroyed ships
        self.delete_redundant_enemies(delete_indexes_ships)

    def handle_player_enemy_ship_collision(self):
        """Checks player ship and enemy ship collision and processes if collision is detected"""
        delete_indexes = []
        for i in range(len(self.enemy_ships_list)):
            enemy_ship = self.enemy_ships_list[i]
            do_collide = utils.do_objects_collide(self.player, enemy_ship)
            if do_collide:
                # Classic, when two variables depend on each other for change, need to use a third variable to store at least one var
                temp = enemy_ship.health
                enemy_ship.health -= self.player.health
                if i not in delete_indexes and enemy_ship.health <= 0:
                    delete_indexes.append(i)
                self.deal_damage_to_player(temp)

        self.delete_redundant_enemies(delete_indexes)

    def generate_upgrades(self):
        """Generates player upgrade choices"""
        # To prevent user from upausing
        self.game_state = 2
        self.pause()
        self.upgrade_indexes = []
        # Upgrade options:
        upgrade_texts = [
            f"Increase max health by {self.player_health_gain} units",
            f"Increase speed by {self.player_speed_gain} units",
            f"Increase damage per bullet by {self.player_damage_gain} units",
            f"Increase shoot rate by {self.player_shoot_rate_gain} seconds",
            f"Increase bullets per volley by {self.player_bullets_per_volley_gain} bullets",
            f"Decrease hp regen interval by {self.player_hp_regen_interval_reduction} seconds",
            f"Increase player's bullet size by {self.player_bullet_size_gain} units"
        ]
        # 0 - Increase  max health by {player_health_gain}
        # 1 - Increase speed by {player_speed_gain}
        # 2 - Increase damage per bullet by {player_damage_gain}
        # 3 - Increase shoot rate by {player_shoot_rate_gain}
        # 4 - Increase bullets per volley by {player_bullets_per_volley_gain}
        # 5 - Decrease hp regen interval by {player_hp_regen_interval_reduction} (can't be less than 1)
        # 6 - Increase player's bullet size by {player_bullet_size_gain}
        choice_max = len(upgrade_texts) - 1
        # Generate random upgrades indexes
        for i in range(self.player_upgrade_choices):
            choice_index = random.randint(0, choice_max)
            # Makes sure that upgrade choices are unique
            while choice_index in self.upgrade_indexes:
                choice_index = random.randint(0, choice_max)
            self.upgrade_indexes.append(choice_index)
        font_size = 23
        text_vertical_margin = font_size + 12
        y_pos = self.canvas_centre_y - 150
        # display choices on the screen
        canvas.create_text(self.canvas_centre_x, y_pos,
                           font=f"Arial {font_size} bold", text="Upgrade time! Press a key corresponding to chosen upgrade")
        # Draw all upgrade choices as text
        for i in range(len(self.upgrade_indexes)):
            y_pos += text_vertical_margin
            upgrade_index = self.upgrade_indexes[i]
            canvas.create_text(self.canvas_centre_x, y_pos,
                               font=f"Arial {font_size - 5} bold", text=f"{i + 1}: {upgrade_texts[upgrade_index]}")

    def upgrade_player(self, index: int):
        """Processes user inputed upgrade choice and applies it"""
        # Actually implements upgrades
        chosen_upgrade = self.upgrade_indexes[index]
        # 0 - Increase  max health by {player_health_gain}
        # 1 - Increase speed by {player_speed_gain}
        # 2 - Increase damage per bullet by {player_damage_gain}
        # 3 - Increase shoot rate by {player_shoot_rate_gain}
        # 4 - Increase bullets per volley by {player_bullets_per_volley_gain}
        # 5 - Decrease hp regen interval by {player_hp_regen_interval_reduction} (can't be less than 1)
        # 6 - Increase player's bullet size by {player_bullet_size_gain}
        if chosen_upgrade == 0:
            self.player.health += self.player_health_gain
            self.player.max_health += self.player_health_gain
        elif chosen_upgrade == 1:
            self.player.speed_per_second += self.player_speed_gain
            self.player.speed = self.player.speed_per_second / self.player.fps
        elif chosen_upgrade == 2:
            self.player.bullet_damage += self.player_damage_gain
        elif chosen_upgrade == 3:
            self.player.shoot_rate_per_second = round(
                self.player.shoot_rate_per_second + self.player_shoot_rate_gain, 1)
            self.player.shoot_rate = self.fps / self.player.shoot_rate_per_second
        elif chosen_upgrade == 4:
            self.player.bullets_per_volley += self.player_bullets_per_volley_gain
        elif chosen_upgrade == 5:
            # Prevent the hp regen interval from going into negatives!
            temp = self.player_hp_regen_interval - self.player_hp_regen_interval_reduction
            if temp <= self.player_hp_regen_interval_absolute_min:
                self.player_hp_regen_interval = self.player_hp_regen_interval_absolute_min
            else:
                self.player_hp_regen_interval = temp
        elif chosen_upgrade == 6:
            self.player.bullet_width += self.player_bullet_size_gain
            self.player.bullet_height += self.player_bullet_size_gain
            self.player.volley_bullets_offset = bullet_volley_offset + self.player.bullet_width
        print(f"{chosen_upgrade} implemented on player\n")
        # Resume the game after upgrade is implemented
        self.game_state = 0
        self.upgrade_indexes = []
        self.resume()

    def upgrade_enemies(self):
        """Implements random upgrades on enemy ships"""
        upgrade_indexes = []
        # 0 - Increase health by {enemy_health_gain}
        # 1 - Increase damage by {enemy_damage_gain}
        # 2 - Increase bullets per volley by {enemy_bullets_in}
        # 3 - Increase min and max shoot rates by {enemy_shoot_rate_gain}
        # 4 - Increase enemy bullets width by {enemy_bullet_width_gain}
        # 5 - Increase enemies max on screen by {max_enemies_on_screen_gain}
        # 6 - Decrease enemy ship spawn interval by {enemy_ship_spawn_interval_decrease}
        # 7 - Upgrade enemies bullet speed by {bullet speed gain}
        choice_max = 7
        # Generate {upgrades_per_interval} random upgrades
        for i in range(self.enemy_upgrades_per_interval):
            upgrade_choice = random.randint(0, choice_max)
            while upgrade_choice in upgrade_indexes:
                upgrade_choice = random.randint(0, choice_max)
            upgrade_indexes.append(upgrade_choice)

        # Iterate through upgrades choices generated and implement them
        for i in range(len(upgrade_indexes)):
            chosen_upgrade = upgrade_indexes[i]
            if chosen_upgrade == 0:
                self.enemy_ship_health += self.enemy_health_gain
            elif chosen_upgrade == 1:
                self.enemy_ship_bullet_damage += self.enemy_damage_gain
            elif chosen_upgrade == 2:
                # Prevent bullets per volley from going too high
                temp = self.enemy_ship_bullets_per_volley + self.enemy_bullets_per_volley_gain
                if temp >= self.enemy_absolute_max_bullets_per_volley:
                    self.enemy_ship_bullets_per_volley = self.enemy_absolute_max_bullets_per_volley
                else:
                    self.enemy_ship_bullets_per_volley = temp
            elif chosen_upgrade == 3:
                temp = self.enemy_ship_shoot_rate_per_second_max + self.enemy_shoot_rate_gain
                # Prevent shoot rate from going too high
                if temp >= self.enemy_absolute_max_shoot_rate:
                    self.enemy_ship_shoot_rate_per_second_min = self.enemy_absolute_max_shoot_rate - 0.2
                    self.enemy_ship_shoot_rate_per_second_max = self.enemy_absolute_max_shoot_rate
                else:
                    self.enemy_ship_shoot_rate_per_second_min += self.enemy_shoot_rate_gain
                    self.enemy_ship_shoot_rate_per_second_max += self.enemy_shoot_rate_gain
                # Round to prevent floating point innacurracy
                self.enemy_ship_shoot_rate_per_second_min = round(
                    self.enemy_ship_shoot_rate_per_second_min, 1)
                self.enemy_ship_shoot_rate_per_second_max = round(
                    self.enemy_ship_shoot_rate_per_second_max, 1)
            elif chosen_upgrade == 4:
                self.enemy_ship_bullet_width += self.enemy_bullet_width_gain
                self.enemy_ship_bullet_height += self.enemy_bullet_width_gain
            elif chosen_upgrade == 5:
                # Prevents max enemies on screen from going over the absolute set limit
                temp = self.max_enemies_on_screen + self.max_enemies_on_screen_gain
                if temp >= self.absolute_max_enemies_on_screen:
                    self.max_enemies_on_screen = self.absolute_max_enemies_on_screen
                else:
                    self.max_enemies_on_screen = temp
            elif chosen_upgrade == 6:
                # Prevents enemy ship spawn interval from going over the absolute set limit
                temp = self.enemy_ship_spawn_interval_seconds - \
                    self.enemy_ship_spawn_interval_decrease
                if temp <= self.absolute_min_ship_spawn_interval_seconds:
                    self.enemy_ship_spawn_interval_seconds = self.absolute_min_ship_spawn_interval_seconds
                else:
                    self.enemy_ship_spawn_interval_seconds = temp
            elif chosen_upgrade == 7:
                self.enemy_ship_bullet_speed_per_second += self.enemy_bullet_speed_per_second_gain
            print(f"{chosen_upgrade} implemented on enemies\n")

    def upgrade_bombs(self):
        """Implements upgrades on bombs"""
        upgrade_indexes = []
        # 0 - Decrease blast delay by {blast_delay_decrease}
        # 1 - Increase blast radius by {blast_radius_gain}
        # 2 - Increase blast damage by {blast_damage_gain}
        # 3 - Decrease bomb spawn interval by {bomb_spawn_interval_decrease}
        # 4 - Increase max_bombs
        choice_max = 4
        # Generate random upgrade choices
        for i in range(self.bomb_upgrades_per_interval):
            upgrade_choice = random.randint(0, choice_max)
            while upgrade_choice in upgrade_indexes:
                upgrade_choice = random.randint(0, choice_max)
            upgrade_indexes.append(upgrade_choice)

        for i in range(len(upgrade_indexes)):
            chosen_upgrade = upgrade_indexes[i]
            if chosen_upgrade == 0:
                # Prevent blast delay from going over min limit
                temp = self.bomb_blast_delay - self.bomb_blast_delay_decrease
                if temp <= self.bomb_absolute_min_blast_delay:
                    temp = self.bomb_absolute_min_blast_delay
                else:
                    self.bomb_blast_delay = temp
                # Prevent floating point errors
                self.bomb_blast_delay = round(self.bomb_blast_delay, 1)
            elif chosen_upgrade == 1:
                # Prevent blast radius from going too big
                temp = self.bomb_blast_radius + self.bomb_blast_radius_gain
                if temp >= self.bomb_absolute_max_blast_radius:
                    self.bomb_blast_radius = self.bomb_absolute_max_blast_radius
                else:
                    self.bomb_blast_radius = temp
            elif chosen_upgrade == 2:
                # Prevenet blast damage from going over the limit
                temp = self.bomb_blast_damage + self.bomb_blast_damage_gain
                if temp >= self.bomb_absolute_max_blast_damage:
                    self.bomb_blast_damage = self.bomb_absolute_max_blast_damage
                else:
                    self.bomb_blast_damage = temp
            elif chosen_upgrade == 3:
                temp = self.bomb_spawn_interval - self.bomb_spawn_interval_decrease
                if temp <= self.bomb_absolute_min_spawn_interval:
                    self.bomb_spawn_interval = self.bomb_absolute_min_spawn_interval
                else:
                    self.bomb_spawn_interval = temp
            elif chosen_upgrade == 4:
                temp = self.max_bombs_on_screen + self.max_bombs_gain
                if temp >= self.absolute_max_bombs_on_screen:
                    self.max_bombs_on_screen = self.absolute_max_bombs_on_screen
                else:
                    self.max_bombs_on_screen = temp

            print(f"{chosen_upgrade} was implemented on bombs\n")

    def display_spreadsheet_image(self):
        """Function to display spreadsheet image on top of everything"""
        # Needs to be self. so that can be removed in the remove function
        self.spreadsheet = tk.PhotoImage(file="images/spreadsheet.PNG")
        self.spreadsheet_overlay = tk.Label(image=self.spreadsheet)
        # Place over the existing content
        self.spreadsheet_overlay.grid(
            row=0, column=0, columnspan=2, sticky="NSEW")

    def delete_spreadsheet_image(self):
        """Deletes spreadsheet image"""
        self.spreadsheet_overlay.destroy()
        self.spreadsheet_overlay = None

    def save_game(self, event):
        """Saves the current state of the game via pickle library into a file with filename given by user"""
        # Only allowed to save if game is ongoing
        if self.game_state == 0:

            self.pause()
            canvas.create_text(
                self.canvas_centre_x, self.canvas_centre_y, font="Arial 35 bold", text="Paused")
            # Need to delete all attributes that are tkinter elements
            # Save all bomb images and then delete them
            bomb_image_list = []
            for bomb in self.enemy_bomb_list:
                bomb_image_list.append(bomb.bomb_image)
                bomb.bomb_image = None
            # Delete right menu, because it uses tkinter elements
            self.right_menu = None
            self.spreadsheet = None
            # this try is for when the user clicks cancel, which is impossible to prevent
            try:
                # Ask the user for filepath of the save
                save_file_path = filedialog.asksaveasfilename(
                    initialdir="./saves/", initialfile="this_save.txt")
                file = open(save_file_path, 'wb')
                # Use pickle to save the Game class
                pickle.dump(self, file)
                file.close()
                # Restore bomb images
                for i in range(len(bomb_image_list)):
                    self.enemy_bomb_list[i].bomb_image = bomb_image_list[i]
                # Restore right menu
                self.create_right_menu()
            except:
                pass

    def record_in_leaderboard(self):
        """Record the game in the leaderboard"""
        leaderboard_data = utils.get_leaderboard_data(
            self.leaderboard_file_path)
        # Check if the current name is already in leaderboard
        present = False
        index = -1
        for i, d in enumerate(leaderboard_data):
            if d[0] == self.identity:
                present = True
                index = i
        # If not in leaderboard, append it
        if not present:
            current_player_data = [self.identity, self.score]
            leaderboard_data.append(current_player_data)
        # If in leaderboard, modify the score if the current score is higher than the recorded score
        else:
            leaderboard_data[index][1] = max(
                self.score, leaderboard_data[index][1])
        # Sort by score
        leaderboard_data.sort(key=lambda d: d[1], reverse=True)
        # Get the formatted string to write in the file
        to_write = ""
        for i, d in enumerate(leaderboard_data):
            to_write += f"{i + 1}) {d[0]}: {d[1]}\n"
        file = open(self.leaderboard_file_path, 'w+')
        file.write(to_write)
        file.close()


class CheatcodesMenu:
    def __init__(self, change_app_state, config, process_cheat_code):
        self.change_app_state = change_app_state
        # flush current cheats
        config["game"]["cheat_list"] = []
        self.config = config
        self.process_cheat_code = process_cheat_code
        self.menu = {}
        self.applied_cheats = []
        self.init_menu()

    def try_cheat_code(self, event):
        """Tries the cheat code entered into cheat field"""
        cheat_code = self.menu["Cheat_entry"].get()
        # Call the Application method for processing cheatcodes
        res = self.process_cheat_code(cheat_code)
        # If cheat code is valid and not applied already
        if res != "" and res != "same":
            self.menu["Cheat_alert"]["text"] = f"Sucess! cheat code '{cheat_code}' is applied: {res}"
            self.applied_cheats.append(res)
            self.menu["Cheats_applied"][
                "text"] = f"Applied cheats: {', '.join(self.applied_cheats)}"
        # If valid cheat code and is applied already
        elif res != "" and res == "same":
            self.menu["Cheat_alert"]["text"] = f"Failure! cheat code '{cheat_code}' is already applied!"
        # Non valid cheat code
        else:
            self.menu["Cheat_alert"][
                "text"] = f"Failure! cheat code '{cheat_code}' is not a valid cheat code!"

    def init_menu(self):
        """Initialize the menu."""
        font = "Arial 22"
        font_smaller = "Arial 15"
        main_window.columnconfigure(0, weight=1)
        main_window.rowconfigure(0, weight=1)
        self.bg = tk.PhotoImage(file="images/menu_background.png")

        self.menu["Menu_frame"] = tk.Frame(main_window, bg="white")
        self.menu["Menu_frame"].columnconfigure(0, weight=1)
        self.menu["Menu_frame"].rowconfigure(0, weight=1)
        self.menu["Menu_frame"].rowconfigure(1, weight=1)
        self.menu["Menu_frame"].rowconfigure(2, weight=1)
        self.menu["Menu_frame"].rowconfigure(3, weight=1)
        self.menu["Menu_frame"].rowconfigure(4, weight=1)

        self.menu["Background"] = tk.Label(
            self.menu["Menu_frame"], image=self.bg)
        self.menu["Background"].place(x=0, y=0, relwidth=1, relheight=1)
        self.menu["Cheat_label"] = tk.Label(
            self.menu["Menu_frame"], font=font, text="Enter a cheat code:", bg="white")
        self.menu["Cheat_label"].grid(row=0, column=0, sticky="")
        fram = tk.Frame(self.menu["Menu_frame"], bg="white")
        self.menu["Cheat_entry"] = tk.Entry(
            fram, font=font, borderwidth=1, relief="solid")
        self.menu["Cheat_entry"].grid(row=0, column=0, sticky="NS")
        self.menu["Cheat_try"] = tk.Button(fram, font=font, text="Try")
        self.menu["Cheat_try"].grid(row=0, column=1, sticky="NS", padx=5)
        self.menu["Cheats_applied"] = tk.Label(
            self.menu["Menu_frame"], font=font_smaller, text="Cheats applied: ", bg="white")
        self.menu["Cheats_applied"].grid(row=1, column=0, sticky="")
        fram.grid(row=2, column=0, sticky="")
        self.menu["Cheat_alert"] = tk.Label(
            self.menu["Menu_frame"], font=font, text="", bg="white")
        self.menu["Cheat_alert"].grid(row=3, column=0, sticky="")
        self.menu["New_game"] = tk.Button(
            self.menu["Menu_frame"], font=font, text="New game", height=2)
        self.menu["New_game"].grid(row=4, column=0, sticky="")
        self.menu["Menu_frame"].grid(row=0, column=0, sticky="NSEW")

        self.menu["Cheat_try"].bind("<Button-1>", self.try_cheat_code)
        self.menu["New_game"].bind(
            "<Button-1>", lambda a: self.change_app_state("game"))
        # Needed to display the background
        main_window.mainloop()


class Menu:
    """Class for the menu, includes load, cheat code enter and key remapping"""

    def __init__(self, main_window_dimensions: dict, change_app_state, config):
        self.change_app_state = change_app_state
        self.config = config
        self.main_window_dimensions = main_window_dimensions
        self.menu = {}
        self.init_menu()

    def load_game(self, event):
        """Modifies the config by reference and changes state to game"""
        save_file_path = filedialog.askopenfilename(initialdir="./saves/")
        # Checks if the file path is not empty and that the save file exists
        if(save_file_path != "" and pathlib.Path(save_file_path).exists()):
            self.config["save_file_path"] = save_file_path
            self.change_app_state("game")

    def init_menu(self):
        """Initialize the menu"""
        main_window.columnconfigure(0, weight=1)
        main_window.rowconfigure(0, weight=1)
        button_font = "Arial 22"
        self.bg = tk.PhotoImage(file="images/menu_background.png")
        # Create a new frame and place buttons in that frame
        self.menu["Menu_frame"] = tk.Frame(main_window, bg="white")
        # I HATE TKINTER
        self.menu["Menu_frame"].columnconfigure(0, weight=1)  # Like flex grow
        self.menu["Menu_frame"].rowconfigure(0, weight=1)
        self.menu["Menu_frame"].rowconfigure(1, weight=1)
        self.menu["Menu_frame"].rowconfigure(2, weight=1)
        self.menu["Menu_frame"].rowconfigure(3, weight=1)
        # main_windowself.menu["Menu_frame"].rowconfigure(4, weight =1)
        self.menu["Background"] = tk.Label(
            self.menu["Menu_frame"], image=self.bg)
        self.menu["Background"].place(x=0, y=0, relwidth=1, relheight=1)
        self.menu["New_game"] = tk.Button(
            self.menu["Menu_frame"], text="New game", font=button_font, height=2, width=15)
        self.menu["New_game"].grid(row=0, column=0, sticky="S", pady=50)
        self.menu["Load_game"] = tk.Button(
            self.menu["Menu_frame"], text="Load game", font=button_font, height=2, width=15)
        self.menu["Load_game"].grid(row=1, column=0, sticky="S", pady=50)
        self.menu["Cheats"] = tk.Button(
            self.menu["Menu_frame"], text="Cheats", font=button_font, height=2, width=15)
        self.menu["Cheats"].grid(row=2, column=0, sticky="S", pady=50)
        self.menu["Leaderboard"] = tk.Button(
            self.menu["Menu_frame"], text="Leaderboard", font=button_font, height=2, width=15)
        self.menu["Leaderboard"].grid(row=3, column=0, sticky="S", pady=50)
        # self.menu["Settings"] = tk.Button(self.menu["Menu_frame"], text="Settings", font=button_font, height=2, width=15)
        # self.menu["Settings"].grid(row = 4, column = 0, sticky="")
        self.menu["Menu_frame"].grid(row=0, column=0, sticky="NSEW")
        # Bind the left mouse press to game start
        self.menu["New_game"].bind(
            "<Button-1>", lambda a: self.change_app_state("game"))
        # Bind the load functionality
        self.menu["Load_game"].bind("<Button-1>", self.load_game)
        # Bind the leaderboard display, get path from config
        self.menu["Leaderboard"].bind(
            "<Button-1>", lambda a: utils.display_leaderboard(self.config["game"]["leaderboard_file_path"]))
        # Bind cheat codes menu display
        self.menu["Cheats"].bind(
            "<Button-1>", lambda a: self.change_app_state("cheat_codes"))
        # Bind settings open
        # self.menu["Settings"].bind("<Button-1>", lambda a: os.system(f"config.ini"))
        # Needed to display the background
        main_window.mainloop()


class Application:
    """Class for the whole application, contains tkinter top window and etc."""

    def __init__(self):
        self.main_window_dimensions = {
            "x": 1600,
            "y": 900
        }
        global main_window
        # Initially no save file path is selected, so game will start new
        self.config = {
            "save_file_path": ""
        }
        self.state = "game"  # Game states: menu, game
        # Initialize the main window
        self.configure_main_window()
        self.parse_config()
        self.change_app_state("menu")
        main_window.mainloop()

    def modify_config(self, key: str, value):
        """Modifies config"""
        self.config[key] = value

    def process_cheat_code(self, code: str) -> bool:
        """Process cheat code entered from the menu"""
        # If cheat code is valid, then activates it in the config
        # Cheatcodes:
        # infi - Infinite player health
        # aezkami - Infinite player damage
        # quortli - player scaling increased by factor of 2
        # junji - bombs deal no damage
        # scrcheat - score gain is multiplied by 2
        # uionjs - enemies scale slower by factor of 2
        codes = {
            "infi": "Infinite player health",
            "aezkami": "Infinite player damage",
            "quortli": "Player scaling increased by factor of 2",
            "junji": "Bombs deal no damage",
            "scrcheat": "Score gain is multiplied by 2",
            "uionjs": "Enemies scale 2 times slower"
        }
        # Check if the code entered is a valid cheatcode
        temp = codes.get(code)
        # If cheat code is valid and not applied
        if temp != None and code not in self.config["game"]["cheat_list"]:
            self.config["game"]["cheat_list"].append(code)
            print(f"{code} cheatcode applied: {temp}")
            return temp
        # If cheat code is valid but is already applied
        elif temp != None and code in self.config["game"]["cheat_list"]:
            print(f"{code} cheatcode is already applied")
            return "same"
        # If cheat code is unvalid
        else:
            print(f"{code} is not a valid cheat code")
            return ""

    def configure_main_window(self):
        """Initializes the main_window"""
        global main_window
        main_window = tk.Tk()
        main_window.title("SpaceShootaz")
        main_window.update_idletasks()
        # Get position for placing top left corner of the window
        x = int((main_window.winfo_screenwidth() -
                self.main_window_dimensions.get("x")) / 2)
        # - 30 is to account for the vertical navbar most OS have
        y = int((main_window.winfo_screenheight() -
                self.main_window_dimensions.get("y")) / 2) - 30
        main_window.geometry(
            f"{self.main_window_dimensions.get('x')}x{self.main_window_dimensions.get('y')}+{x}+{y}")
        main_window.configure(bg='white')
        main_window.resizable(False, False)

    def create_leaderboard(self):
        """Create leaderboard file if it doesnt exist"""
        temp = self.config["game"]["leaderboard_file_path"]
        # Creates a new leaderboard if it does not exist
        if not pathlib.Path(temp).exists():
            file = open(self.config["game"]["leaderboard_file_path"], "w")
            standard_leaderboard = "1) Jess: 1482.5\n2) Crab: 391.5\n3) Michael: 124"
            file.write(standard_leaderboard)
            file.close()
        # Creates saves folder if it doesn't already exist
        if not pathlib.Path("./saves").exists():
            os.mkdir("./saves")

    def create_new_config(self):
        """Creates a new config.ini file with standard settings below"""
        parser = configparser.ConfigParser()
        parser.add_section("IDENTITY")
        parser.set(
            "IDENTITY", "#Please relaunch the app for changes to take effect", "")
        parser.set("IDENTITY", "Name", "Bob the Builder")
        parser.set("IDENTITY", "Leaderboard_file_path", "leaderboard.txt")

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
        """Parses the config file into a self.config variable"""
        # Checks whether there is a config file
        file_exists = pathlib.Path("config.ini").exists()
        if not file_exists:
            # If no config, create new and read again
            self.create_new_config()
            self.parse_config()
        else:
            parser = configparser.ConfigParser()
            parser.read("config.ini")
            controls = {}
            game_config = {}
            # Parse config by sections
            for sect in parser.sections():
                for k, v in parser.items(sect):
                    if sect == "IDENTITY":
                        game_config[k] = v
                    elif sect == "GAME":
                        game_config[k] = v
                    elif sect == "CONTROLS":
                        # Tkinter treats space characters as " " thats why it is here
                        if v == "space":
                            v = " "
                        controls[k] = v

            self.config["controls"] = controls
            self.config["game"] = game_config
            self.config["game"]["cheat_list"] = []
            self.create_leaderboard()

    def change_app_state(self, new_state: str):
        """Function for changing app states
        App states:
        main_menu
        cheat_codes
        game
        """

        self.state = new_state
        # Destroy children widgets to reset the window on state change
        lst = main_window.grid_slaves()
        for l in lst:
            l.destroy()

        if self.state == "game":
            #self.modify_config("save_file_path", "saves/this_save.txt")
            # self.process_cheat_code("infi")
            # self.process_cheat_code("aezkami")
            # self.process_cheat_code("quortli")
            # self.process_cheat_code("junji")
            # self.process_cheat_code("scrcheat")
            # self.process_cheat_code("uionjs")
            game = Game(self.main_window_dimensions,
                        self.config, self.change_app_state)
        elif self.state == "menu":
            menu = Menu(self.main_window_dimensions,
                        self.change_app_state, self.config)
        elif self.state == "cheat_codes":
            cheats = CheatcodesMenu(
                self.change_app_state, self.config, self.process_cheat_code)


def main():
    """Starts the app"""
    global utils
    utils = Utilities()
    app = Application()


if __name__ == "__main__":
    """Entry point into program"""
    main()

# TODO: NOTHING! DONE!
