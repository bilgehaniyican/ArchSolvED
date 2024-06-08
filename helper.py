import json
import time

import ezdxf
import numpy as np
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from singleton import Singleton

upload_directory = "uploads"


class Ticketor(metaclass=Singleton):
    def __init__(self):
        self.id = 1

    def get_id_and_increment(self):
        current_id = self.id
        self.id += 1

        return current_id


class Database(metaclass=Singleton):
    def __init__(self):
        self.storage = {}
        self.data = {}

    def update_access_time(self, key):
        now = time.time()
        self.storage[key]["timestamp"] = now

    def new_entry(self, key):
        self.storage[key] = {}
        self.storage[key]["key"] = key

        self.update_access_time(key)

    def put_filename(self, key, filename):
        try:
            self.storage[key]["filename"] = filename.split(".")[0]
        except Exception:
            self.storage[key]["filename"] = filename

        self.update_access_time(key)

    def put_boundaries(self, key, boundaries):
        self.storage[key]["boundaries"] = boundaries
        self.update_access_time(key)

    def put_area(self, key, area):
        self.storage[key]["area"] = area
        self.update_access_time(key)

    def put_province(self, key, province):
        self.storage[key]["province"] = province
        self.update_access_time(key)

    def put_climate(self, key, climate):
        self.storage[key]["climate"] = climate
        self.update_access_time(key)

    def put_curriculum(self, key, curriculum):
        self.storage[key]["curriculum"] = curriculum
        self.update_access_time(key)

    def put_class_count(self, key, class_count):
        self.storage[key]["class_count"] = class_count
        self.update_access_time(key)

    def put_floor_count(self, key, floor_count):
        self.storage[key]["floor_count"] = floor_count
        self.update_access_time(key)

    def put_requirements(self, key, requirements):
        self.storage[key]["requirements"] = requirements
        self.update_access_time(key)

    def put_scale(self, key, scale):
        self.storage[key]["scale"] = scale
        self.update_access_time(key)

    def get_filename(self, key):
        self.update_access_time(key)

        return self.storage[key]["filename"]

    def get_class_count(self, key):
        self.update_access_time(key)

        return self.storage[key]["class_count"]

    def get_boundaries(self, key):
        self.update_access_time(key)

        boundaries = self.storage[key]["boundaries"]
        return boundaries["siteboundary"], boundaries["setbackboundary"], boundaries["corridor"]

    def clear_corridors(self, key):
        self.update_access_time(key)
        self.storage[key]["boundaries"]["corridor"] = []

    def get_climate_from_province(self, province_id):
        if "province_climate" not in self.data:
            with open("climatedata.json") as fp:
                self.data["province_climate"] = json.load(fp)

        for province in self.data["province_climate"]:
            if province["PLAKA"] == province_id:
                return province["CLIMATE CODE"]

    def get_scale(self, key):
        self.update_access_time(key)

        return self.storage[key]["scale"]

    def get_floor_count(self, key):
        self.update_access_time(key)

        return self.storage[key]["floor_count"]

    def get_requirements(self, key):
        self.update_access_time(key)

        return self.storage[key]["requirements"]

    def dump_data(self, key):
        self.update_access_time(key)

        return self.storage[key]


class DxfParser:
    def __init__(self, file_name):
        self.file_name = file_name

    def parse(self):
        dxf_document = ezdxf.readfile(self.file_name)
        points = {"siteboundary": [], "setbackboundary": [], "corridor": []}

        for entity in dxf_document.entities:
            layer_name = entity.dxf.layer
            if layer_name not in ["siteboundary", "setbackboundary", "corridor"]:
                continue

            if entity.DXFTYPE == "LWPOLYLINE":
                layer_points = []
                for point in entity:
                    x, y = point[0], point[1]
                    layer_points.append((x, y))

                points[layer_name] += layer_points

            elif entity.DXFTYPE == "LINE":
                line = ((entity.dxf.start[0], entity.dxf.start[1]),
                        (entity.dxf.end[0], entity.dxf.end[1]))
                points[layer_name].append(line)

        points = correct_coordinates(points)

        return points


def correct_coordinates(points):
    y_sum = 0

    new_points = {"siteboundary": [], "setbackboundary": [], "corridor": []}
    for point in points["siteboundary"]:
        y_sum += point[1]

    for point in points["setbackboundary"]:
        y_sum += point[1]

    for start, end in points["corridor"]:
        y_sum += start[1] + end[1]

    count = len(points["siteboundary"]) + len(points["setbackboundary"]) + 2 * len(points["corridor"])
    if count == 0:
        return None

    y_mean = y_sum / count

    for point in points["siteboundary"]:
        new_point = (point[0], 2 * y_mean - point[1])

        new_points["siteboundary"].append(new_point)

    for point in points["setbackboundary"]:
        new_point = (point[0], 2 * y_mean - point[1])

        new_points["setbackboundary"].append(new_point)

    for start, end in points["corridor"]:
        new_start = (start[0], 2 * y_mean - start[1])
        new_end = (end[0], 2 * y_mean - end[1])

        new_line = (new_start, new_end)

        new_points["corridor"].append(new_line)

    return new_points


def correct_coordinates_x(points):
    x_sum = 0

    new_points = {"siteboundary": [], "setbackboundary": [], "corridor": []}
    for point in points["siteboundary"]:
        x_sum += point[0]

    for point in points["setbackboundary"]:
        x_sum += point[0]

    for start, end in points["corridor"]:
        x_sum += start[0] + end[0]

    count = len(points["siteboundary"]) + len(points["setbackboundary"]) + 2 * len(points["corridor"])
    if count == 0:
        return None

    x_mean = x_sum / count

    for point in points["siteboundary"]:
        new_point = (2 * x_mean - point[0], point[1])

        new_points["siteboundary"].append(new_point)

    for point in points["setbackboundary"]:
        new_point = (2 * x_mean - point[0], point[1])

        new_points["setbackboundary"].append(new_point)

    for start, end in points["corridor"]:
        new_start = (2 * x_mean - start[0], start[1])
        new_end = (2 * x_mean - end[0], end[1])

        new_line = (new_start, new_end)

        new_points["corridor"].append(new_line)

    return new_points


def read_html_from_file(filename: str) -> str:
    with open(filename, "r", encoding="utf8") as fp:
        content = "".join(fp.readlines())

    return content


def handle_uploaded_file(uploaded_file: FileStorage):
    if uploaded_file is not None and uploaded_file.filename != "" and \
            "dxf" in uploaded_file.filename.rsplit(".", 1):
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save("{0}/{1}".format(upload_directory, filename))
    else:
        filename = None

    return f"{upload_directory}/{filename}"


def get_scale_and_deltas(shape, dimension, border):
    shape = np.array(shape)

    scale = (dimension - 2 * border) / max(shape[:, :1].max() - shape[:, :1].min(),
                                           shape[:, 1:].max() - shape[:, 1:].min())

    shape *= scale

    x_delta = (shape[:, :1].min() + shape[:, :1].max()) / 2 - dimension / 2
    y_delta = (shape[:, 1:].min() + shape[:, 1:].max()) / 2 - dimension / 2

    return scale, x_delta, y_delta


def scale_and_center_result(solutions, dimension, border):
    scale_result(solutions, dimension, border)
    center_result(solutions, dimension)


def find_extremes(solution):
    extremes = {"xmin": 999999999999999999999999999999999, "xmax": 0,
                "ymin": 999999999999999999999999999999999, "ymax": 0}

    for shape in solution["shapes"]:
        for point in shape["points"]:
            if point[0] > extremes["xmax"]:
                extremes["xmax"] = point[0]
            if point[0] < extremes["xmin"]:
                extremes["xmin"] = point[0]
            if point[1] > extremes["ymax"]:
                extremes["ymax"] = point[1]
            if point[1] < extremes["ymin"]:
                extremes["ymin"] = point[1]

    return extremes


def scale_result(solutions, dimension, border):
    for solution in solutions:
        extremes = find_extremes(solution)

        scale = (dimension - 2 * border) / max(extremes["xmax"] - extremes["xmin"],
                                               extremes["ymax"] - extremes["ymin"])

        for shape in solution["shapes"]:
            scaled_points = []
            for point in shape["points"]:
                scaled_points.append((
                    point[0] * scale,
                    point[1] * scale
                ))
            shape["points"] = scaled_points


def center_result(solutions, dimension):
    for solution in solutions:
        extremes = find_extremes(solution)

        xdelta = dimension / 2 - (extremes["xmax"] + extremes["xmin"]) / 2
        ydelta = dimension / 2 - (extremes["ymax"] + extremes["ymin"]) / 2

        for shape in solution["shapes"]:
            offseted_points = []
            for point in shape["points"]:
                offseted_points.append((
                    point[0] + xdelta,
                    point[1] + ydelta
                ))
            shape["points"] = offseted_points


def unscale_shape(shape, scale, dimension):
    for line in shape:
        line[0][0] = (dimension - line[0][0]) / scale
        line[0][1] = (dimension - line[0][1]) / scale
        line[1][0] = (dimension - line[1][0]) / scale
        line[1][1] = (dimension - line[1][1]) / scale

    return shape


def calculate_area_of_polygon(points):
    area = 0.0
    for (i) in range(-1, len(points) - 1):
        area += points[i][0] * (points[i + 1][1] - points[i - 1][1])
    return round(abs(area) / 2.0)


def calculate_required_corridor_length(rooms, floor):
    total = 0
    for room in rooms.values():
        if "length" not in room:
            continue

        total += room["length"] * room["count"]

    per_floor = total / floor
    adjusted = per_floor * 1.0 / 2

    return adjusted


def load_legend_data():
    with open("colors.json", "r") as fd:
        colors = json.load(fd)

    legend_data = []
    for room_name, color in colors.items():
        legend_data.append(
            {"name": room_name_display(room_name), "color": color}
        )

    return json.dumps(legend_data)


def room_name_display(room_name):
    lookup = {
        "classroom": "Classroom",
        "library": "Library",
        "laboratory": "Laboratory",
        "cafe": "Cafeteria",
        "mess": "Dining Hall",
        "hall": "Multi-Purpose Hall",
        "gym": "Gymnasium",
        "auditorium": "Auditorium",
        "workshop": "Workshop",
        "WC": "WC",
        "circulation": "Circulation",
        "administrative": "Administrative",
        "teacherslounge": "Teachers' Room",
        "headmasters": "Principal's Office",
        "counseling": "Counseling"
    }

    return lookup[room_name]
