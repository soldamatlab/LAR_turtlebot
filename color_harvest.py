from main import img_threshold

def print_center_color(turtle, sticks):
    if sticks.count > 0:
        params = sticks.params[0]
        hsv = turtle.get_hsv_image()
        bin = img_threshold(hsv)

        center_coords = [int(params[0]) + int(params[2]/2), int(params[1]) + int(params[3]/2)]
        center_color = hsv[center_coords[0], center_coords[1]]
        center_bool = bin[center_coords[0], center_coords[1]]

        print("Centroid 0 coords: " + str(center_coords) + ", hsv color: " + str(center_color) + ", bool: " + str(center_bool))
