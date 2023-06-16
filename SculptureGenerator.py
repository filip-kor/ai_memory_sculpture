import cadquery as cq
import math
import random

# Set the parameters
p_num = 50 # Number of points to deviate the bottom base
r = 60.0 # The model's radius
h = 60.0 # The height of the entire model

class SculptureGenerator():
    """
    Class for generating 3D sculptures based on audio and emotion input.
    """

    def __init__(self):
        """
        Constructor method for SculptureGenerator class.

        Initializes the object's attributes:
            old_center: tuple, stores the previous center point of the sculpture
            cur_h: float, stores the current height of the sculpture
            recent_points: list, stores the previous generated points of the sculpture
            response: list, stores the emotion input as a list of dictionaries
        """

        self.old_center = (0.0, 0.0)
        self.cur_h = 0.0
        self.recent_points = []
        self.response = []

    def gen_waveform_base(self, p_num, r, h, audio_array, rand_base=False, skip_p=None):
        """
        Method that generates the bottom part of the sculpture with the waveform curvature.

        Parameters:
            p_num: the number of points used to create the bottom part of the sculpture
            r: the radius of the bottom part of the sculpture
            h: the height of the sculpture
            audio_array: array of audio data
            rand_base: boolean indicating whether to use a random array instead of the audio waveform
            skip_p: number of points to skip in the waveform

        Returns:
            bot: the bottom part of the sculpture
        """

        # Use a random array instead of the audio waveform if necessary
        if rand_base:
            print("Unable to produce the base using waveform, generating with random numbers...")
            audio_array = [round(random.uniform(-0.04, 0.04), 4) for _ in range(p_num)]
            r = random.random()
            if r <= (1/3):
                skip_p = None
            elif r <= (2/3):
                skip_p = 1
            else:
                skip_p = 2
        
        # Create a set of points that deviate the bottom base circle according to the waveform
        points = []
        for n in range(p_num):
            deviation = audio_array[n]
            new_point = ((1+deviation)*r*math.cos((n+1)*2*math.pi/p_num)-r, \
                (1+deviation)*r*math.sin((n+1)*2*math.pi/p_num))
            points.append(new_point)

        if skip_p is not None:
            points = points[:-skip_p]

        # Create the bottom part of the model
        bot = (
            cq.Workplane("XY").spline(points, tol=r*0.005).close()
            .workplane(offset=h/2)
            .move(-r,0)
            .circle(r)
            .loft(combine=True)
            .edges(">Z").fillet(r*0.2)
        )

        self.cur_h = h/2

        return bot

    def set_params(self, response, diameter_limit):
        """
        Set the parameters for the 3D model based on the response and diameter limit.

        Args:
            response: a list of dictionaries, each dictionary represents an emotion detected.
            diameter_limit: a float number represents the diameter limit.

        Returns:
            layer_list: a list of dictionaries, each dictionary represents a layer of the 3D model.
        """

        bot_limit = r*0.19
        top_limit = r*diameter_limit
        layer_list = []

        prev_emotion = None
        t2_symmetry = False

        bot_fillet = False

        satisfied_index = [el['class_name'] for el in response].index('satisfied')

        for i, emotion in enumerate(response):

            # Change bot_fillet based on the satisfaction position and confidence
            if satisfied_index < 3 and response[satisfied_index]['confidence'] > .15 and prev_emotion and prev_emotion['class_name'] != 'frustrated':
                bot_fillet = True
            else:
                bot_fillet = False

            # Satisfaction cannot be used in the third layer because of high deviation
            if (emotion['class_name'] == 'satisfied') and t2_symmetry:
                if i == 2: return layer_list
                emotion = response[0]

            # Significantly stronger (0.3 absolute) emotion overwrites the lower level emotion
            if (i != 0) and ((prev_emotion['confidence'] - emotion['confidence'] > .3) or (emotion['confidence'] < .15)):
                emotion = response[0]

            # Set layer parameters for frustration
            if emotion['class_name'] == 'frustrated':

                if satisfied_index < 3 and response[satisfied_index]['confidence'] > .15:
                    t2_symmetry = True

                radius = r*0.63

                polygon_range = (3, 6)

                if emotion['confidence'] >= .8: # emotion confidence defines the number of extruded shapes
                    points_num = 13
                elif emotion['confidence'] >= .65:
                    points_num = 12
                elif emotion['confidence'] >= .5:
                    points_num = 11
                else:
                    points_num = 10

                layer_list.append({
                        "type": 2,
                        "confidence": emotion['confidence'],
                        "points_num": points_num//(i+1) if i < 2 else 1,
                        "radius": radius-r*i*.27 if i < 2 else None,
                        "polygon_range": polygon_range,
                        "deviation_range": 0,
                        "symmetry": t2_symmetry
                    })
                # print('add:', emotion)
                if layer_list[-1]['points_num'] == 1: return layer_list

            # Set layer parameters for excitement
            elif emotion['class_name'] == 'excited':

                satisfied_index = [el['class_name'] for el in response].index('satisfied')
                if satisfied_index < 3 and response[satisfied_index]['confidence'] > .15:
                    t2_symmetry = True

                radius = r*0.63

                if emotion['confidence'] >= .8: # emotion confidence defines the number of extruded shapes
                    points_num = 13
                elif emotion['confidence'] >= .65:
                    points_num = 12
                elif emotion['confidence'] >= .5:
                    points_num = 11
                else:
                    points_num = 10

                layer_list.append({
                        "type": 2,
                        "confidence": emotion['confidence'],
                        "points_num": points_num//(i+1) if i < 2 else 1,
                        "radius": radius-r*i*.27 if i < 2 else None,
                        "polygon_range": None,
                        "deviation_range": 0,
                        "symmetry": t2_symmetry
                    })
                # print('add:', emotion)
                if layer_list[-1]['points_num'] == 1: return layer_list

            # Set layer parameters for sadness
            elif emotion['class_name'] == 'sad':

                poly_points_num = random.randint(17,35)
                if emotion["confidence"] > 0.5:
                    poly_points_num *= 1 + round(emotion["confidence"]/4)

                if top_limit-r*i*.15 < bot_limit: return layer_list
                layer_list.append({
                        "type": 1,
                        "confidence": emotion['confidence'],
                        "points_num": poly_points_num-i*2,
                        "radius": top_limit-r*i*.15 if ((i < 2) or (not prev_emotion or (prev_emotion['class_name'] not in ['excited', 'frustrated'])) and (i < 2)) else r*0.15,
                        "edge_fillet": 0.0,
                        "vertex_fillet": 0.0,
                        "deviation_range": 1.0,
                        "symmetry": False,
                        "bot_fillet": bot_fillet if i > 0 else False
                    })
                # print('add:', emotion)
            
            # Set layer parameters for sympathy
            elif emotion['class_name'] == 'sympathetic':
                poly_points_num = random.randint(10,25)
                if (top_limit-r*i*.15 < bot_limit): return layer_list
                layer_list.append({
                        "type": 1,
                        "confidence": emotion['confidence'],
                        "points_num": poly_points_num-i*2,
                        "radius": top_limit-r*i*.15 if ((i < 2) or (not prev_emotion or (prev_emotion['class_name'] not in ['excited', 'frustrated'])) and (i < 2)) else r*0.15,
                        "edge_fillet": r*0.1,
                        "vertex_fillet": r*0.1,
                        "deviation_range": 1.0,
                        "symmetry": False,
                        "bot_fillet": bot_fillet
                    })
                # print('add:', emotion)
                
            # Set layer parameters for satisfaction
            elif emotion['class_name'] == 'satisfied':
                if top_limit-r*i*.2 < bot_limit: return layer_list
                poly_points_num = random.randint(12,15)
                layer_list.append({
                        "type": 1,
                        "confidence": emotion['confidence'],
                        "points_num": poly_points_num-i*3,
                        "radius": top_limit-r*i*.2,
                        "edge_fillet": r*0.1,
                        "vertex_fillet": r*0.2,
                        "deviation_range": 2.2,
                        "symmetry": True,
                        "bot_fillet": bot_fillet
                    })
                t2_symmetry = True
                # print('add:', emotion)

            prev_emotion = emotion

            if len(layer_list) == 3:
                break
            
        return layer_list

    def get_polygon_points(self, polygon_p_num, pol_r, deviation_arr, symmetry=False):
        """
        Returns a list of points representing a regular polygon with optional deformations with n points and given radius and deviation.

        Args:
            polygon_p_num (int): The number of points of the regular polygon.
            pol_r (float): The radius of the regular polygon.
            deviation_arr (List[float]): A list of deviations for each point of the polygon.
            symmetry (bool): A boolean indicating whether the polygon is symmetrical or not.

        Returns:
            polygon_pts: A list of points representing the regular polygon.
        """

        polygon_pts = []

        if symmetry:
            pts_tomap = []
            temp = None
            c = 0

            # Create the list of points using the circle equation
            for n in range(polygon_p_num):
                deviation = deviation_arr[n]
                new_point = ((1+deviation)*pol_r*math.cos((n+1)*2*math.pi/polygon_p_num)-r, \
                    (1+deviation)*pol_r*math.sin((n+1)*2*math.pi/polygon_p_num))
                c+=1
                
                # Add relevant points to the array
                if new_point[1] >= -r/20 and c == 1:
                    polygon_pts.append(new_point)
                    c-=1
                    if new_point[1] >= r/20:
                        pts_tomap.append(new_point)
                elif new_point[1] >= -r/20 and c >= 1:
                    temp = new_point
            
            # Mirror the array on the other side of Y axis
            pts_tomap = pts_tomap[::-1]
            for point in pts_tomap:
                (x,y) = point
                polygon_pts.append((x,-y))
            
            if temp:
                polygon_pts.append(temp)

        else:
            # Create the list of points using the circle equation
            for n in range(polygon_p_num):
                deviation = deviation_arr[n]
                new_point = ((1+deviation)*pol_r*math.cos((n+1)*2*math.pi/polygon_p_num)-r, \
                    (1+deviation)*pol_r*math.sin((n+1)*2*math.pi/polygon_p_num))
                polygon_pts.append(new_point)

        # Move the points if deviation affected the centre of mass
        mean_x = sum([el[0] for el in polygon_pts])/len(polygon_pts)
        mean_y = sum([el[1] for el in polygon_pts])/len(polygon_pts)

        shift_x = -r - mean_x
        shift_y = -mean_y

        polygon_pts = [(point[0]+shift_x, point[1]+shift_y) for point in polygon_pts]

        return polygon_pts

    def gen_circular_type2_layer(self, res, points, sizes, heights, n, prev_layer):
        """
        Generates a circular type-2 layer given a list of points, sizes, heights, and a previous layer.

        Args:
            res (cq.Workplane): The workplane to operate on.
            points (List[Tuple[float, float]]): A list of points where to place the circles.
            sizes (List[float]): A list of radii for each circle.
            heights (List[float]): A list of heights for each circle.
            n (int): The current layer number.
            prev_layer (Dict[str, Any]): A dictionary representing the previous layer.

        Returns:
            res: The CadQuery model with the generated layer.
        """

        b_h = self.cur_h

        for m, point in enumerate(points):
            circle_r = sizes[m]
            ex_h = heights[m] + h*n/20

            # Put a new prism on the bottom surface
            res = (
                res
                .faces(cq.selectors.NearestToPointSelector((-r, 0, h/2)))
                .center(point[0]-self.old_center[0], point[1]-self.old_center[1])
                .circle(circle_r)
                .extrude((b_h-h/2) + ex_h)
                .faces(cq.selectors.NearestToPointSelector((point[0], point[1], b_h+ex_h)))
                .fillet(circle_r)
            )
            
            self.old_center = (point[0], point[1])

        # Apply smoothing to the bottom surface if possible
        if prev_layer and not ((prev_layer['type'] == 2) and prev_layer['polygon_range'] != None) and not ((prev_layer['type'] == 1) and prev_layer['edge_fillet'] != 0):
            res = res.faces(cq.selectors.NearestToPointSelector((-r,0,self.cur_h))).fillet(r*0.009)

        return res

    def gen_spiky_type2_layer(self, res, points, polygon_range, sizes, heights, n):
        """
        Generates a spiky type-2 layer given a list of points, a range of polygon points, sizes, heights, and the current layer number.

        Args:
            res (cq.Workplane): The workplane to operate on.
            points (List[Tuple[float, float]]): A list of points where to place the polygons.
            polygon_range (Tuple[int, int]): A tuple with the minimum and maximum number of points for the polygons.
            sizes (List[float]): A list of radii for each polygon.
            heights (List[float]): A list of heights for each polygon.
            n (int): The current layer number.

        Returns:
            res: The resulting CadQuery model with the generated layer.
        """

        b_h = self.cur_h

        for m, point in enumerate(points):
            circle_r = sizes[m]
            ex_h = heights[m] + h*n/20

            polygon_pts_num = random.randint(polygon_range[0], polygon_range[1])
            polygon_pts = [(point[0]+r, point[1]) for point in self.get_polygon_points(polygon_pts_num, circle_r, [0.0 for _ in range(polygon_pts_num)], False)]
            
            polygon_sketch = (
                cq.Sketch()
                .polygon(polygon_pts, tag='face')
            )

            # Put a new spiky prism on the bottom surface
            res = (
                res.faces(cq.selectors.NearestToPointSelector((-r,0,b_h)))
                .workplane()
                .center(point[0]-self.old_center[0], point[1]-self.old_center[1])
                .placeSketch(polygon_sketch)
                .extrude(0.0001)
                .faces(cq.selectors.NearestToPointSelector((point[0],point[1],b_h+0.0001)))
                .wires(">Z")
                .toPending()
                .workplane(offset=ex_h)
                .circle(0.0001)
                .workplane(offset=-ex_h)
                .loft(combine=True)
            )
            
            self.old_center = (point[0], point[1])

        return res

    def gen_type1(self, res, layer, i, prev_layer, last_layer = False):
        """
        Generates a type-1 layer given a dictionary representing the layer, the current index, the previous layer, and a boolean indicating whether this is the last layer.

        Args:
            res (cq.Workplane): The workplane to operate on.
            layer (Dict[str, Any]): A dictionary representing the layer.
            i (int): The current layer index.
            prev_layer (Dict[str, Any]): A dictionary representing the previous layer.
            last_layer (bool): A boolean indicating whether this is the last layer.

        Returns:
            res: The CadQuery model with the generated layer.
        """

        deviation_arr = [random.uniform(0,layer['deviation_range']*0.3) if layer['deviation_range'] != 0 else 0 for n in range(layer["points_num"])]
        polygon_pts = self.get_polygon_points(layer["points_num"], layer["radius"], deviation_arr, layer['symmetry'])

        # Prepare the base polygon
        plane = (
            cq.Sketch()
            .polygon(polygon_pts, tag='face')
        )

        if layer['vertex_fillet'] != 0:
            plane = (
                plane 
                .edges('%LINE',tag='face')
                .vertices()
                .fillet(layer['vertex_fillet'])
            )

        # Extrude the polygon with smoothing if required
        if last_layer and layer['edge_fillet'] != 0:

            ex_h = (h/(3*(i+1)))

            if layer["confidence"] > 0.5:
                ex_h *= 1 + layer["confidence"]/4.0
            
            res = (
                res
                .faces(cq.selectors.NearestToPointSelector((-r,0,self.cur_h)))
                .workplane().center(0.0-self.old_center[0], 0.0-self.old_center[1])
                .placeSketch(plane)
                .extrude(0.0001)
                .faces(cq.selectors.NearestToPointSelector((-r,0,self.cur_h+0.0001)))
                .wires('>Z')
                .toPending()
                .workplane(offset=ex_h)
                .move(-r,0)
                .circle(layer["radius"])
                .loft(combine=True, ruled=False)
                .faces(cq.selectors.NearestToPointSelector((-r,0,self.cur_h+0.0001+ex_h)))
                .edges('>Z').fillet(layer["radius"]*1/((i+1)))
            )

            # Apply smoothing to the bottom surface if possible
            if layer['bot_fillet'] and not (prev_layer and (prev_layer['type'] == 2)):
                res = res.faces(cq.selectors.NearestToPointSelector((-r,0,self.cur_h))).fillet(h/(20*((i+1))))

            self.cur_h += 0.0001+ex_h
        
        # Extrude the polygon without smoothing
        else:

            ex_h = h/(6*(i+1))

            if layer["confidence"] > 0.5:
                ex_h *= 1+(layer["confidence"]/4.0)

            res = (
                res
                .faces(cq.selectors.NearestToPointSelector((-r,0,self.cur_h))) 
                .workplane().center(0.0-self.old_center[0], 0.0-self.old_center[1])
                .placeSketch(plane)
                .extrude(ex_h)
            )

            if (layer['bot_fillet']) and (prev_layer['type'] != 2):
                res = res.faces(cq.selectors.NearestToPointSelector((-r,0,self.cur_h))).fillet(h/(12*((i+1))))

            self.cur_h += ex_h

            if layer['edge_fillet'] != 0:
                res = (
                    res
                    .faces(cq.selectors.NearestToPointSelector((-r,0,self.cur_h+0.0001)))
                    .edges('>Z').fillet(layer['edge_fillet']/(i+1))
                )
        
        self.old_center = (0.0, 0.0)
        self.recent_points = polygon_pts

        return res

    def gen_type2(self, res, layer, i, prev_layer):
        """Generates a type 2 layer based on the given layer information.

        Args:
            res (cq.Workplane): The initial model to start with.
            layer (dict): A dictionary containing information about the layer to generate.
            i (int): The index of the current layer.
            prev_layer (dict): A dictionary containing information about the previous layer.

        Returns:
            res: The CadQuery model with the new layer.
        """

        b_h = self.cur_h

        # If it's not the last layer of the sculpture
        if layer['points_num'] > 1:

            heights = [h*round(random.uniform(0.1401, max((0.3/0.6)*layer['confidence'],0.15)), 4) for _ in range(layer['points_num'])]  # emotion confidence defines the height range
            sizes = [r*random.uniform(0.08, 0.14) for _ in range(layer['points_num'])]

            # Apply symmetry if necessary
            if layer['symmetry'] == True:
                # Heights and sizes are symmetrical
                for n in range(layer['points_num']//2):
                    heights[layer['points_num']-2-n] = heights[n]
                    sizes[layer['points_num']-2-n] = sizes[n]

            deviation_arr = [random.uniform(0,layer['deviation_range']*0.3) if layer['deviation_range'] != 0 else 0 for n in range(layer["points_num"])]
            points = self.get_polygon_points(layer['points_num'], layer['radius'], deviation_arr, layer['symmetry'])

            # Call the relevant modelling function
            if layer['polygon_range'] == None:
                res = self.gen_circular_type2_layer(res, points, sizes, heights, i, prev_layer)

            else:
                res = self.gen_spiky_type2_layer(res, points, layer['polygon_range'], sizes, heights, i)
        
        # If it's the last layer of the sculpture
        else:

            # If the base is circular
            if layer['polygon_range'] == None:
                if b_h == h/2:
                    circle_r = r*random.uniform(0.1, 0.18)
                    ex_h = round(h*random.uniform(0.1401, max((0.3/0.6)*layer['confidence'],0.15)), 4) + h*6/35
                else:
                    circle_r = r*0.12
                    ex_h = h*0.2

                # Put one hemispheric prism in the middle
                res = (
                    res
                    .faces(cq.selectors.NearestToPointSelector((-r,0,h/2)))
                    .center(-self.old_center[0]-r, -self.old_center[1])
                    .circle(circle_r)
                    .extrude((b_h-h/2) + ex_h)
                    .faces(cq.selectors.NearestToPointSelector((-r,0.0,b_h+ex_h)))
                    .fillet(circle_r)
                )
            
            # If the base is a polygon
            else:
                circle_r = r*random.uniform(0.1, 0.18)
                ex_h = round(h*random.uniform(0.1401, max((0.3/0.6)*layer['confidence'],0.15)), 4) + h*6/35

                polygon_pts_num = random.randint(layer['polygon_range'][0], layer['polygon_range'][1])
                polygon_pts = [(point[0]+r, point[1]) for point in self.get_polygon_points(polygon_pts_num, circle_r, [0.0 for _ in range(polygon_pts_num)], False)]

                polygon_sketch = (
                    cq.Sketch()
                    .polygon(polygon_pts, tag='face')
                )

                # Put one spiky prism in the middle
                res = (
                    res
                    .faces(cq.selectors.NearestToPointSelector((-r,0,b_h)))
                    .workplane()
                    .center(-self.old_center[0]-r, -self.old_center[1])
                    .placeSketch(polygon_sketch)
                    .extrude(0.0001)
                    .faces(cq.selectors.NearestToPointSelector((-r,0.0,b_h+0.0001)))
                    .wires(cq.selectors.NearestToPointSelector((-r,0.0,b_h+0.0001)))
                    .toPending()
                    .workplane(offset=ex_h)
                    .circle(0.0001)
                    .workplane(offset=-ex_h)
                    .loft(combine=True)
                )

        return res

    def shape_top(self, bot, response):
        """
        Method for generating the top part of the sculpture.

        Args:
            bot: the bottom part of the sculpture as a CadQuery object
            response: list, the emotion input as a list of dictionaries

        Returns:
            res: the entire sculpture as a CadQuery object
        """

        res = bot

        # Set the layer parameters
        layer_list = self.set_params(response, 0.5)
        last_layer = False
        prev_layer = None

        # Call the relevant function for each layer
        for i, layer in enumerate(layer_list):
            print(layer)

            if i == len(layer_list) - 1:
                last_layer = True

            if layer['type'] == 1 :
                res = self.gen_type1(res, layer, i, prev_layer, last_layer)
            elif layer['type'] == 2:
                res = self.gen_type2(res, layer, i, prev_layer)
            
            prev_layer = layer

        return res

    def generate(self, response, audio_array):
        """
        Method for generating a 3D sculpture based on audio array and emotions from Tone Analytics tool.

        Args:
            response: list, the emotion input as a list of dictionaries
            audio_array: numpy array, the processed audio input as a numpy array

        Returns:
            result: the generated 3D sculpture as a CadQuery object
        """

        # -- Create the bottom part of the sculpture with the waveform curvature. Skip the last audio array elements or generate a random array on failure.
        fail_count = 0

        bot = None
        while bot is None:
            try:
                if fail_count == 1:
                    bot = self.gen_waveform_base(p_num, r, h, audio_array, skip_p=1)
                elif fail_count == 2:
                    bot = self.gen_waveform_base(p_num, r, h, audio_array, skip_p=2)
                elif fail_count >= 3:
                    bot = self.gen_waveform_base(p_num, r, h, audio_array, rand_base=True)
                else:
                    bot = self.gen_waveform_base(p_num, r, h, audio_array)
            except:
                fail_count += 1

        # -- Add the top model depending on the emotion

        # Stochastic elements make the function throw ValueError in some cases
        fail_count = 0

        top = None
        while top is None:
            try:
                print(response)
                if (fail_count >= 7) and (fail_count < 14): # remove the last array point if failed 7 times
                    bot = self.gen_waveform_base(p_num, r, h, audio_array, skip_p=1)
                elif (fail_count >= 14) and (fail_count < 21): # remove the 2 last array points if failed 14 times
                    bot = self.gen_waveform_base(p_num, r, h, audio_array, skip_p=2)
                elif fail_count >= 21: # generate a random array if failed 21 times
                    bot = self.gen_waveform_base(p_num, r, h, audio_array, rand_base=True)
                top = self.shape_top(bot, response)
            except:
                self.old_center = (0.0, 0.0)
                self.cur_h = h/2
                self.recent_points = []
                print('Incompatible layers, regenerating...')
                fail_count += 1

        result = top

        return result