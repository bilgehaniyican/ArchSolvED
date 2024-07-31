function enable_submit() {
    document.getElementById("submit").disabled = false;
}

function show_corridors() {
    let canvas = document.getElementById("canvas");
    let ctx = canvas.getContext("2d");
    ctx.lineWidth = 5;

    let land_boundary = JSON.parse(document.getElementById("land_boundary").innerText);
    draw_me_a_polygon(ctx, land_boundary);

    let construction_boundary = JSON.parse(document.getElementById("construction_boundary").innerText);
    draw_me_a_polygon(ctx, construction_boundary);

    let corridors = JSON.parse(document.getElementById("corridors").innerText);
    for (let line of corridors) {
        ctx.beginPath();
        ctx.moveTo(line[0][0], line[0][1]);
        ctx.lineTo(line[1][0], line[1][1]);
        ctx.stroke();
    }
}

function draw_me_a_polygon(draw_context, points) {
    let first_point = points[0];

    draw_context.beginPath();
    draw_context.moveTo(first_point[0], first_point[1]);

    for (let i = 1; i < points.length; i++) {
        let point = points[i];
        draw_context.lineTo(point[0], point[1]);
    }

    draw_context.lineTo(first_point[0], first_point[1]);

    draw_context.stroke();
}

function on_result_page_load() {
    draw_legend()
    draw_canvas_from_data()
}

function draw_legend() {
    let legend = document.getElementById("legend");
    do_draw_legend(legend);
}

function do_draw_legend(legend) {
    let legend_text = document.getElementById("legend-data").innerText;
    let data = JSON.parse(legend_text);

    for (let d of data) {
        draw_legend_entry(legend, d)
    }
}

function draw_legend_entry(legend, legend_entry) {
    let legend_cell = document.createElement("div");
    legend_cell.style.margin = ".5em";
    legend_cell.style.textAlign = "center";

    let color_square = document.createElement("span");
    color_square.style.display = "block";
    color_square.style.width = "4em";
    color_square.style.height = "4em";
    color_square.style.margin = "1em";
    color_square.style.backgroundColor = legend_entry.color;
    legend_cell.appendChild(color_square);

    let legend_text = document.createElement("div");
    legend_text.innerText = legend_entry.name;
    legend_cell.appendChild(legend_text);

    legend.appendChild(legend_cell);
}

function draw_canvas_from_data() {
    let data = JSON.parse(document.getElementById("data").innerText);

    if (data.length === 0) {
        let results = document.getElementById("results");
        results.innerText = "No results could be generated. Change parameters and try again."
        return;
    }

    for (let d of data) {
        insert_element_and_draw(d);
    }
}

function insert_element_and_draw(data) {
    let results = document.getElementById("results");
    let text_row = results.insertRow(-1);
    text_row.style.borderTop = "1px solid black";
    let image_row = results.insertRow(-1);

    do_insert_result(data, text_row, image_row);
}

function do_insert_result(data, text_row, image_row) {
    text_row.innerHTML = "<td><h3 style='padding: 0.1em'>Solution: " + (data.i + 1).toString() + "</h3></td>" + "<td><h3 style='padding: 0.1em'>Score: " + data.score.toFixed(2) + "</h3></td>" + "<td><button onclick='print_solution(" + data.i + ")'>Print</button></td>" + "<td>↑N</td>";


    let cells = {};
    for (let shape of data["shapes"]) {
        let layer_id = shape["layer"];
        if (!(layer_id in cells)) {
            let layer_data = {};

            layer_data.cell = image_row.insertCell(layer_id);

            let layer_text = document.createElement("p");
            layer_text.innerText = "Floor " + layer_id;
            layer_data.cell.appendChild(layer_text);

            layer_data.canvas = document.createElement("canvas");
            layer_data.canvas.width = 400;
            layer_data.canvas.height = 400;

            layer_data.cell.appendChild(layer_data.canvas);
            cells[layer_id] = layer_data;
        }
    }

    for (let shape of data["shapes"]) {
        let layer_id = shape["layer"];
        let layer = cells[layer_id];
        let canvas = layer["canvas"];
        let points = shape["points"];

        let ctx = canvas.getContext("2d");
        ctx.fillStyle = shape["color"];

        let lineWidth = ctx.lineWidth;
        let strokeStyle = ctx.strokeStyle;

        if (points.length == 2) {
            ctx.strokeStyle = "red";
            ctx.lineWidth = 4;
        }

        ctx.beginPath();
        ctx.moveTo(points[0][0], points[0][1]);
        ctx.lineTo(points[1][0], points[1][1]);
        if (points.length > 2) {
            ctx.lineTo(points[2][0], points[2][1]);
            ctx.lineTo(points[3][0], points[3][1]);
            ctx.lineTo(points[0][0], points[0][1]);
            ctx.fill();
        }

        ctx.closePath();

        ctx.stroke();

        if (points.length == 2) {
            ctx.strokeStyle = strokeStyle;
            ctx.lineWidth = lineWidth;
        }

        if (points.length > 2) {
            let x = (points[0][0] + points[1][0] + points[2][0] + points[3][0]) / 4;
            let y = (points[0][1] + points[1][1] + points[2][1] + points[3][1]) / 4;

            ctx.font = "12px Arial";
            ctx.textBaseline = "middle";
            ctx.textAlign = "center";
            ctx.fillStyle = "black";

            ctx.fillText(shape["score"], x, y);
        }
    }
}

function update_areas() {
    let rooms = ["classroom", "library", "laboratory", "cafe", "mess", "hall", "gym", "auditorium", "workshop", "WC", "circulation", "administrative", "counseling", "teacherslounge", "headmasters"];

    let total = 0;
    for (let room_type of rooms) {
        let area = parseInt(document.getElementById(room_type + "_width").value) * parseInt(document.getElementById(room_type + "_length").value) * parseInt(document.getElementById(room_type + "_count").value);

        document.getElementById(room_type + "_area").innerText = area.toString();

        total += area;
    }

    let circulation_ratio = parseFloat(document.getElementById("circulation_ratio").value) / 100.0;
    let total_with_circulation = total * (1 + circulation_ratio);
    document.getElementById("total_building_area").innerText = total_with_circulation.toFixed(0);
}

function print_solution(i) {
    let frame = document.createElement("iframe");
    frame.domain = document.domain;
    frame.style.position = "absolute";
    frame.style.top = "-10000px";
    document.body.appendChild(frame);

    // <link type="text/css" rel="stylesheet" href="style.css">
    let style = frame.contentDocument.createElement("style");
    frame.contentDocument.head.appendChild(style);

    frame.contentDocument.write("<h1>ArchSolved</h1>" + "<h2>Result</h2>" + "<table id='result' class='result'></table>" + "<h2>Legend</h2>" + "<div id='legend' class='legend'></div>");

    let body = frame.contentDocument.body;
    let data = JSON.parse(document.getElementById("data").innerText)[i];
    let result = body.getElementsByClassName("result")[0];
    let text_row = result.insertRow(-1);
    let image_row = result.insertRow(-1);
    do_insert_result(data, text_row, image_row);

    let legend = body.getElementsByClassName("legend")[0];
    legend.style = "border: 1em black; display: flex; flex-wrap: wrap;";
    do_draw_legend(legend);

    setTimeout(function () {
        frame.focus();
        frame.contentWindow.print();
        frame.parentNode.removeChild(frame);
    }, 3000);
    window.focus();
}

function check_student_density() {
    const OK_MESSAGE = "The land has sufficient capacity"
    const NOK_MESSAGE = "Land capacity is insufficient, please proceed with this in mind"
    const STUDENTS_PER_CLASSROOM = 30;

    let classroom_count = parseInt(document.getElementById("class_count").value);
    let area = parseInt(document.getElementById("land_area").value);
    let required_area_per_student = parseInt(document.getElementById("density_standard").value);

    let message = document.getElementById("density_message");
    let possible_student_count = area / required_area_per_student;
    let desired_student_count = STUDENTS_PER_CLASSROOM * classroom_count;
    if (possible_student_count >= desired_student_count) {
        message.innerText = OK_MESSAGE;
    } else {
        message.innerText = NOK_MESSAGE;
    }
}

function populate_scores_table() {
    const details = document.getElementById("score-details");
    const table_body = document.getElementById("score-table");

    if (details.open) {
        const json = document.getElementById("score-data").innerText;
        const data = JSON.parse(json);

        for (const unit of data) {
            const name = unit.name;
            const scores = unit.scores;

            const row = table_body.insertRow(-1);

            const name_cell = row.insertCell(-1);
            name_cell.style.textAlign = "right";
            name_cell.innerText = name;
            name_cell.style.border = "1px";
            name_cell.style.borderStyle = "solid";
            name_cell.style.paddingRight = "5px";

            for (const score of scores) {
                const cell = row.insertCell(-1);
                let score_numeric = parseInt(score);
                if (score_numeric === 50) {
                    cell.style.backgroundColor = "#90E0EF";
                } else if (score_numeric === 100) {
                    cell.style.backgroundColor = "#48BBDB";
                }

                cell.width = "10em";
                cell.style.textAlign = "center";
                cell.style.border = "1px";
                cell.style.borderStyle = "solid";

                cell.innerText = score;
            }
        }
    } else {
        table_body.innerHTML = "";
    }
}
