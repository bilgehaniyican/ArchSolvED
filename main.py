from flask import Flask, request, Response

from helper import *

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = upload_directory


@app.route("/")
def serve_index() -> str:
    return read_html_from_file("index.html")


@app.route("/upload_plan")
def serve_upload() -> str:
    process_id = Ticketor().get_id_and_increment()
    Database().new_entry(process_id)
    return read_html_from_file("upload_plan.html").format(process_id=process_id)


@app.route("/select_curriculum_and_climate", methods=["post"])
def save_plan_and_serve_curriculum_selection() -> str:
    process_id = request.form.get("process_id", 0, type=int)

    use_sample = request.form.get("sample-file")
    if use_sample:
        file_name = "sample.dxf"
    else:
        uploaded_file = request.files.get("dxf-file")
        file_name = handle_uploaded_file(uploaded_file)

    Database().put_filename(process_id, file_name)

    boundaries = DxfParser(file_name).parse()
    Database().put_boundaries(process_id, boundaries)

    area = calculate_area_of_polygon(boundaries["siteboundary"])
    Database().put_area(process_id, area)

    return read_html_from_file("select_curriculum_and_climate.html").format(process_id=process_id, area=area)


@app.route("/set_requirements_list", methods=["post"])
def save_curriculum_and_serve_requirements_list() -> str:
    process_id = request.form.get("process_id", 0, type=int)

    curriculum = request.form.get("curriculum", 0, type=int)
    Database().put_curriculum(process_id, curriculum)

    with open("requirements.json", "r") as fd:
        curriculum_requirements = json.load(fd)[f"{curriculum}"]

    province = request.form.get("province", 0, type=int)
    Database().put_province(process_id, province)

    climate = Database().get_climate_from_province(province)
    Database().put_climate(process_id, climate)

    floor_count = request.form.get("floor_count", 0, type=int)
    Database().put_floor_count(process_id, floor_count)

    class_count = request.form.get("class_count", 0, type=int)
    Database().put_class_count(process_id, class_count)

    return read_html_from_file("set_requirements_list.html").format(
        process_id=process_id,
        class_count=class_count,
        WC_count=Database().get_floor_count(process_id) * 2,
        administrative_count=Database().get_floor_count(process_id),
        library_count=curriculum_requirements["library"],
        lab_count=curriculum_requirements["lab"],
        cafe_count=curriculum_requirements["cafe"],
        mess_count=curriculum_requirements["mess"],
        hall_count=curriculum_requirements["hall"],
        gym_count=curriculum_requirements["gym"],
        auditorium_count=curriculum_requirements["auditorium"],
        workshop_count=curriculum_requirements["workshop"],
        circulation_count=curriculum_requirements["circulation"],
        counseling_count=curriculum_requirements["counseling"],
        teacherslounge_count=curriculum_requirements["teacherslounge"],
        headmasters_count=curriculum_requirements["headmasters"],
    )


@app.route("/circulation", methods=["post"])
def save_requirements_list_and_serve_circulation_drawer() -> str:
    process_id = request.form.get("process_id", 0, type=int)

    land_boundary, construction_boundary, corridors = Database().get_boundaries(process_id)

    dimension = 1000
    border = 20
    scale, x_delta, y_delta = get_scale_and_deltas(land_boundary, dimension, border)
    scale_point = lambda p: (p[0] * scale - x_delta, p[1] * scale - y_delta)

    if len(corridors) == 0:
        rooms = {}
        for key, value in request.form.items():
            room_type, room_attribute = tuple(key.rsplit("_", 1))

            if room_type not in rooms:
                rooms[room_type] = {}

            rooms[room_type][room_attribute] = int(value)

        rooms["classroom"]["count"] = Database().get_class_count(process_id)
        Database().put_requirements(process_id, rooms)

        floor_count = Database().get_floor_count(process_id)
        required_corridor_length = calculate_required_corridor_length(rooms, floor_count)

        Database().put_scale(process_id, scale)

        land_boundary_scaled = list(map(scale_point, land_boundary))
        construction_boundary_scaled = list(map(scale_point, construction_boundary))

        show_popup = "true"
    else:
        Database().clear_corridors(process_id)
        scale = Database().get_scale(process_id)

        land_boundary_scaled = list(map(scale_point, land_boundary))
        construction_boundary_scaled = list(map(scale_point, construction_boundary))

        floor_count = Database().get_floor_count(process_id)
        rooms = Database().get_requirements(process_id)
        required_corridor_length = calculate_required_corridor_length(rooms, floor_count)

        show_popup = "false"

    return read_html_from_file("draw_corridors.html").format(
        process_id=process_id,
        land_boundary=json.dumps(land_boundary_scaled),
        construction_boundary=json.dumps(construction_boundary_scaled),
        snap_radius=10,
        required_corridor_length=required_corridor_length,
        meter_unit_conversion_factor=scale,
        show_popup=show_popup,
        score_data=json.dumps(get_climate_score_json(Database().get_climate(process_id)))
    )


@app.route("/show_result", methods=["post"])
def save_circulation_run_solver_and_serve_show_results() -> str:
    from solver.school import School
    from helper import load_legend_data
    from datetime import datetime

    process_id = request.form.get("process_id", 0, type=int)

    land_boundary, construction_boundary, corridors = Database().get_boundaries(process_id)
    if len(corridors) == 0:
        points = json.loads(request.form.get("points"))

        for start, end in points:
            start[0] = 1000 - start[0]
            end[0] = 1000 - end[0]

            start[1] = 1000 - start[1]
            end[1] = 1000 - end[1]

        scale = Database().get_scale(process_id)
        corridor_points = unscale_shape(points, scale, 1000)
        boundaries = {"siteboundary": land_boundary, "setbackboundary": construction_boundary, "corridor": corridor_points}

        Database().put_boundaries(process_id, boundaries)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open("json/{0}.json".format(timestamp), "w") as fd:
        json.dump(Database().dump_data(process_id), fd)

    solutions = School(Database().dump_data(process_id)).solve()
    solutions = enumerate(solutions)
    solutions = list(map(lambda e: {"i": e[0], "score": e[1].get_score(), "shapes": e[1].get_shapes(), "class_score": e[1].get_class_score()}, solutions))

    solutions.sort(key=lambda s: s["score"], reverse=True)
    solutions = solutions[:50]

    scale_and_center_result(solutions, 400, 10)
    data = json.dumps(solutions)

    legend_data = load_legend_data()

    return read_html_from_file("show_result.html").format(
        process_id=process_id,
        data=data,
        legend_data=legend_data,
        title="ArchSolvED",
        score_data=json.dumps(get_climate_score_json(Database().get_climate(process_id)))
    )


@app.route("/corridor_drawer.js")
def serve_corridor_drawer_js() -> Response:
    return Response(read_html_from_file("corridor_drawer.js"), mimetype="text/javascript")


@app.route("/muscle.js")
def serve_muscle_js() -> Response:
    return Response(read_html_from_file("muscle.js"), mimetype="text/javascript")


@app.route("/style.css")
def serve_style_css() -> Response:
    return Response(read_html_from_file("style.css"), mimetype="text/css")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
