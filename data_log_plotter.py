import math
from PIL import Image, ImageColor, ImageDraw

white = ImageColor.getrgb("#ffffff")
grid_lines_color = ImageColor.getrgb("#cccccc")
black = ImageColor.getrgb("#000000")
data_line_color = ImageColor.getrgb("#00a000")

def plot_graphs(data_log, output_filename):
    num_graphs = len(data_log)

    img = Image.new('RGB', (1064, 548 * num_graphs + 16), white)
    draw = ImageDraw.Draw(img)

    for graph_num in range(num_graphs):
        start_x = 36
        width = 1000
        start_y = 548 * graph_num + 530
        height = 500

        current_graph = data_log[graph_num]
        data_series = current_graph[0]
        vertical_axis_label = current_graph[1]
        horizontal_axis_label = current_graph[2]

        max_horizontal = 1  # not 0 to prevent division by zero later
        min_horizontal = 0
        max_vertical = 1
        min_vertical = 0
        for point in data_series:
            if point[0]:
                # Round the values for grid min/max purposes so that minor
                # rounding/integration errors don't create unnecessary grid lines.
                rounded_point = round(point[0], 1)
                max_vertical = max(rounded_point, max_vertical)
                min_vertical = min(rounded_point, min_vertical)
            if point[1]:
                rounded_point = round(point[1], 1)
                max_horizontal = max(rounded_point, max_horizontal)
                min_horizontal = min(rounded_point, min_horizontal)

        # Horizontal grid (vertical grid lines)
        grid_step_horizontal = 1
        while max_horizontal / grid_step_horizontal > 30:
            grid_step_horizontal *= 10
        max_horizontal = grid_step_horizontal * math.ceil(float(max_horizontal) / grid_step_horizontal)
        scale_horizontal = (width - 20) / max_horizontal
        grid_num = 0
        while grid_num <= max_horizontal / grid_step_horizontal:
            line_x = start_x + scale_horizontal * grid_num * grid_step_horizontal
            draw.line([line_x, start_y, line_x, start_y - height], grid_lines_color, 1)
            grid_num += 1

        # Vertical grid (horizontal grid lines)
        grid_step_vertical = 1
        while (max_vertical - min_vertical) / grid_step_vertical > 30:
            grid_step_vertical *= 10
        max_vertical = grid_step_vertical * math.ceil(float(max_vertical) / grid_step_vertical)
        min_vertical = grid_step_vertical * math.floor(float(min_vertical) / grid_step_vertical)
        range_vertical = max_vertical - min_vertical
        scale_vertical = (height - 20) / range_vertical

        grid_num = 0
        while grid_num <= range_vertical / grid_step_vertical:
            grid_y = min_vertical + grid_num * grid_step_vertical
            line_y = start_y - scale_vertical * (grid_y - min_vertical)
            draw.line([start_x, line_y, start_x + width, line_y], grid_lines_color, 1)
            draw.text([start_x - 4, line_y], str(grid_y), fill=black, anchor="rm")
            grid_num += 1

        # Horizontal axis
        horizontal_axis_y = start_y + scale_vertical * min_vertical
        draw.line([start_x, horizontal_axis_y, start_x + width, horizontal_axis_y], black, 2)
        draw.line([start_x + width, horizontal_axis_y, start_x + width - 8, horizontal_axis_y - 4], black, 2)
        draw.line([start_x + width, horizontal_axis_y, start_x + width - 8, horizontal_axis_y + 4], black, 2)

        # Vertical axis
        draw.line([start_x, start_y, start_x, start_y - height], black, 2)
        draw.line([start_x, start_y - height, start_x + 4, start_y - height + 8], black, 2)
        draw.line([start_x, start_y - height, start_x - 4, start_y - height + 8], black, 2)

        prev_xy = None
        for data_point in data_series:
            if data_point[0] and data_point[1]:
                this_xy = [start_x + data_point[1] * scale_horizontal, start_y - (data_point[0] - min_vertical) * scale_vertical]
            else:
                this_xy = None
            if prev_xy and this_xy:
                draw.line([prev_xy[0], prev_xy[1], this_xy[0], this_xy[1]], data_line_color, 2)
            prev_xy = this_xy

        # Axis labels
        draw.text([start_x + width, horizontal_axis_y - 8], horizontal_axis_label, fill=black, anchor="rs")
        grid_num = 0
        while grid_num <= max_horizontal / grid_step_horizontal:
            line_x = start_x + scale_horizontal * grid_num * grid_step_horizontal
            draw.text([line_x, horizontal_axis_y + 6], str(grid_num * grid_step_horizontal), fill=black, anchor="mt")
            grid_num += 1

        draw.text([start_x + 12, start_y - height], vertical_axis_label, fill=black, anchor="ls")

    img.save(output_filename, "PNG")