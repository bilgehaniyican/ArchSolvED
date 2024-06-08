const canvas_states = {
    READY_TO_DRAW: 1,
    DRAW_ONGOING: 2,
    FROZEN: 3
};

const action_types = {
    LINE_DRAW_START: 1,
    LINE_DRAW_END: 2
};

class Action {
    constructor(point, type) {
        this.point = point;
        this.type = type;
    }
}

class Point {
    constructor(X, Y) {
        this.X = X;
        this.Y = Y;
    }

    distance_from(point) {
        let X_delta = this.X - point.X;
        let Y_delta = this.Y - point.Y;

        return Math.sqrt(square(X_delta) + square(Y_delta));
    }

    closest_of(actions) {
        if (Array.isArray(actions) === false || actions.length === 0) {
            return null;
        }

        let closest = null;
        let closest_distance = 0;

        for (let action of actions) {
            let point = action.point;
            let distance_from_point = this.distance_from(point);
            if (closest == null || distance_from_point < closest_distance) {
                closest = point;
                closest_distance = distance_from_point;
            }
        }

        return closest;
    }

    is_inside_of_polygon(polygon) {
        if (this.X <= build_limit_min_x || this.X >= build_limit_max_x || this.Y <= build_limit_min_y || this.Y >= build_limit_max_y) {
            return false;
        }

        let is_inside = false;

        let i = 0;
        let j = polygon.length - 1;
        while (i < polygon.length) {
            let a = (polygon[i][1] >= this.Y) !== (polygon[j][1] >= this.Y);
            let b = this.X <= (polygon[j][0] - polygon[i][0]) * (this.Y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) + polygon[i][0];

            if (a === true && b === true) {
                is_inside = !is_inside;
            }

            j = i;
            i++;
        }

        return is_inside;
    }
}

let canvas = null;

let actions_list = null;
let undo_list = null;

let snap_radius = 0;
let meter_unit_conversion_factor = 0;

let total_line_length = null;
let current_line_length = null;
let remaining_line_length = null;
let required_line_length = 0;

let current_state = canvas_states.FROZEN;

let land_limit = null;
let build_limit = null;

let build_limit_min_x = 0;
let build_limit_max_x = 0;
let build_limit_min_y = 0;
let build_limit_max_y = 0;

function init() {
    canvas = document.getElementById("canvas");

    actions_list = [];
    undo_list = [];

    snap_radius = JSON.parse(document.getElementById("snap_radius").value);
    meter_unit_conversion_factor = JSON.parse(document.getElementById("meter_unit_conversion_factor").value);

    required_line_length = JSON.parse(document.getElementById("required_corridor_length").value);

    total_line_length = document.getElementById("total_line_length");
    total_line_length.innerHTML = "0";

    current_line_length = document.getElementById("current_line_length");
    current_line_length.innerHTML = "0";

    remaining_line_length = document.getElementById("remaining_line_length");
    remaining_line_length.innerHTML = required_line_length.toFixed(2).toString();

    land_limit = JSON.parse(document.getElementById("land_limits").value);
    build_limit = JSON.parse(document.getElementById("build_limits").value);

    calculate_bounding_box();
    raster_actions(null);

    current_state = canvas_states.READY_TO_DRAW;
}

function square(value) {
    return Math.pow(value, 2);
}

function calculate_total_length() {
    let line_start_point = null;
    let total_length = 0;

    for (let action of actions_list) {
        switch (action.type) {
            case action_types.LINE_DRAW_START:
                line_start_point = action.point;
                break;

            case action_types.LINE_DRAW_END:
                let line_end_point = action.point;
                total_length += line_end_point.distance_from(line_start_point);
                break;
        }
    }

    let length = (total_length / meter_unit_conversion_factor);
    let intersect_offset = (7 * actions_list.length / 2);

    return length - intersect_offset;
}

function handle_click(handler_arguments) {
    let mouseup_event = handler_arguments[0];
    let click_point = new Point(mouseup_event.offsetX, mouseup_event.offsetY);

    if (click_point.is_inside_of_polygon(build_limit) === false) {
        return null;
    }

    let closest_existing_point = click_point.closest_of(actions_list);
    if (closest_existing_point != null && click_point.distance_from(closest_existing_point) < snap_radius) {
        click_point = closest_existing_point;
    }

    let action = null;
    switch (current_state) {
        case canvas_states.READY_TO_DRAW:
            action = new Action(click_point, action_types.LINE_DRAW_START);
            actions_list.push(action);

            current_state = canvas_states.DRAW_ONGOING;
            break;

        case canvas_states.DRAW_ONGOING:
            action = new Action(click_point, action_types.LINE_DRAW_END);
            actions_list.push(action);

            update_lengths();

            current_state = canvas_states.READY_TO_DRAW;
            break;

        case canvas_states.FROZEN:
            break;

        default:
            break;
    }

    raster_actions(null);
}

function handle_move(handler_arguments) {
    let mousemove_event = handler_arguments[0];
    let click_point = new Point(mousemove_event.offsetX, mousemove_event.offsetY);

    if (click_point.is_inside_of_polygon(build_limit) === false) {
        return null;
    }

    let closest_existing_point = click_point.closest_of(actions_list);
    if (closest_existing_point != null && click_point.distance_from(closest_existing_point) < snap_radius) {
        click_point = closest_existing_point;
    }

    let preview_action = null;
    switch (current_state) {
        case canvas_states.READY_TO_DRAW:
            preview_action = new Action(click_point, action_types.LINE_DRAW_START);
            break;

        case canvas_states.DRAW_ONGOING:
            preview_action = new Action(click_point, action_types.LINE_DRAW_END);
            break;

        case canvas_states.FROZEN:
            break;

        default:
            break;
    }

    raster_actions(preview_action);
}

function handle_done() {
    current_state = canvas_states.FROZEN;

    let points = [];

    let start_point = null;

    for (let action of actions_list) {
        switch (action.type) {
            case action_types.LINE_DRAW_START:
                start_point = action.point;
                break;

            case action_types.LINE_DRAW_END:
                let end_point = action.point;

                let data = {
                    "start": start_point,
                    "end": end_point
                };

                points.push([[start_point.X, start_point.Y], [end_point.X, end_point.Y]]);
                break;
        }
    }

    let form = document.createElement("form");
    form.method = "post";
    form.action = "/show_result";

    let process_id = document.getElementById("process_id").value;
    let process_id_field = document.createElement("input");
    process_id_field.type = "hidden";
    process_id_field.name = "process_id";
    process_id_field.value = process_id;
    form.appendChild(process_id_field);

    let points_field = document.createElement("input");
    points_field.type = "hidden";
    points_field.name = "points";
    points_field.value = JSON.stringify(points);
    form.appendChild(points_field);

    document.body.appendChild(form);
    form.submit();
}

function raster_actions(preview_action) {
    let draw_context = canvas.getContext("2d");

    draw_context.clearRect(0, 0, canvas.width, canvas.height);

    draw_context.lineWidth = 1;
    draw_polygon(draw_context, land_limit);
    draw_polygon(draw_context, build_limit);

    draw_context.lineWidth = 5;
    for (let action of actions_list) {
        switch (action.type) {
            case action_types.LINE_DRAW_START:
                draw_context.beginPath();
                draw_context.arc(action.point.X, action.point.Y, 4, 0, 2 * Math.PI);
                draw_context.stroke();

                draw_context.beginPath();
                draw_context.moveTo(action.point.X, action.point.Y);
                break;

            case action_types.LINE_DRAW_END:
                draw_context.lineTo(action.point.X, action.point.Y);
                draw_context.stroke();

                draw_context.beginPath();
                draw_context.arc(action.point.X, action.point.Y, 4, 0, 2 * Math.PI);
                draw_context.stroke();
                break;
        }
    }

    if (preview_action != null) {
        let preview_point = preview_action.point;

        switch (preview_action.type) {
            case action_types.LINE_DRAW_START:
                draw_context.beginPath();
                draw_context.arc(preview_point.X, preview_point.Y, 4, 0, 2 * Math.PI);
                draw_context.stroke();

                draw_context.beginPath();
                draw_context.moveTo(preview_point.X, preview_point.Y);
                break;

            case action_types.LINE_DRAW_END:
                draw_context.lineTo(preview_point.X, preview_point.Y);
                draw_context.stroke();

                let last_point_start = actions_list[actions_list.length - 1].point;
                let preview_line_distance = last_point_start.distance_from(preview_point) / meter_unit_conversion_factor;
                if (preview_line_distance < 7) {
                    current_line_length.innerHTML = 0;
                } else {
                    current_line_length.innerHTML = (preview_line_distance - 7).toFixed(2).toString();
                }

                draw_context.beginPath();
                draw_context.arc(preview_point.X, preview_point.Y, 4, 0, 2 * Math.PI);
                draw_context.stroke();
                break;
        }
    }

}

function draw_polygon(draw_context, points) {
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

function handle_undo() {
    let action = actions_list.pop();
    if (action === undefined) {
        return;
    }

    undo_list.push(action);

    switch (action.type) {
        case action_types.LINE_DRAW_START:
            current_state = canvas_states.READY_TO_DRAW;
            break;

        case action_types.LINE_DRAW_END:
            current_state = canvas_states.DRAW_ONGOING;
            break;
    }

    update_lengths();

    raster_actions(null);
}

function handle_redo() {
    let action = undo_list.pop();
    if (action === undefined) {
        return;
    }

    actions_list.push(action);

    switch (action.type) {
        case action_types.LINE_DRAW_START:
            current_state = canvas_states.DRAW_ONGOING;
            break;

        case action_types.LINE_DRAW_END:
            current_state = canvas_states.READY_TO_DRAW;
            break;
    }

    update_lengths();

    raster_actions(null);
}

function calculate_bounding_box() {
    build_limit_min_x = build_limit[0][0];
    build_limit_max_x = build_limit[0][0];
    build_limit_min_y = build_limit[0][1];
    build_limit_max_y = build_limit[0][1];

    for (let n = 1; n < build_limit.length; n++) {
        const q = build_limit[n];

        build_limit_min_x = Math.min(q[0], build_limit_min_x);
        build_limit_max_x = Math.max(q[0], build_limit_max_x);
        build_limit_min_y = Math.min(q[1], build_limit_min_y);
        build_limit_max_y = Math.max(q[1], build_limit_max_y);
    }
}

function update_lengths() {
    current_line_length.innerHTML = "";

    let total_lines = calculate_total_length();
    total_line_length.innerHTML = total_lines.toFixed(2).toString();

    let remaining_lines = required_line_length - total_lines;
    if (remaining_lines < 0) {
        remaining_lines = 0;
    }
    remaining_line_length.innerHTML = remaining_lines.toFixed(2).toString();
}

function show_modal(should_show) {
    if (should_show === "true" || should_show === true) {
        let modal = document.getElementById("modal");
        modal.style.display = "block";
    }
}

function hide_modal() {
    let modal = document.getElementById("modal");
    modal.style.display = "none";
}
