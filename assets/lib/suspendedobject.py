import numpy as np
from operator import add 

from ipywidgets import interact, interactive, fixed, interact_manual
from ipywidgets import HBox, VBox, Label, Layout
import ipywidgets as widgets

import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid') # global style for plotting

from IPython.display import IFrame
from IPython.display import set_matplotlib_formats, display, Math, Markdown, Latex, HTML
set_matplotlib_formats('svg')

from bokeh.io import push_notebook, show, output_notebook, curdoc
from bokeh.plotting import figure
from bokeh.models import Legend, ColumnDataSource, Slider, Span, LegendItem
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead, LabelSet
from bokeh.models.glyphs import Wedge, Bezier
from bokeh.layouts import gridplot, row, column

output_notebook(hide_banner=True)

class SuspendedObjectLab:
    """
    This class embeds all the necessary code to create a virtual lab to study the static equilibrium of an object suspended on a clothesline with a counterweight.
    """
    
    def __init__(self, m_object = 3, distance = 5, height = 1.5, x_origin = 0, y_origin = 0):
        '''
        Initiates and displays the virtual lab on suspended objects.
        
        :m_object: mass of the suspended object
        :distance: horizontal distance between the two poles
        :height: height of the poles (same height for both)
        :x_origin: x coordinate of the bottom of the left pole (origin of the coordinate system)
        :y_origin: y coordinate of the bottom of the left pole (origin of the coordinate system)
        '''
        
        ###--- Static parameters of the situation
        self.m_object = m_object # mass of the wet object, in kg
        
        self.distance = distance # distance between the poles, in m
        self.height = height # height of the poles, in m

        self.x_origin = x_origin # x coordinate of point of origin of the figure = x position of the left pole, in m
        self.y_origin = y_origin # y coordinate of point of origin of the figure = y position of the lower point (ground), in m


        # Parameters for drawing forces
        self.gravity = 9.81
        self.force_scaling = .01
        self.forces_nb = 4
        
        # parameters for sliders
        self.alpha_slider_min = 0.5
        self.alpha_slider_max = 30
        self.alpha_degrees = 20 # initial angle

        # parameter to draw the angle
        self.radius=0.3

    
    def launch(self):
        
        ###--- Elements of the ihm:
        # IHM input elements
        self.alpha_slider_label = Label('Angle α (°):', layout=Layout(margin='0px 5px 0px 0px'))
        self.alpha_slider_widget = widgets.FloatSlider(min=self.alpha_slider_min,max=self.alpha_slider_max,step=0.5,value=self.alpha_degrees, layout=Layout(margin='0px'))
        self.alpha_slider_note = Label('[Note: once you have clicked on the slider (the circle becomes blue), you can use the arrows from your keyboard to make it move.]', layout=Layout(margin='0px 0px 15px 0px'))
 
        self.alpha_slider_input = VBox([HBox([self.alpha_slider_label, self.alpha_slider_widget], layout=Layout(margin='0px')), self.alpha_slider_note])

        # Linking widgets to handlers
        self.alpha_slider_widget.observe(self.alpha_slider_event_handler, names='value')


        ###--- Compute variables dependent with alpha
        alpha = degrees_to_radians(self.alpha_degrees)
        alpha_text = '⍺ = {:.2f} °'.format(self.alpha_degrees)
        
        coord_object = self.get_object_coords(alpha)
        height_text =  'h = {:.2f} m'.format(coord_object[1])

        
        ###--- Create the figure ---###
        # LIMITATIONS of Bokeh (BokehJS 1.4.0)
        # - labels: impossible to use LaTeX formatting in labels
        # - arc: impossible to take into account figure ratio when dynamic rescaling is activated
        # - forces/vectors: impossible to adjust the line_color and line_dash of OpenHead according to datasource

        ###--- First display the clothesline
        # Fix graph to problem boundaries
        ymargin = .05
        xmargin = .2
        fig_object = figure(title='Suspended object ({} kg)'.format(self.m_object), plot_width=800, plot_height=400, #plot_width=600, plot_height=400, sizing_mode='stretch_height', 
                            y_range=(self.y_origin-ymargin,self.y_origin+self.height+ymargin), x_range=(self.x_origin-xmargin,self.x_origin+self.distance+xmargin), 
                            background_fill_color='#ffffff', toolbar_location=None)
        fig_object.title.align = "center"
        fig_object.yaxis.axis_label = 'Height (m)'

        # Customize graph style so that it doesn't look too much like a graph
        fig_object.ygrid.visible = False
        fig_object.xgrid.visible = False
        fig_object.outline_line_color = None

        # Indicate the horizontal scale
        fig_object.xaxis.axis_label = "Distance (m) "

        # Draw the horizon line
        fig_object.add_layout(Span(location=self.height, dimension='width', line_color='gray', line_dash='dashed', line_width=1))
        
        # Draw the poles
        fig_object.line([self.x_origin, self.x_origin], [self.y_origin, self.y_origin+self.height], color="black", line_width=8, line_cap="round")
        fig_object.line([self.x_origin+self.distance, self.x_origin+self.distance], [self.y_origin, self.y_origin+self.height], color="black", line_width=8, line_cap="round")
        
        # Draw the ground
        fig_object.add_layout(Span(location=self.x_origin, dimension='width', line_color='black', line_width=1))
        fig_object.hbar(y=self.y_origin-ymargin, height=ymargin*2, left=self.x_origin-xmargin, right=self.x_origin+self.distance+xmargin, color="white", line_color="white", hatch_pattern="/", hatch_color="gray")

        
        # --DYN-- Draw the point at which the object is suspended (this data source also used for the other graphs)
        self.object_source = ColumnDataSource(data=dict(
            x=[coord_object[0]],
            y=[coord_object[1]],
            alpha_degrees=[self.alpha_degrees],
            height_text=[height_text],
            alpha_text=[alpha_text]
        ))
        fig_object.circle(source=self.object_source, x='x', y='y', size=8, fill_color="black", line_color='black', line_width=2)
        fig_object.add_layout(LabelSet(source=self.object_source, x='x', y='y', text='height_text', level='glyph', x_offset=8, y_offset=-20))

        # --DYN-- Draw the hanging cable
        self.cable_source = ColumnDataSource(data=dict(
            x=[self.x_origin, coord_object[0], self.x_origin+self.distance],
            y=[self.y_origin+self.height, coord_object[1], self.y_origin+self.height]
        ))
        fig_object.line(source=self.cable_source, x='x', y='y', color="black", line_width=2, line_cap="round")

        
        # --DYN-- Draw the angle between the hanging cable and horizonline
        # Trick here: we use a straight line because the Arc glyph doesn't support dynamic figure ratio
        ratio=1.5
        x0=self.x_origin+ratio*self.radius
        y0=self.y_origin+self.height
        x1=(self.x_origin+self.radius*np.cos(alpha))
        y1=(self.y_origin+self.height-self.radius*np.sin(alpha))
        self.alpha_arc = fig_object.line([x0, x1], [y0, y1], color="gray", line_width=1, line_dash=[2,2])
        fig_object.add_layout(LabelSet(source=self.object_source, x=self.x_origin, y=self.y_origin+self.height, text='alpha_text', level='glyph', x_offset=50, y_offset=-20))

        
        
        # --DYN-- Draw the force vectors
        # Weight
        Fy = self.m_object*self.gravity*self.force_scaling
        # Tension
        Tx = ((self.m_object*self.gravity) / (2*np.tan(alpha)))*self.force_scaling
        Ty = .5*self.m_object*self.gravity*self.force_scaling

        self.forces_x_start = [coord_object[0]]*self.forces_nb
        self.forces_y_start = [coord_object[1]]*self.forces_nb
        self.forces_x_mag = [0, Tx, 0, -Tx]
        self.forces_y_mag = [-Fy, Ty, Fy, Ty]

        self.forces_source = ColumnDataSource(data=dict(
            x_start=self.forces_x_start,
            y_start=self.forces_y_start,
            x_end=list(map(add, self.forces_x_start, self.forces_x_mag)),
            y_end=list(map(add, self.forces_y_start, self.forces_y_mag)),
            name=["F", "T", "Tr", "T"],
            color=["blue", "red", "gray", "red"],
            dash=["solid", "solid", [2,2], "solid"],
            x_offset=[8, 25, 8, -35],
            y_offset=[-45, 6, 45, 6]
        ))
        
        # Draw the arrows
        forces_arrows = Arrow(source=self.forces_source, x_start='x_start', y_start='y_start', x_end='x_end', y_end='y_end', 
                   line_color='color', line_width=2, end=OpenHead(line_width=2, size=12, line_color='black'))
        fig_object.add_layout(forces_arrows)

        # Add the labels
        forces_labels = LabelSet(source=self.forces_source, x='x_start', y='y_start', text='name', text_color='color', level='glyph', 
                                 x_offset='x_offset', y_offset='y_offset', render_mode='canvas')
        fig_object.add_layout(forces_labels)
        
        
        # --DYN-- Draw the tension projection lines
        self.proj_source = ColumnDataSource(data=dict(
            x=self.forces_source.data["x_end"][1:4],
            y=self.forces_source.data["y_end"][1:4]
        ))
        fig_object.line(source=self.proj_source, x='x', y='y', color="gray", line_width=1, line_dash="dashed")

        
        ###--- Display the whole interface
        show(row(children=[fig_object]), notebook_handle=True)
        display(VBox([self.alpha_slider_input]))
        

    # Event handlers
    def alpha_slider_event_handler(self, change):
        # get new value of counterweight mass
        self.alpha_degrees = change.new

        # compute the variables depending on alpha
        alpha = degrees_to_radians(self.alpha_degrees)
        alpha_text = '⍺ = {:.2f} °'.format(self.alpha_degrees)

        coord_object = self.get_object_coords(alpha)
        height_text =  'h = {:.2f} m'.format(coord_object[1])

        self.forces_y_start = [coord_object[1]]*self.forces_nb
        Tx = ((self.m_object*self.gravity) / (2*np.tan(alpha)))*self.force_scaling
        self.forces_x_mag = [0, Tx, 0, -Tx]    

        # update the object representation on all graphs (coordinates+labels)
        self.object_source.data = dict(
            x=[coord_object[0]],
            y=[coord_object[1]],
            alpha_degrees=[self.alpha_degrees],
            height_text=[height_text],
            alpha_text=[alpha_text]
        )

        # update line representing the angle alpha
        self.alpha_arc.data_source.patch({
            'x' : [(1, self.x_origin+self.radius*np.cos(alpha))],
            'y' : [(1, self.y_origin+self.height-self.radius*np.sin(alpha))]
        })

        # update the point where the object is attached on cable
        self.cable_source.patch({
            'x' : [(1, coord_object[0])],
            'y' : [(1, coord_object[1])]
        })

        # update point of start for all forces, update Tx and Ty for T
        self.forces_source.patch({ 
            'y_start' : [(slice(self.forces_nb), self.forces_y_start)],
            'x_end' : [(slice(self.forces_nb), list(map(add, self.forces_x_start, self.forces_x_mag)))],
            'y_end' : [(slice(self.forces_nb), list(map(add, self.forces_y_start, self.forces_y_mag)))],
        })

        # update the tension projection lines
        self.proj_source.patch({
            'x' : [(slice(3), self.forces_source.data["x_end"][1:4])],
            'y' : [(slice(3), self.forces_source.data["y_end"][1:4])]
        })

        push_notebook()
        
        
        
        
    def visualize_angle(self, angle_degrees):
        
        ### first let's validate the angle
        # it cannot be null (i.e. cable horizontal) or negative
        if angle_degrees <= 0:
            print("\033[1m\x1b[91m The angle cannot be null or negative. \x1b[0m\033[0m")
            return
        
        # it cannot be more than the default angle given the parameters of the situation
        alpha_default = np.arctan(self.height / (self.distance / 2))
        alpha_default_degrees = radians_to_degrees(alpha_default)
        if angle_degrees > alpha_default_degrees:
            print(f"\033[1m\x1b[91m The angle cannot be greater than {alpha_default_degrees:.2f} degrees given the parameters of this situation (poles of {self.height} meters, distant by {self.distance} meters). \x1b[0m\033[0m")
            angle_degrees = alpha_default_degrees

        
        # compute variables dependent with the angle selected by the user
        alpha_degrees = angle_degrees
        alpha = degrees_to_radians(alpha_degrees)
        alpha_text = '⍺ = {:.2f} °'.format(alpha_degrees)
        
        coord_object = self.get_object_coords(alpha)
        height_text =  'h = {:.2f} m'.format(coord_object[1])

        
        ###--- Create the figure ---###
        # LIMITATIONS of Bokeh (BokehJS 1.4.0)
        # - labels: impossible to use LaTeX formatting in labels
        # - arc: impossible to take into account figure ratio when dynamic rescaling is activated
        # - forces/vectors: impossible to adjust the line_color and line_dash of OpenHead according to datasource

        ###--- First display the clothesline
        # Fix graph to problem boundaries
        ymargin = .05
        xmargin = .2
        fig_object = figure(title='Suspended object ({} kg)'.format(self.m_object), plot_width=800, plot_height=400, #sizing_mode='scale_both', 
                            y_range=(self.y_origin-ymargin,self.y_origin+self.height+ymargin), x_range=(self.x_origin-xmargin,self.x_origin+self.distance+xmargin), 
                            background_fill_color='#ffffff', toolbar_location=None)
        fig_object.title.align = "center"
        fig_object.yaxis.axis_label = 'Height (m)'
        fig_object.xaxis.axis_label = "Distance (m)"

        # Customize graph style so that it doesn't look too much like a graph
        fig_object.ygrid.visible = False
        fig_object.xgrid.visible = False
        fig_object.outline_line_color = None


        # Draw the horizon line
        fig_object.add_layout(Span(location=self.height, dimension='width', line_color='gray', line_dash='dashed', line_width=1))
        
        # Draw the poles
        fig_object.line([self.x_origin, self.x_origin], [self.y_origin, self.y_origin+self.height], color="black", line_width=8, line_cap="round")
        fig_object.line([self.x_origin+self.distance, self.x_origin+self.distance], [self.y_origin, self.y_origin+self.height], color="black", line_width=8, line_cap="round")
        
        # Draw the ground
        fig_object.add_layout(Span(location=self.x_origin, dimension='width', line_color='black', line_width=1))
        fig_object.hbar(y=self.y_origin-ymargin, height=ymargin*2, left=self.x_origin-xmargin, right=self.x_origin+self.distance+xmargin, color="white", line_color="white", hatch_pattern="/", hatch_color="gray")

        
        # --DYN-- Draw the point at which the object is suspended (this data source also used for the other graphs)
        self.object_source = ColumnDataSource(data=dict(
            x=[coord_object[0]],
            y=[coord_object[1]],
            alpha_degrees=[alpha_degrees],
            height_text=[height_text],
            alpha_text=[alpha_text]
        ))
        fig_object.circle(source=self.object_source, x='x', y='y', size=8, fill_color="black", line_color='black', line_width=2)
        fig_object.add_layout(LabelSet(source=self.object_source, x='x', y='y', text='height_text', level='glyph', x_offset=8, y_offset=-35))

        # --DYN-- Draw the hanging cable
        self.cable_source = ColumnDataSource(data=dict(
            x=[self.x_origin, coord_object[0], self.x_origin+self.distance],
            y=[self.y_origin+self.height, coord_object[1], self.y_origin+self.height]
        ))
        fig_object.line(source=self.cable_source, x='x', y='y', color="black", line_width=2, line_cap="round")

        
        # --DYN-- Draw the angle between the hanging cable and horizonline
        # Trick here: we use a straight line because the Arc glyph doesn't support dynamic figure ratio
        ratio=1.5
        x0=self.x_origin+ratio*self.radius
        y0=self.y_origin+self.height
        x1=(self.x_origin+self.radius*np.cos(alpha))
        y1=(self.y_origin+self.height-self.radius*np.sin(alpha))
        self.alpha_arc = fig_object.line([x0, x1], [y0, y1], color="gray", line_width=1, line_dash=[2,2])
        fig_object.add_layout(LabelSet(source=self.object_source, x=self.x_origin, y=self.y_origin+self.height, text='alpha_text', level='glyph', x_offset=50, y_offset=-20))

        
        # --DYN-- Draw the force vectors
        # Weight
        Fy = self.m_object*self.gravity*self.force_scaling
        # Tension
        Tx = ((self.m_object*self.gravity) / (2*np.tan(alpha)))*self.force_scaling
        Ty = .5*self.m_object*self.gravity*self.force_scaling

        self.forces_x_start = [coord_object[0]]*self.forces_nb
        self.forces_y_start = [coord_object[1]]*self.forces_nb
        self.forces_x_mag = [0, Tx, 0, -Tx]
        self.forces_y_mag = [-Fy, Ty, Fy, Ty]

        self.forces_source = ColumnDataSource(data=dict(
            x_start=self.forces_x_start,
            y_start=self.forces_y_start,
            x_end=list(map(add, self.forces_x_start, self.forces_x_mag)),
            y_end=list(map(add, self.forces_y_start, self.forces_y_mag)),
            name=["F", "T", "Tr", "T"],
            color=["blue", "red", "gray", "red"],
            dash=["solid", "solid", [2,2], "solid"],
            x_offset=[8, 15, 8, -25],
            y_offset=[-64, -16, 45, -16]
        ))
        
        # Draw the arrows
        ### Bokeh issue here: with a datasource, it is not possible to specify the color of the openhead so it remains black
        forces_arrows = Arrow(source=self.forces_source, x_start='x_start', y_start='y_start', x_end='x_end', y_end='y_end', 
                   line_color='color', line_width=2, end=OpenHead(line_width=2, size=12))
        fig_object.add_layout(forces_arrows)
        

        # Add the labels
        forces_labels = LabelSet(source=self.forces_source, x='x_start', y='y_start', text='name', text_color='color', level='glyph', 
                                 x_offset='x_offset', y_offset='y_offset', render_mode='canvas')
        fig_object.add_layout(forces_labels)
        
        
        # --DYN-- Draw the tension projection lines
        self.proj_source = ColumnDataSource(data=dict(
            x=self.forces_source.data["x_end"][1:4],
            y=self.forces_source.data["y_end"][1:4]
        ))
        fig_object.line(source=self.proj_source, x='x', y='y', color="gray", line_width=1, line_dash="dashed")

        
        ###--- Display the whole interface
        show(row(children=[fig_object]), notebook_handle=True) #, sizing_mode="scale_both"
        

    # Utility functions
    def get_angle(self, m_counterweight):
        """
        Computes the angle that the cable makes with the horizon depending on the counterweight chosen:
        - if the counterweight is sufficient: angle = arcsin(1/2 * m_object / m_counterweight)
        - else (object on the ground): alpha = arctan(height / (distance / 2))

        :m_counterweight: mass of the chosen counterweight

        :returns: angle that the cable makes with the horizon (in rad)
        """
        # Default alpha value i.e. object is on the ground
        alpha_default = np.arctan(self.height / (self.distance / 2))
        alpha = alpha_default

        # Let's check that there is actually a counterweight
        if  m_counterweight > 0:

            # Then we compute the ratio of masses
            ratio = 0.5 * self.m_object / m_counterweight

            # Check that the ratio of masses is in the domain of validity of arcsin ([-1;1])
            if abs(ratio) < 1:
                alpha = np.arcsin(ratio)

        return min(alpha_default, alpha)


    def get_object_coords(self, angle):
        """
        Computes the position of the object on the cable taking into account the angle determined by the counterweight and the dimensions of the hanging system.
        By default:
        - the object is supposed to be suspended exactly in the middle of the cable
        - the object is considered on the ground for all values of the angle which give a delta height higher than the height of the poles

        :angle: angle that the cable makes with the horizon, in radians

        :returns: coordinates of the point at which the object are hanged 
        """
        # the jean is midway between the poles
        x_object = self.x_origin + 0.5 * self.distance

        # default y value: the jean is on the ground 
        y_object = self.y_origin 

        # we check that the angle is comprised between horizontal (greater than 0) and vertical (smaller than pi/2)
        if angle > 0 and angle < (np.pi / 2): 
            
            # we compute the delta between the horizon and the point given by the angle
            delta = (0.5 * self.distance * np.tan(angle))
            
            # we check that the delta is smaller than the height of the poles (otherwise it just means the jean is on the ground)
            if delta <= self.height:
                y_object = self.y_origin + self.height - delta

        return [x_object, y_object]



def degrees_to_radians(angle_degrees):
    return angle_degrees * np.pi / 180

def radians_to_degrees(angle_radians):
    return angle_radians * 180 / np.pi


# EOF
