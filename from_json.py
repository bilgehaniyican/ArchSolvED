import os

from flask import Flask, request

import json
from helper import load_legend_data, scale_and_center_result, DxfParser, correct_coordinates_x
from main import read_html_from_file
from solver.enums import Climate
from solver.school import School

app = Flask(__name__)

template = """<option value="{0}">{0}</a>"""


@app.route("/")
def index():
    jsons = []
    for file in os.listdir("json"):
        file_name = file.rsplit("/", 1)
        file_name = file_name[1] if len(file_name) > 1 else file_name[0]
        if file_name == ".gitignore":
            continue
        jsons.append(template.format(file_name))
    jsons = "<br>\n".join(jsons)

    climates = []
    for climate in Climate:
        climate = ["Cold", "Mild", "Hot-Dry", "Hot-Humid"][int(climate)]
        climates.append(template.format(climate))
    climates = "<br>\n".join(climates)

    dxfs = []
    for file in os.listdir("dxf"):
        file_name = file.rsplit("/", 1)
        file_name = file_name[1] if len(file_name) > 1 else file_name[0]
        if file_name == ".gitignore":
            continue
        dxfs.append(template.format(file_name))
    dxfs = "<br>\n".join(dxfs)

    return read_html_from_file("from_json_index.html").format(json=jsons, climate=climates, dxf=dxfs)


@app.route("/solve")
def save_circulation_run_solver_and_serve_show_results() -> str:
    json_file = request.args.get("json")
    with open("json/{0}".format(json_file), "r") as fd:
        data = json.load(fd)

    climate = request.args.get("climate")
    if climate == "Cold":
        climate = "D"
    elif climate == "Mild":
        climate = "C"
    elif climate == "Hot-Dry":
        climate = "B"
    else:
        climate = "A"

    data["climate"] = climate

    dxf_file = request.args.get("dxf")
    boundaries = DxfParser("dxf/{0}".format(dxf_file)).parse()

    solutions = School(data).solve()
    solutions = list(
        map(
            lambda e: {"i": e[0], "score": e[1].get_score(), "shapes": e[1].get_shapes()},
            enumerate(solutions)
        )
    )

    solution_count = len(solutions)

    solutions.sort(key=lambda s: s["score"], reverse=True)
    solutions = solutions[:50]

    scale_and_center_result(solutions, 400, 10)
    data = json.dumps(solutions)

    legend_data = load_legend_data()

    score = solutions[0]["score"]

    title = "{0}_{1}_solution_count_{2}_score_{3}".format(request.args.get("climate"), dxf_file, solution_count, round(score))

    return read_html_from_file("show_result.html").format(process_id=0, data=data, legend_data=legend_data, title=title)


@app.route("/muscle.js")
def muscle():
    return read_html_from_file("muscle.js")

@app.route("/style.css")
def style():
    return read_html_from_file("style.css")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
