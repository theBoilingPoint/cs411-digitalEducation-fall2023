import matplotlib.pyplot as plt
import ipywidgets as widgets

# Enable interactive backend for matplotlib
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'widget')


def displayInteractiveHouse():
    # We will plot a rectangle to model a house
    house_x = [2, 2, 4, 4]
    house_y = [0, 2, 2, 0]

    # We will plot a triangle to model the roof
    roof_x = [2, 3, 4]
    roof_y = [2, 5, 2]

    # Creation of the figure
    fig = plt.figure(num='Interactive figure', figsize=(6,4))

    # Creation of one subplot/axe - it will take position index number 1 in a grid of 1 row and 1 column, as described by (nrows, ncols, index)
    ax = fig.add_subplot(1,1,1)

    # Plot the house
    ax.plot(house_x, house_y)

    # Plot the roof, and get the resulting line, on which we will add interactivity later - NOTICE the syntax with the comma "roof_line, ="
    roof_line, = ax.plot(roof_x, roof_y)

    # We create a slider with values ranging from 2 to 10 in steps of .5, by default on value 5
    roof_widget = widgets.FloatSlider(min=2, max=10, step=0.5, value=5, description='Roof height:')
    

    # This function will be called when the slider is moved
    def roof_event_handler(change):
        # It allows us to retrieve the new value of the slider
        newposition = change.new

        # Then we can change the points of the door line
        roof_line.set_ydata([2, newposition, 2])
        
        # Finally we tell the figure to draw the changed parts
        fig.canvas.draw_idle()
        
    
    # Finally we link the widget to the callback function  
    roof_widget.observe(roof_event_handler, names='value')


    # The figure is automatically displayed since matplotlib is in interactive mode (if we display it explicitely, it will show up twice!)
    # We only need to display the widget
    display(roof_widget)
