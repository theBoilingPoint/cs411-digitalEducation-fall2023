# Enable interactive backend for matplotlib
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'widget')

import numpy as np

from ipywidgets import interact, interactive, fixed, interact_manual
from ipywidgets import HBox, VBox, Label, Layout
import ipywidgets as widgets

from IPython.display import IFrame
from IPython.display import set_matplotlib_formats, display, Math, Markdown, Latex, HTML
set_matplotlib_formats('svg')


import matplotlib.pyplot as plt
import matplotlib.patches as pat
plt.style.use('seaborn-whitegrid') # global style for plotting

class SuspendedObjectLab:
    """
    This class embeds all the necessary code to create a virtual lab to study the static equilibrium of an object suspended on a clothesline with a counterweight.
    """
    
    def __init__(self, m_object = 3, distance = 2, height = 1, x_origin = 0, y_origin = 0):
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


        
        ###--- Then we define the elements of the ihm:
        # parameters for sliders
        self.m_counterweight_min = 0.0
        self.m_counterweight_max = 100.0
        self.m_counterweight = self.m_counterweight_min # initial mass of the counterweight (0 by default, no counterweight at the beginning)

        # IHM input elements
        self.m_counterweight_label = Label('Mass of the counterweight ($kg$):', layout=Layout(margin='15px 5px 15px 0px'))
        self.m_counterweight_widget = widgets.FloatSlider(min=self.m_counterweight_min,max=self.m_counterweight_max,step=0.5,value=self.m_counterweight, layout=Layout(margin='15px 0px'))
        self.m_counterweight_input = HBox([self.m_counterweight_label, self.m_counterweight_widget])

        # IHM output elements
        self.quiz_output = widgets.Output()

        # Linking widgets to handlers
        self.m_counterweight_widget.observe(self.m_counterweight_event_handler, names='value')


        
        ###--- Compute variables dependent with the counterweight selected by the user
        alpha = self.get_angle(self.m_counterweight)
        alpha_degrees = alpha*180/np.pi
        alpha_text = r'$\alpha$ = {:.2f} $^\circ$'.format(alpha_degrees)
        
        coord_object = self.get_object_coords(alpha)
        height_text =  r'h = {:.2f} $m$'.format(coord_object[1])


        
        ###--- Create the figure
        
        # Create the figure and subplots in it
        self.fig = plt.figure(num='Suspended Object Lab', constrained_layout=False, figsize=(10,4)) # hack for interactive backend: num is the title which appears above the canvas
        gs = self.fig.add_gridspec(ncols=7, nrows=1, wspace=0.5, hspace=0, right=0.95, top=0.9, left=0.05, bottom=0.1)
        ax1 = self.fig.add_subplot(gs[0, :3])
        ax2 = self.fig.add_subplot(gs[0, 3:5], sharey = ax1)
        ax3 = self.fig.add_subplot(gs[0, 5:7], sharex = ax2)
        
        # Deactivate toolbar (hack for interactive backend) 
        # NOT WORKING
        self.fig.canvas.toolbar_visible = False
        
        # Deactivate coordinate formatter (hack for interactive backend)
        ax1.format_coord = lambda x, y: ''
        ax2.format_coord = lambda x, y: ''
        ax3.format_coord = lambda x, y: ''
        
        
        ###--- First display the clothesline
        ax1.set_title('Suspended object ({} kg)'.format(self.m_object))

        # Fix graph to problem boundaries
        ymargin = .06
        xmargin = .4
        ax1.set_ylim(bottom = self.y_origin - ymargin) # limit bottom of y axis to ground
        ax1.set_ylim(top = self.y_origin + self.height + ymargin) # limit top of y axis to values just above height

        # Customize graph style so that it doesn't look like a graph
        ax1.grid(False) # hide the grid 
        ax1.set_ylabel("Height ($m$)") # add a label on the y axis
        ax1.get_xaxis().set_visible(False) # hide x axis
        ax1.spines['top'].set_visible(False) # hide the frame
        ax1.spines['bottom'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)

        # Draw the poles
        x_pole1 = np.array([self.x_origin, self.x_origin])
        y_pole1 = np.array([self.y_origin, self.y_origin+self.height])
        ax1.plot(x_pole1, y_pole1, "k-", linewidth=7, zorder=1)
        x_pole2 = np.array([self.x_origin+self.distance, self.x_origin+self.distance])
        y_pole2 = np.array([self.y_origin, self.y_origin+self.height])
        ax1.plot(x_pole2, y_pole2, "k-", linewidth=7, zorder=1)
        
        # Draw the ground
        ax1.axhline(y=self.y_origin, color='black', linewidth=1, zorder=2)
        ax1.add_patch(pat.Polygon([[self.x_origin-xmargin, self.y_origin], [self.x_origin+self.distance+xmargin, self.y_origin], [self.x_origin+self.distance+xmargin, self.y_origin-ymargin], [self.x_origin-xmargin, self.y_origin-ymargin]], closed=True, fill="white", facecolor="white", edgecolor="gray", hatch='///', linewidth=0.0, zorder=2))
        
        # Draw the horizon line
        ax1.axhline(y=self.y_origin+self.height, color='gray', linestyle='-.', linewidth=1, zorder=1)
        
        # -DYN- Draw the hanging cable
        x = np.array([self.x_origin, coord_object[0], self.x_origin+self.distance])
        y = np.array([self.y_origin+self.height, coord_object[1], self.y_origin+self.height])
        self.cable, = ax1.plot(x, y, linewidth=2, linestyle = "-", color="black")

        # -DYN- Draw the angle between the hanging cable and horizonline
        ellipse_radius = 0.2
        fig_ratio = self.height / self.distance
        self.cable_angle = pat.Arc(xy = (self.x_origin, self.y_origin+self.height), width = ellipse_radius/fig_ratio, height = ellipse_radius, theta1 = -1*alpha_degrees, theta2 = 0, color="gray", linestyle='-.')
        ax1.add_patch(self.cable_angle)
        self.cable_angle_text = ax1.annotate(alpha_text, xy=(self.x_origin, self.y_origin+self.height), xytext=(30, -15), textcoords='offset points', bbox=dict(boxstyle="round", facecolor = "white", edgecolor = "white", alpha = 0.8))
        
        # -DYN- Draw the point at which the object is suspended
        self.cable_point = ax1.scatter(coord_object[0], coord_object[1], s=80, c="black", zorder=15)
        self.cable_point_text = ax1.annotate(height_text, xy=(coord_object[0], coord_object[1]), xytext=(10, -10), textcoords='offset points', bbox=dict(boxstyle="round", facecolor = "white", edgecolor = "white", alpha = 0.8))
        
        # -DYN- Draw the force vectors
        # Parameters for drawing forces
        self.gravity = 9.81
        self.force_scaling = .01
        
        # Weight
        Fy = self.m_object*self.gravity*self.force_scaling
        self.cable_weight = ax1.quiver(coord_object[0], coord_object[1], 0, -Fy, color='blue', angles='xy', scale_units='xy', scale=1, zorder=12, width=0.007)
        self.cable_weight_text = ax1.annotate(r'$\vec{F}$', xy=(coord_object[0], coord_object[1]), xytext=(10, -55), textcoords='offset points', color='blue')

        # Tension
        Tx = ((self.m_object*self.gravity) / (2*np.tan(alpha)))*self.force_scaling
        Ty = .5*self.m_object*self.gravity*self.force_scaling
        self.cable_tension_right = ax1.quiver(coord_object[0], coord_object[1], Tx, Ty, color='red', angles='xy', scale_units='xy', scale=1, zorder=12, width=0.007, linewidth=1)
        self.cable_tension_right_text = ax1.annotate(r'$\vec{T}$', xy=(coord_object[0], coord_object[1]), xytext=(40, 5), textcoords='offset points', color='red')
        self.cable_tension_left = ax1.quiver(coord_object[0], coord_object[1], -Tx, Ty, color='red', angles='xy', scale_units='xy', scale=1, zorder=12, width=0.007, linewidth=1)
        self.cable_tension_left_text = ax1.annotate(r'$\vec{T}$', xy=(coord_object[0], coord_object[1]), xytext=(-45, 5), textcoords='offset points', color='red')
        self.cable_tension_sum = ax1.quiver(coord_object[0], coord_object[1], 0, Fy, color='red', angles='xy', scale_units='xy', scale=1, zorder=12, width=0.007, facecolor="none", edgecolor="red", hatch="/"*8, linewidth=0.0)
        self.cable_tension_sum_text = ax1.annotate(r'$\vec{T_r}$', xy=(coord_object[0], coord_object[1]), xytext=(10, 45), textcoords='offset points', color='red')
        
        
        ###--- Then display the angle and the height as functions from the mass of the counterweight
        # Create all possible values of the mass of the counterweight
        m_cw = np.linspace(self.m_counterweight_min, self.m_counterweight_max, 100)

        # Compute the angle (in degrees) and height for all these values
        angle = []
        height = []
        for m in m_cw:
            a = self.get_angle(m)
            angle.append(a*180/np.pi)

            c = self.get_object_coords(a)
            height.append(c[1])

        # Display the functions on the graphs
        ax2.set_title(r'Height ($m$)')
        ax2.set_xlabel('Mass of the counterweight (kg)')
        ax2.plot(m_cw, height, "green")

        ax3.set_title(r'Angle $\alpha$ ($^\circ$)')
        ax3.set_xlabel('Mass of the counterweight (kg)')
        ax3.plot(m_cw, angle, "green")

        
        # Draw the horizon lines
        ax2.axhline(y=self.y_origin+self.height, color='gray', linestyle='-.', linewidth=1, zorder=1)
        ax3.axhline(y=self.y_origin, color='gray', linestyle='-.', linewidth=1, zorder=1)
        
        # -DYN- Add the current height from the counterweight selected by the user
        self.graph_height_point = ax2.scatter(self.m_counterweight, coord_object[1], s=80, c="black", zorder=15)
        self.graph_height_text = ax2.annotate(height_text, xy=(self.m_counterweight, coord_object[1]), xytext=(10, -10), textcoords='offset points', bbox=dict(boxstyle="round", facecolor = "white", edgecolor = "white", alpha = 0.8))

        # -DYN- Add the current angle from the counterweight selected by the user
        self.graph_angle_point = ax3.scatter(self.m_counterweight, alpha_degrees, s=80, c="black", zorder=15)
        self.graph_angle_text = ax3.annotate(alpha_text, xy=(self.m_counterweight, alpha_degrees), xytext=(10, 5), textcoords='offset points', bbox=dict(boxstyle="round", facecolor = "white", edgecolor = "white", alpha = 0.8))



        ###--- Display the whole interface
        display(self.m_counterweight_input)
        


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
        - the object is on considered the ground for all values of the angle 

        :angle: angle that the cable makes with the horizon

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

        
        

    # Event handler
    def m_counterweight_event_handler(self, change):
        self.m_counterweight = change.new


        # Compute new values with the counterweight selected by the user
        alpha = self.get_angle(self.m_counterweight)
        alpha_degrees = alpha*180/np.pi
        alpha_text = r'$\alpha$ = {:.2f} $^\circ$'.format(alpha_degrees)
        
        coord_object = self.get_object_coords(alpha)
        height_text =  r'h = {:.2f} $m$'.format(coord_object[1])
        
        ### Update the clothesline figure
        # Update of the cable line
        x = np.array([self.x_origin, coord_object[0], self.x_origin+self.distance])
        y = np.array([self.y_origin+self.height, coord_object[1], self.y_origin+self.height])
        self.cable.set_xdata(x)
        self.cable.set_ydata(y)
        
        # Update of the point
        self.cable_point.set_offsets(coord_object)
        self.cable_point_text.set_text(height_text)
        self.cable_point_text.xy = (coord_object[0], coord_object[1])
        
        # Update of the angle
        self.cable_angle.theta1 = -1*alpha_degrees
        self.cable_angle_text.set_text(alpha_text)
        
        # Update the weight position (direction does not change)
        self.cable_weight.set_offsets(coord_object)
        self.cable_weight_text.xy = (coord_object[0], coord_object[1])

        # Update the tension position and directions
        Tx = ((self.m_object*self.gravity) / (2*np.tan(alpha)))*self.force_scaling
        Ty = .5*self.m_object*self.gravity*self.force_scaling
        self.cable_tension_right.set_offsets(coord_object)
        self.cable_tension_right.set_UVC(Tx, Ty)
        self.cable_tension_right_text.xy = (coord_object[0], coord_object[1])
        self.cable_tension_left.set_offsets(coord_object)
        self.cable_tension_left.set_UVC(-Tx, Ty)
        self.cable_tension_left_text.xy = (coord_object[0], coord_object[1])
        self.cable_tension_sum.set_offsets(coord_object)
        self.cable_tension_sum_text.xy = (coord_object[0], coord_object[1])
        
        
        ### Update the other two graphs
        # Update point of angle
        self.graph_angle_point.set_offsets([self.m_counterweight, alpha_degrees])
        self.graph_angle_text.set_text(alpha_text)
        self.graph_angle_text.xy = (self.m_counterweight, alpha_degrees)

        # Update point of height
        self.graph_height_point.set_offsets([self.m_counterweight, coord_object[1]])
        self.graph_height_text.set_text(height_text)
        self.graph_height_text.xy = (self.m_counterweight, coord_object[1])
        
        
        # Display graph 
        #self.fig.canvas.draw_idle()



# EOF
