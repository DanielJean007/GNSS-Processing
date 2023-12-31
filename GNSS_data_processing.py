import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from GNSS_data_input import GNSSDataSourceFactory as data_input
from vpython import scene, vector, arrow, box, color, label, cross, cos, sin

TO_RAD = 2*np.pi/360

# Initialize lists to store data for 2D plotting
time_points = []
x_projected_points = []
y_projected_points = []
heading_deg_points = []


def calculate_projection(gnss_point: tuple) -> tuple:
    """
    Calculate the projection of a GNSS point onto a plane.

    Args:
        gnss_point (tuple): A tuple containing GNSS data (time, x, y, roll_deg, pitch_deg).

    Returns:
        tuple: A tuple containing time, projected_x, and projected_y.
    """
    time, x, y, roll_deg, pitch_deg = gnss_point

    # Convert roll and pitch to radians
    roll_rad = np.deg2rad(roll_deg)
    pitch_rad = np.deg2rad(pitch_deg)

    # Define the GNSS module height above the moving plane
    gnss_height = 1500

    # Calculate the projection
    projected_x = x + gnss_height * np.tan(pitch_rad)
    projected_y = y + gnss_height * np.tan(roll_rad)

    return time, projected_x, projected_y


def calculate_heading(past_point: tuple, current_point: tuple) -> float:
    """
    Calculate the heading (angle in radians) between two GNSS points.

    Args:
        past_point (tuple): A tuple representing the previous GNSS point.
        current_point (tuple): A tuple representing the current GNSS point.

    Returns:
    """
    heading_rad = None

    x1, y1 = past_point[1], past_point[2]
    x2, y2 = current_point[1], current_point[2]

    # Calculate the change in position
    delta_x = x2 - x1
    delta_y = y2 - y1

    # Calculate the heading (angle in radians)
    heading_rad = np.arctan2(delta_y, delta_x)

    return heading_rad


def update_plot_2D(frame, gnss_data, x_min, x_max, y_min, y_max):
    point = gnss_data[frame]

    if frame > 0:
        past_point = gnss_data[frame - 1]
    else:
        past_point = point

    projected_point = calculate_projection(point)
    x_projected, y_projected = projected_point[1], projected_point[2]

    heading = calculate_heading(past_point, point)
    heading_deg = np.rad2deg(heading)

    time_points.append(point[0])
    x_projected_points.append(x_projected)
    y_projected_points.append(y_projected)
    heading_deg_points.append(heading_deg)

    plt.clf()

    # Create a plot for projections
    plt.plot(x_projected_points, y_projected_points, 'bo-', lw=1)  # Added line plot
    plt.title('Projection With Respect to the Origin (X=0, Y=0)')
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # Print the most recent heading value as text on the plot
    latest_heading = heading_deg_points[-1]
    direction = "Moving "
    direction += "Forward" if latest_heading == 90 else "Left" if latest_heading > 90 and latest_heading < 270 else "Right"
    direction += f" ({latest_heading:.2f}°)"
    plt.text(x_projected_points[-1], y_projected_points[-1], f' {direction}', fontsize=12, color='red')

    plt.tight_layout()


def update_plot_3D(point: tuple, direction_relative: str, direction_absolute: str) -> None:
    """
    Update the 3D plot of the GNSS module with its orientation.

    Args:
        point (tuple): A tuple containing GNSS data (time, x, y, roll_deg, pitch_deg).
        direction_relative (str): The movement direction relative the last position of the module (Forward, Left, Right).
                       : Direction here is defined by the difference between the current and last headings. 
                       : If difference is positive, module is moving right. If negative, module is moving left.
                       : If difference is 0, then module is moving forward.
        direction_absolute (str): The movement direction relative the origin (X=0, Y=0).

    Returns:
        None
    """
    roll = (point[3]) * TO_RAD
    pitch = (point[4]) * TO_RAD

    k = vector(cos(roll), sin(pitch), sin(roll))
    y = vector(0, 1, 0)
    s = cross(k, y)
    v = cross(s, k)

    xarrow.axis = k
    zarrow.axis = s
    yarrow.axis = v
    module.axis = k
    module.up = v
    xarrow.length = 1
    yarrow.length = -1.5
    zarrow.length = 2

    roll_text.text = f"Roll: {point[3]:.2f}°"
    pitch_text.text = f"Pitch: {point[4]:.2f}°"
    xy_text.text = f"X: {point[1]:.2f}mm, Y: {point[2]:.2f}mm"
    direction_relative_text.text = f"Relative Direction: {direction_relative}"
    direction_absolute_text.text = f"Absolute Direction: {direction_absolute}"


def plot_2D(gnss_data):
    x_min = min([x[1] for x in gnss_data]) - 100
    x_max = max([x[1] for x in gnss_data]) + 200
    y_min = min([y[2] for y in gnss_data]) - 100
    y_max = max([y[2] for y in gnss_data]) + 200
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    plt.xlim(x_min, x_max)  # Set x-axis limits
    plt.ylim(y_min, y_max)  # Set y-axis limits

    ani = FuncAnimation(fig, update_plot_2D, fargs=(gnss_data, x_min, x_max, y_min, y_max), frames=len(gnss_data), repeat=False)
    plt.show()


def plot_3D(gnss_data):
    if gnss_data:
        past_point = None
        past_heading = None
        direction_relative = None
        direction_absolute = None

        # In this case, since we're using a filel we get all data at once
        for current_point in gnss_data:                
            start_time = time.time()

            # Only process if we have at least 2 points
            if past_point is not None:
                heading = calculate_heading(past_point=past_point, current_point=current_point) 
                
                if past_heading is not None:
                    relative_heading = past_heading - heading
                    relative_heading_deg = np.rad2deg(relative_heading)
                    direction_relative = "Forward" if relative_heading_deg == 0 else "Left" if relative_heading_deg < 0 else "Right"
                    direction_relative += f" {relative_heading_deg:.2f}° (relative to the last position)"

                    heading_deg = np.rad2deg(heading)
                    direction_absolute = "Forward" if heading_deg == 90 else "Left" if heading_deg > 90 and heading_deg < 270 else "Right"
                    direction_absolute += f" {heading_deg:.2f}°"
                
                past_heading = heading                
                update_plot_3D(current_point, direction_relative, direction_absolute)

            past_point = current_point
            # MOCK receiving data from stream. In our case, there are 4 readings per second
            time.sleep(max(0, (1/readings_per_second) - (time.time() - start_time)))
    else:
        # No data, exit application
        exit(-1)


if __name__ == "__main__":
    readings_per_second = 4
    data_source_type = "File"  # Change this to "UART" or "USB" for other source types
    file_path = "gnss_data.txt"  # Specify the file path if using "File" source

    # For plot
    scene.range = 2
    scene.forward = vector(-1, 1, 0)
    scene.width = 700
    scene.height = 600

    xarrow = arrow(length=1, shaftwidth=0.1, color=color.red, axis=vector(1, 0, 0))
    yarrow = arrow(length=1, shaftwidth=0.1, color=color.green, axis=vector(0, 1, 0))
    zarrow = arrow(length=1, shaftwidth=0.1, color=color.blue, axis=vector(0, 0, 1))
    module = box(length=5, width=3, height=2, opacity=0.8, pos=vector(0, 0, 0))
    
    roll_text = label(pos=vector(-10, 34, 20), text="Roll: ", height=16, color=color.white)
    pitch_text = label(pos=vector(-10, 34, 5), text="Pitch: ", height=16, color=color.white)
    xy_text = label(pos=vector(-10, 34, -15), text="X: 0mm, Y: 0mm", height=16, color=color.white)
    direction_relative_text = label(pos=vector(-10, 24, 0), text="Relative Direction: Undefined", height=16, color=color.white)
    direction_absolute_text = label(pos=vector(-10, 28, 0), text="Absolute Direction: Undefined", height=16, color=color.white)

    try:
        # Get the data source and the data
        data_source = data_input.create_data_source(data_source_type, file_path)
        gnss_data = data_source.read_data()
        
        plot_2D(gnss_data)
        plot_3D(gnss_data)
    except Exception as e:
        print(e)