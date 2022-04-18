from camera import img_threshold

# prints hsv color of pixel in the center of the screen
def print_center_color(turtle):
    hsv = turtle.get_hsv_image()
    shape = hsv.shape
    center = [int(shape[0]/2), int(shape[1]/2)]
    print("hsv color of screen-center pixel: " + str(hsv[center[0], center[1]]))

# prints hsv color of centroid of first segment from [sticks]
def print_segment_color(turtle, sticks):
    if sticks.count > 0:
        hsv = turtle.get_hsv_image()
        bin = img_threshold(hsv, turtle.detect)

        params = sticks.params[0]
        centroid = [int(sticks.centroids[0][0]), int(sticks.centroids[0][1])]

        #center_coords = [int(params[0]) + int(params[2]/2), int(params[1]) + int(params[3]/2)]
        #center_color = hsv[center_coords[0], center_coords[1]]
        #center_bool = bin[center_coords[0], center_coords[1]]

        center_color = hsv[centroid[1], centroid[0]]
        center_bool = bin[centroid[1], centroid[0]]

        print("Centroid 0 coords: " + str(centroid) + ", hsv color: " + str(center_color) + ", bool: " + str(center_bool))

def rotate_detected_color(turtle):
    if turtle.detect == 0:
        turtle.set_detect(1)
    elif turtle.detect == 1:
        turtle.set_detect(2)
    elif turtle.detect == 2:
        turtle.set_detect(0)
    
