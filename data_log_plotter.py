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
        max_vertical = 1
        for point in data_series:
            max_vertical = max(point[0], max_vertical)
            max_horizontal = max(point[1], max_horizontal)

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
            draw.text([line_x, start_y + 6], str(grid_num * grid_step_horizontal), fill=black, anchor="mt")
            grid_num += 1

        # Vertical grid (horizontal grid lines)
        grid_step_vertical = 1
        while max_vertical / grid_step_vertical > 30:
            grid_step_vertical *= 10
        max_vertical = grid_step_vertical * math.ceil(float(max_vertical) / grid_step_vertical)
        scale_vertical = (height - 20) / max_vertical
        grid_num = 0
        while grid_num <= max_vertical / grid_step_vertical:
            line_y = start_y - scale_vertical * grid_num * grid_step_vertical
            draw.line([start_x, line_y, start_x + width, line_y], grid_lines_color, 1)
            # TODO: figure out why the anchor doesn't work
            draw.text([start_x - 4, line_y], str(grid_num * grid_step_vertical), fill=black, anchor="rm") 
            grid_num += 1

        # Horizontal axis
        draw.line([start_x, start_y, start_x + width, start_y], black, 2)
        draw.line([start_x + width, start_y, start_x + width - 8, start_y - 4], black, 2)
        draw.line([start_x + width, start_y, start_x + width - 8, start_y + 4], black, 2)

        # Vertical axis
        draw.line([start_x, start_y, start_x, start_y - height], black, 2)
        draw.line([start_x, start_y - height, start_x + 4, start_y - height + 8], black, 2)
        draw.line([start_x, start_y - height, start_x - 4, start_y - height + 8], black, 2)

        prev_xy = None
        for data_point in data_series:
            this_xy = [start_x + data_point[1] * scale_horizontal, start_y - data_point[0] * scale_vertical]
            if prev_xy:
                draw.line([prev_xy[0], prev_xy[1], this_xy[0], this_xy[1]], data_line_color, 2)
            prev_xy = this_xy

        # Axis labels
        draw.text([start_x + width, start_y - 8], horizontal_axis_label, fill=black, anchor="rs")
        draw.text([start_x + 12, start_y - height], vertical_axis_label, fill=black, anchor="ls")

    img.save(output_filename, "PNG")