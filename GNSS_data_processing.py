import time
import numpy as np
from GNSS_data_input import GNSSDataSourceFactory as data_input
from vpython import scene, vector, arrow, box, color, label, cross, cos, sin

TO_RAD = 2*np.pi/360

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


def plot_module(point: tuple, direction: str) -> None:
    """
    Update the 3D plot of the GNSS module with its orientation.

    Args:
        point (tuple): A tuple containing GNSS data (time, x, y, roll_deg, pitch_deg).
        direction (str): The movement direction of the module (Forward, Left, Right).
                       : Direction is defined by the difference between the current and last headings. 
                       : If difference is positive, module is moving right. If negative, module is moving left.
                       : If difference is 0, then module is moving forward.

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
    direction_text.text = f"Direction: {direction}"


def main():
    # Get the data source and the data
    data_source = data_input.create_data_source(data_source_type, file_path)
    gnss_data = data_source.read_data()
    
    if gnss_data:
        past_point = None
        past_heading = None
        direction = None

        # In this case, since we're using a filel we get all data at once
        for current_point in gnss_data:                
            start_time = time.time()

            # Only process if we have at least 2 points
            if past_point is not None:
                heading = calculate_heading(past_point=past_point, current_point=current_point) 
                
                if past_heading is not None:
                    direction = "Forward" if past_heading - heading == 0 else ("Left" if past_heading - heading < 0 else "Right")
                
                past_heading = heading                
                plot_module(current_point, direction)

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
    direction_text = label(pos=vector(-10, 24, 0), text="Direction: Undefined", height=16, color=color.white)

    try:
        main()
    except Exception as e:
        print(e)