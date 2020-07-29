
"""
List of functions intended to visualise the loaded data (electrophysiological signals).

This functions are mainly supported by Bokeh package.

Available Functions
-------------------
[Public]

plot_future  !!!!!!!!!!! Untested version for future application !!!!!!!!!!!!!!!!!
    Plotting function intended for an easy representation of OpenSignals acquired data.
plot
    Plotting function intended for an easy representation of OpenSignals acquired data.
opensignals_style
    The application of this function ensures that OpenSignals graphical style will be automatically
    applied to the Bokeh plots.
opensignals_color_pallet
    Returns one of the available OpenSignals colors following an iterative mechanism.
opensignals_kwargs
    Function used in order to be automatically applied the OpenSignals graphical style to the
    toolbar of Bokeh grid plots.
plot_android_sensor_timeline
    Function to visualise the sensor acquisition timeline of android sensors.

Available Functions
-------------------
[Private]

_check_validity_of_inputs
    Checks when an input of function 'plot' has a valid format.

Observations/Comments
---------------------
None

/\
"""

import itertools
from numbers import Number
import numpy
from bokeh.plotting import figure, output_file, show, save
from bokeh.models.tools import PanTool, ResetTool, BoxZoomTool, WheelZoomTool
from bokeh.models.glyphs import Line
from bokeh.plotting.figure import FigureOptions
from bokeh.layouts import gridplot
# select a palette
from bokeh.palettes import Category20_20 as palette
from IPython.display import HTML
from .aux_functions import _filter_keywords, _is_instance, _generate_bokeh_file

COLOR_LIST = itertools.cycle(("#009EE3", "#302683", "#00893E", "#94C11E", "#FDC400", "#E84D0E",
                              "#CF0272", "#F199C1"))

def _plot_future(time, data, legend_label=None, title=None, y_axis_label=None, hor_lines=None,
                hor_lines_leg=None, vert_lines=None, vert_lines_leg=None,
                apply_opensignals_style=True, show_plot=True, warn_print=False, **kwargs):
    """
    Plotting function intended for an easy representation of OpenSignals acquired data.

    ----------
    Parameters
    ----------
    time : list or list of lists
        List that contains the time axis samples or a list of lists, when it is intended to present
        data in a gridplot format. When the input is a list of lists the following structure must
        be respected:
        Gridplot with N rows and M columns
        [[cell_row_0_column_0, cell_row_0_column_1, ..., cell_row_0_column_M],
         [cell_row_1_column_0, cell_row_1_column_1, ..., cell_row_1_column_M],
          ...
         [cell_row_N_column_0, cell_row_N_column_1, ..., cell_row_N_column_M]]

    data : list or list of lists
        Should have the same shape of time until the cell_row_n_column_m level. At this stage
        cell_row_n_column_m can contain a set of lists. Each one of these lists contains give
        rise to a different plot at the figure located in row n and column m of the grid structure.

    legend_label : list
        Input where the legend of each plot is specified. Should have the same shape of data.

    title : list
        Input where the title of each figure is specified. Should have the same shape of time.

    y_axis_label : list
        Input where the y label of each figure is specified. Should have the same shape of time.

    hor_lines : list of lists
        The parent list must have the same shape of time and each of its elements (child lists)
        must be formed by numbers defining the y axis position of the horizontal lines.

    hor_lines_leg : list of lists
        Legends of the horizontal lines (same shape of hor_lines).

    vert_lines : list of lists
        The parent list must have the same shape of time and each of its elements (child lists)
        must be formed by numbers defining the x axis position of the vertical lines.

    vert_lines_leg : list of lists
        Legends of the vertical lines (same shape of vert_lines).

    apply_opensignals_style : boolean
        If True then the OpenSignals style will be applied.


    show_plot : boolean
        If True the generated figures will be shown.

    warn_print : bool
        If True some warnings about invalid kwargs keys will be prompted.

    **kwargs : dict
        Keyword values for applying in bokeh figures, lines and gridplots.

    Returns
    -------
    out : bokeh figure or gridplot
        Object that is produced during the execution of the present function.

    """

    # -------------------------------- Application of styling options -----------------------------
    if apply_opensignals_style is True:
        style_figure = {**opensignals_kwargs("figure"), **_filter_keywords(FigureOptions, kwargs,
                                                                           is_class=True,
                                                                           warn_print=warn_print)}
        style_line = {**opensignals_kwargs("line"), **_filter_keywords(Line, kwargs,
                                                                       warn_print=warn_print)}
        style_gridplot = {**opensignals_kwargs("gridplot"),
                          **_filter_keywords(gridplot, kwargs, warn_print=warn_print)}
    else:
        style_figure = _filter_keywords(FigureOptions, kwargs, is_class=True, warn_print=warn_print)
        style_line = _filter_keywords(Line, kwargs, warn_print=warn_print)
        style_gridplot = _filter_keywords(gridplot, kwargs, warn_print=warn_print)

    # ---------- Based on the input check if the output should be in the gridplot format ----------
    if len(list(numpy.shape(data))) == 3 and len(list(numpy.shape(time))) == 3:
        grid_plot = True
    elif len(list(numpy.shape(data))) == 1 and len(list(numpy.shape(time))) == 1:
        grid_plot = False
    else:
        raise RuntimeError("'time' and 'data' fields must have the same shape, which would be a "
                           "list with 1 dimension or a list of lists with 3 levels, such as [[["
                           "time_0_0, time_0,1, time_0_2], [time_1_0, time_1_1, time_1_2]]]. In the"
                           " previous example the output will be a gridplot with 2 rows and "
                           "three columns.")

    # ------------ Verification if the input arguments (title and legend) are valid ---------------
    # [legend]
    legend_label = _check_validity_of_inputs(data, legend_label, "legend", grid_plot, dimension=3)

    # [title]
    title = _check_validity_of_inputs(data, title, "title", grid_plot, dimension=2)

    # [y_axis_label]
    y_axis_label = _check_validity_of_inputs(data, y_axis_label, "y_axis_label", grid_plot,
                                             dimension=2)

    # Horizontal Lines.
    # [hor_lines]
    hor_lines = _check_validity_of_inputs(data, hor_lines, "hor_lines", grid_plot, dimension=2)
    hor_lines_leg = _check_validity_of_inputs(data, hor_lines_leg, "hor_lines_leg", grid_plot,
                                              dimension=2)

    # Vertical Lines.
    # [vert_lines]
    vert_lines = _check_validity_of_inputs(data, vert_lines, "vert_lines", grid_plot, dimension=2)
    vert_lines_leg = _check_validity_of_inputs(data, vert_lines_leg, "vert_lines_leg", grid_plot,
                                               dimension=2)

    # --------------------------------------- Plotting Stage --------------------------------------
    fig_list = []
    if grid_plot is True:
        # Each element inside "data", "time", "title", "legend" ... matrix cell must be a list.
        if all(_is_instance(list, el, condition="all", deep=True) for el in [time, data, title,
                                                                         legend_label, y_axis_label,
                                                                         hor_lines, vert_lines,
                                                                         hor_lines_leg,
                                                                         vert_lines_leg]):
            for row in range(0, len(data)):  # Generation of a figure per plot.
                fig_list.append([])
                for column in range(0, len(data[row])):
                    for plt in range(0, len(data[row][column])):
                        # Verification if all elements inside list are numbers.
                        if _is_instance(Number, data[row][column][plt], condition="all", deep=True) \
                                and not _is_instance(bool, data[row][column][plt], condition="any") \
                                and _is_instance(Number, time[row][column][0], condition="all") \
                                and not _is_instance(bool, time[row][column][0], condition="any"):
                            fig_list.append([])

                            # Generation of multiple figures.
                            fig_list[-1][-1].append(figure(title=title[row][column][0],
                                                           y_axis_label=y_axis_label[row]
                                                                                    [column][0],
                                                           **style_figure))

                            fig_list[-1][-1][-1].line(time[row][column][0], data[row][column][plt],
                                                      legend_label=legend_label[row][column][plt], **style_line)
                        else:
                            raise RuntimeError("At least one of the list elements, specified in "
                                               "data or time, is not numeric.")

                    # Representation of horizontal lines.
                    if hor_lines is not None:
                        for hor_line_nbr, hor_line in enumerate(hor_lines[row][column]):
                            if hor_lines_leg is not None:
                                fig_list[-1][-1][-1].line([time[row][column][0],
                                                           time[row][column][-1]],
                                                          [hor_line, hor_line],
                                                          legend_label=hor_lines_leg[row][hor_line_nbr],
                                                          **opensignals_kwargs("line"))
                            else:
                                fig_list[-1][-1][-1].line([time[row][column][0],
                                                           time[row][column][-1]],
                                                          [hor_line, hor_line],
                                                          **opensignals_kwargs("line"))

                    # Representation of vertical lines.
                    if vert_lines is not None:
                        for vert_line_nbr, vert_line in enumerate(vert_lines[row][column]):
                            if vert_lines_leg is not None:
                                fig_list[-1][-1][-1].line([vert_line, vert_line],
                                                          [numpy.min(data[row][column][0]),
                                                           numpy.max(data[row][column][0])],
                                                          legend_label=vert_lines_leg[row][vert_line_nbr],
                                                          **opensignals_kwargs("line"))
                            else:
                                fig_list[-1][-1][-1].line([vert_line, vert_line],
                                                          [numpy.min(data[row][column][0]),
                                                           numpy.max(data[row][column][0])],
                                                          **opensignals_kwargs("line"))

                    # Update of line style.
                    if apply_opensignals_style is True:
                        style_line = {**opensignals_kwargs("line"),
                                      **_filter_keywords(Line, kwargs, warn_print=warn_print)}
                    else:
                        style_line = _filter_keywords(Line, kwargs, warn_print=warn_print)

        else:
            raise RuntimeError("At least one of the list elements, specified in data, "
                               "is not a sublist.")
    else:
        # If this happen, then we receive as input a single list for time and data
        # (Single plot perspective).
        if _is_instance(Number, data, condition="all") \
                and not _is_instance(bool, data, condition="any") \
                and _is_instance(Number, time, condition="all")\
                and not _is_instance(bool, time, condition="any"):
            fig_list.append(figure(title=title, y_axis_label=y_axis_label[0], **style_figure))
            fig_list[-1].line(time, data, legend_label=legend_label, **style_line)
        else:
            raise RuntimeError("At least one of the list elements, specified in data or time, is "
                               "not numeric.")

    # Application of the OpenSignals Sytle.
    if apply_opensignals_style is True:
        opensignals_style([item for sublist in fig_list for item in sublist])

    # Show of plots.
    if grid_plot is True:
        # Generation of the gridplot.
        grid = gridplot(fig_list, **style_gridplot)

        if show_plot is True:
            show(grid)
        else:
            raise RuntimeError("The specified number of lines and columns for the grid plot is not "
                               "compatible.")

    else:
        if show_plot is True:
            show(fig_list[-1])

    return fig_list


def plot(*args, legend_label=None, title=None, x_axis_label="Time (s)", y_axis_label=None,
         grid_plot=False, grid_lines=None, grid_columns=None, hor_lines=None, hor_lines_leg=None,
         vert_lines=None, vert_lines_leg=None, apply_opensignals_style=True, show_plot=True,
         save_plot=False, warn_print=False, get_fig_list=False, file_name="plot", scatter=False, **kwargs):
    """
    -----
    Brief
    -----
    Plotting function intended for an easy representation of OpenSignals acquired data.

    -----------
    Description
    -----------
    This function allows to plot data acquired with resource to OpenSignals, available at
    https://bitalino.com/en/software, in an easy way using the Bokeh library (https://bokeh.pydata.org/en/latest/).
    The plot will automatically present the OpenSignals style if the corresponding parameter is set to True
    (apply_opensignals_style=True).

    This allows to easily use multiple plot elements without the need to know any visualization libraries.

    ----------
    Parameters
    ----------
    *args: list
        Variable number of arguments with the purpose of giving the user the possibility of
        defining as an input only the "data" axis or both "time" and "data" axes.

    legend_label : list
        Input where the legend of each plot is specified. Should have the same shape of time.

    title : list
        Input where the title of each figure is specified. Should have the same shape of time.

    x_axis_label : list
        Input where the x label of each figure is specified. All figures will have the same x label
        in the current implementation.

    y_axis_label : list
        Input where the y label of each figure is specified. Should have a length equal to the
        number of figures.

    grid_plot : boolean
        If True then the plots will be organized in a grid_plot structure.

    grid_lines : int
        Number of lines of grid plot.

    grid_columns : int
        Number of columns of grid plot.

    hor_lines : list of lists
        The parent list must have the same shape of time and each of its elements (child lists)
        must be formed by numbers defining the y axis position of the horizontal lines.

    hor_lines_leg : list of lists
        Legends of the horizontal lines (same shape of hor_lines).

    vert_lines : list of lists
        The parent list must have the same shape of time and each of its elements (child lists)
        must be formed by numbers defining the x axis position of the vertical lines.

    vert_lines_leg : list of lists
        Legends of the vertical lines (same shape of vert_lines).

    apply_opensignals_style : boolean
        If True then the OpenSignals style will be applied.


    show_plot : boolean
        If True the generated figures will be shown.

    save_plot : boolean
        If True the generated figures will be stored on an html file.

    warn_print : bool
        If True some warnings about invalid kwargs keys will be prompted.

    get_fig_list : bool
        If True then it will be returned a list containing the figure objects generated during
        the function execution.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    scatter : bool (default: False)
        If True, the plot will be a scatter plot, else, it will be a line plot.

    **kwargs : dict
        Keyword values for applying in bokeh figures, lines and gridplots.

    Returns
    -------
    out : bokeh figure or gridplot
        Object that is produced during the execution of the present function.

    """

    # Generation of the HTML file where the plot will be stored.
    #file_name = _generate_bokeh_file(file_name)

    # Data conversion for ensuring that the function only works with lists.
    if len(args) == 1:
        time = [list(numpy.linspace(1, len(args[0][0]) + 1, len(args[0][0])))] * len(args[0])
        data = args[0]
    elif len(args) == 2:
        time = list(args[0])
        data = list(args[1])
    else:
        raise RuntimeError("biosignalsnotebooks plot function only accepts 1 or 2 arguments in *args"
                           " input. If only 1 input is given it should be a list with data samples,"
                           "otherwise if 2 inputs are given then the first one defines the time"
                           "axis and the second one data values.")

    # This function offers two input mechanisms (easy and complex). The easiest one consists in
    # the representation of a single plot in a single figure, so, the user only needs to specify as
    # inputs "time" and "data" lists. On the other hand, for the complex mechanism, the user can
    # represent plots in different figures, using for that lists of lists as "time" and "data"
    # inputs.
    # In the following lines is ensured that independently of the input given, the function will
    # achieve is purpose correctly.
    if _is_instance(Number, data, condition="all") and not _is_instance(bool, data, condition="any") \
            and _is_instance(Number, time, condition="all") \
            and not _is_instance(bool, time, condition="any"):
        time = [time]
        data = [data]
        if y_axis_label is not None:
            y_axis_label = [y_axis_label]
        if hor_lines is not None:
            hor_lines = [hor_lines]
        if hor_lines_leg is not None:
            hor_lines_leg = [hor_lines_leg]
        if vert_lines is not None:
            vert_lines = [vert_lines]
        if vert_lines_leg is not  None:
            vert_lines_leg = [vert_lines_leg]
        if title is not None:
            title = [title]
        if legend_label is not None:
            legend_label = [legend_label]
    elif _is_instance(numpy.ndarray, data, condition="any") \
            or _is_instance(numpy.ndarray, time, condition="any"):
        time = list(map(list, time))
        data = list(map(list, data))

    # Ensures the application or not of opensignals graphical style.
    if apply_opensignals_style is True:
        style_figure = {**opensignals_kwargs("figure"), **_filter_keywords(FigureOptions, kwargs,
                                                                           is_class=True,
                                                                           warn_print=warn_print)}
        style_line = {**opensignals_kwargs("line"), **_filter_keywords(Line, kwargs,
                                                                       warn_print=warn_print)}
        style_gridplot = {**opensignals_kwargs("gridplot"),
                          **_filter_keywords(gridplot, kwargs, warn_print=warn_print)}
    else:
        style_figure = _filter_keywords(FigureOptions, kwargs, is_class=True, warn_print=warn_print)
        style_line = _filter_keywords(Line, kwargs, warn_print=warn_print)
        style_gridplot = _filter_keywords(gridplot, kwargs, warn_print=warn_print)

    # ------------------------ Verification if the input arguments are valid ----------------------
    if legend_label is not None:
        if isinstance(legend_label, list):
            if len(legend_label) != len(time) or len(legend_label) != len(data):
                raise RuntimeError("The shape of legend does not match with time input.")
        else:
            raise RuntimeError("The specified data type of legend field is not valid. Input must "
                               "be a list.")
    #else:
    #    legend_label = [None] * len(time)

    if title is not None:
        if isinstance(title, list):
            if len(title) != len(time) or len(title) != len(data):
                raise RuntimeError("The shape of title does not match with time input.")
        elif isinstance(title, str):
            if grid_plot is True:
                raise RuntimeError("Each figure of the gridplot must have a title, i.e., the shape"
                                   " of time, data and title inputs needs to match.")
            else:
                title = [title] * len(time)
        elif grid_plot is False and len(title) != 1:
            raise RuntimeError("The number of titles is not compatible with the number of figures "
                               "(only one title is needed).")
        else:
            raise RuntimeError("The specified data type of title field is not valid. Input must be "
                               "a list.")
    else:
        title = [None] * len(time)

    if y_axis_label is not None:
        if isinstance(y_axis_label, list):
            if len(y_axis_label) != len(time) or len(y_axis_label) != len(data):
                raise RuntimeError("The shape of y_axis_label does not match with time input.")
        elif isinstance(y_axis_label, str):
            y_axis_label = [y_axis_label] * len(time)
        elif grid_plot is False and len(y_axis_label) != 1:
            raise RuntimeError("The number of y axis labels is not compatible with the number of "
                               "figures.")
        else:
            raise RuntimeError("The specified data type of y_axis_label field is not valid. Input "
                               "must be a list or a string when grid_plot field is False.")
    else:
        y_axis_label = [None] * len(time)

    # Coherence between grid_plot, grid_lines and grid_columns inputs.
    if grid_lines is not None or grid_columns is not None:
        if grid_plot is not True:
            raise RuntimeError("When grid_lines and grid_columns inputs are used the field grid_"
                               "plot must be True.")
        else:
            if not isinstance(grid_lines, int) or not isinstance(grid_columns, int):
                raise RuntimeError("At least one of the grid_lines or grid_columns values is not "
                                   "an integer.")

    # Horizontal Lines.
    if hor_lines is not None:
        if isinstance(hor_lines, list):
            if len(hor_lines) != len(time) or len(hor_lines) != len(data):
                raise RuntimeError("The shape of hor_lines does not match with time input.")
        else:
            raise RuntimeError("The specified data type of hor_lines field is not valid. Input "
                               "must be a list of lists.")

        # Each sublist entry must be numeric.
        for cell in hor_lines:
            if not _is_instance(Number, cell, condition="all") \
                    or _is_instance(bool, cell, condition="any"):
                raise RuntimeError("At least one of the list elements, specified in hor_lines, "
                                   "is not numeric.")
            elif vert_lines_leg is not None:
                if len(hor_lines) != len(hor_lines_leg):
                    raise RuntimeError("The shape of hor_lines and hor_lines_leg is not the same.")

    # Vertical Lines.
    if vert_lines is not None:
        if isinstance(vert_lines, list):
            if len(vert_lines) != len(time) or len(vert_lines) != len(data):
                raise RuntimeError("The shape of vert_lines does not match with time input.")
        else:
            raise RuntimeError("The specified data type of vert_lines field is not valid. "
                               "Input must be a list of lists.")

        # Each sublist entry must be numeric.
        for cell in vert_lines:
            if not _is_instance(Number, cell, condition="all") \
                    or _is_instance(bool, cell, condition="any"):
                raise RuntimeError("At least one of the list elements, specified in vert_lines, "
                                   "is not numeric.")
            elif vert_lines_leg is not None:
                if len(vert_lines) != len(vert_lines_leg):
                    raise RuntimeError("The shape of vert_lines and vert_lines_leg is not "
                                       "the same.")

    # --------------------------------------- Plotting Stage --------------------------------------
    fig_list = []
    # If all data entries are lists, then it is considered that we are in a multiplot situation.
    if _is_instance(list, data, condition="all") and _is_instance(list, time, condition="all"):
        for list_entry in range(0, len(time)):  # Generation of a figure per plot.
            # Verification if all elements inside list are numbers.
            if _is_instance(Number, data[list_entry], condition="all") \
                    and not _is_instance(bool, data[list_entry], condition="any") \
                    and _is_instance(Number, time[list_entry], condition="all") \
                    and not _is_instance(bool, time[list_entry], condition="any"):
                if len(time[list_entry]) == len(data[list_entry]):  # Shape verification
                    if grid_plot is True:  # Generation of multiple figures.
                        fig_list.append(figure(title=title[list_entry],
                                               y_axis_label=y_axis_label[list_entry],
                                               x_axis_label=x_axis_label,
                                               **style_figure))
                    elif grid_plot is False and list_entry == 0:
                        fig_list.append(figure(title=title[list_entry],
                                               y_axis_label=y_axis_label[list_entry],
                                               x_axis_label=x_axis_label,
                                               sizing_mode='scale_both',
                                               **style_figure))

                    if legend_label is not None:
                        if not scatter:
                            fig_list[-1].line(time[list_entry], data[list_entry], legend_label=legend_label[list_entry],
                                          **style_line)
                        else:
                            fig_list[-1].circle(time[list_entry], data[list_entry], legend_label=legend_label[list_entry],
                                          **style_line)
                    else:
                        if not scatter:
                            fig_list[-1].line(time[list_entry], data[list_entry], **style_line)
                        else:
                            fig_list[-1].circle(time[list_entry], data[list_entry], **style_line)

                    # Representation of horizontal lines.
                    if hor_lines is not None:
                        for hor_line_nbr, hor_line in enumerate(hor_lines[list_entry]):
                            if hor_lines_leg is not None:
                                fig_list[-1].line([time[list_entry][0], time[list_entry][-1]],
                                                  [hor_line, hor_line],
                                                  legend_label=hor_lines_leg[list_entry][hor_line_nbr],
                                                  **opensignals_kwargs("line"))
                            else:
                                fig_list[-1].line([time[list_entry][0], time[list_entry][-1]],
                                                  [hor_line, hor_line],
                                                  **opensignals_kwargs("line"))

                    # Representation of vertical lines.
                    if vert_lines is not None:
                        for vert_line_nbr, vert_line in enumerate(vert_lines[list_entry]):
                            if vert_lines_leg is not None:
                                fig_list[-1].line([vert_line, vert_line],
                                                  [numpy.min(data[list_entry]),
                                                   numpy.max(data[list_entry])],
                                                  legend_label=vert_lines_leg[list_entry][vert_line_nbr],
                                                  **opensignals_kwargs("line"))
                            else:
                                fig_list[-1].line([vert_line, vert_line],
                                                  [numpy.min(data[list_entry]),
                                                   numpy.max(data[list_entry])],
                                                  **opensignals_kwargs("line"))

                    # Update of line style.
                    if apply_opensignals_style is True:
                        style_line = {**opensignals_kwargs("line"),
                                      **_filter_keywords(Line, kwargs, warn_print=warn_print)}
                    else:
                        style_line = _filter_keywords(Line, kwargs, warn_print=warn_print)

                else:
                    raise RuntimeError("The shape of time and data inputs does not match.")
            else:
                raise RuntimeError("At least one of the list elements, specified in data or time, "
                                   "is not numeric.")

    # If this happen, then we receive as input a single list for time and data
    # (Single plot perspective).
    elif _is_instance(Number, data, condition="all") \
            and not _is_instance(bool, data, condition="any") \
            and _is_instance(Number, time, condition="all") \
            and not _is_instance(bool, time, condition="any"):
        grid_plot = False

        # Verification if all elements inside list are numbers.
        if _is_instance(Number, data, condition="all") \
                and not _is_instance(bool, data, condition="any") \
                and _is_instance(Number, time, condition="all") \
                and not _is_instance(bool, time, condition="any"):
            if len(time) == len(data):  # Shape verification
                fig_list.append(figure(title=title[0], y_axis_label=y_axis_label[0],
                                       x_axis_label=x_axis_label, **style_figure))
                if legend_label is not None:
                    fig_list[-1].line(time, data, legend_label=legend_label[0], **style_line)
                else:
                    fig_list[-1].line(time, data, **style_line)
            else:
                raise RuntimeError("The shape of time and data inputs does not match.")
        else:
            raise RuntimeError("At least one of the list elements, specified in data or time, is "
                               "not numeric.")

    else:
        raise RuntimeError("The input 'data' or/and 'time' does not have a valid format. It should "
                           "be a list of numbers or a list of lists.")

    # Application of the OpenSignals Style.
    if apply_opensignals_style is True:
        opensignals_style(fig_list)

    # Show of plots.
    if grid_plot is True:
        nbr_of_spaces = grid_lines * grid_columns
        nbr_of_figures = len(fig_list)

        if nbr_of_spaces >= nbr_of_figures > (grid_lines - 1) * grid_columns:
            # Organization of data accordingly to the number of rows and columns specified as input
            # arguments.
            grid_layout = []
            fig_nbr = 0
            for row in range(0, grid_lines):
                grid_layout.append([])
                for column in range(0, grid_columns):
                    if fig_nbr <= nbr_of_figures - 1:
                        grid_layout[-1].append(fig_list[fig_nbr])
                    else:
                        grid_layout[-1].append(None)

                    # Update of auxiliary variable.
                    fig_nbr += 1

            # Generation of the gridplot.
            grid = gridplot(grid_layout, **style_gridplot)

            if show_plot is True:
                show(grid)
            if save_plot is True:
                save(grid, file_name + ".html")
                #return HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')
        else:
            raise RuntimeError("The specified number of lines and columns for the grid plot is not "
                               "compatible.")

    else:
        if show_plot is True:
            show(fig_list[-1])
        if save_plot is True:
            save(fig_list[-1], file_name + ".html")
            #return HTML('<iframe width=100% height="' + str(fig_list[-1].plot_height) + '" src="generated_plots/' + file_name + '"></iframe>')

    if get_fig_list is True:
        return fig_list


def applyOpenSignalsStyle(graph):
    graph.background_fill_color = (242, 242, 242)
    toolbar = "right"
    graph.toolbar.active_scroll = graph.select_one(WheelZoomTool)
    graph.sizing_mode = 'scale_width'
    graph.height = 200
    graph.toolbar.logo = None
    graph.toolbar_location = toolbar
    graph.xaxis.axis_label = "Value"
    graph.yaxis.axis_label = "# Points"

    graph.xgrid.grid_line_color = (150, 150, 150)
    graph.ygrid.grid_line_color = (150, 150, 150)

    graph.xgrid.grid_line_dash = [2, 2]

    graph.xaxis.major_tick_line_color = "white"
    graph.xaxis.minor_tick_line_color = "white"
    graph.xaxis.axis_line_color = "white"
    graph.yaxis.major_tick_in = 0
    graph.yaxis.major_tick_out = 0

    graph.yaxis.major_tick_line_color = "white"
    graph.yaxis.minor_tick_line_color = "white"
    graph.yaxis.minor_tick_in = 0
    graph.yaxis.minor_tick_out = 0
    graph.yaxis.axis_line_color = (150, 150, 150)
    graph.yaxis.axis_line_dash = [2, 2]

    graph.yaxis.major_label_text_color = (88, 88, 88)
    graph.xaxis.major_label_text_color = (88, 88, 88)

    graph.ygrid.grid_line_dash = [2, 2]

    return graph

def dispersion(x_axis, y_axis, x_axis_label, y_axis_label, show_plot=True):
    """
    -----
    Brief
    -----
    This auxiliary function ensures a graphical representation of a dispersion graph.

    -----------
    Description
    -----------
    Through Bokeh tools, a dispersion plot can be generated using circles to present each
    point of the plot and removing the connection lines.

    ----------
    Parameters
    ----------
    x_axis : list
        List containing the x axis samples of the dispersion plot.

    y_axis : list
        List containing the y axis samples of the dispersion plot.

    x_axis_label : str
        A string containing the text to be presented near the x axis.

    y_axis_label : str
        A string containing the text to be presented near the y axis.

    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    Returns
    -------
    out : list
        List of Bokeh figures that compose the generated gridplot.
    """
    # List that store the figure handler
    list_figures_1 = []

    # Plotting of Tachogram
    list_figures_1.append(figure(x_axis_label=x_axis_label, y_axis_label=y_axis_label,
                                 **opensignals_kwargs("figure")))
    list_figures_1[-1].circle(x_axis, y_axis, **opensignals_kwargs("line"))

    # Apply Opensignals style
    opensignals_style(list_figures_1)

    # Show plot
    if show_plot is True:
        show(list_figures_1[-1])

    return list_figures_1


def opensignals_style(figure_list, grid_plot=None, toolbar="right"):
    """
    -----
    Brief
    -----
    Function used to automatically apply the OpenSignals graphical style to Bokeh plots.

    -----------
    Description
    -----------
    OpenSignals has its own graphical style and Bokeh plots function in an object oriented way.

    This function allows to apply the Opensignals graphical style to a set of Bokeh figures objects given as inputs.

    ----------
    Parameters
    ----------
    figure_list : bokeh figure/s
        The base object/s where the graphical functions will be applied.

    grid_plot : bokeh gridplot
        Contains the layout structure, where multiple bokeh figures are represented.

    toolbar : str
        String defining the toolbar position.

    """

    for fig in figure_list:
        fig.background_fill_color = (242, 242, 242)

        fig.toolbar.active_scroll = fig.select_one(WheelZoomTool)

        # Removal of unnecessary tools.
        figure_tools = fig.tools
        for tool in range(len(figure_tools) - 1, -1, -1):
            if not isinstance(figure_tools[tool], (type(PanTool()), type(BoxZoomTool()),
                                                   type(WheelZoomTool()), type(ResetTool()))):
                del figure_tools[tool]

        fig.sizing_mode = 'scale_width'
        fig.height = 200
        fig.toolbar.logo = None
        fig.toolbar_location = toolbar

        fig.xgrid.grid_line_color = (150, 150, 150)
        fig.ygrid.grid_line_color = (150, 150, 150)

        fig.xgrid.grid_line_dash = [2, 2]

        fig.xaxis.major_tick_line_color = "white"
        fig.xaxis.minor_tick_line_color = "white"
        fig.xaxis.axis_line_color = "white"
        fig.yaxis.major_tick_in = 0
        fig.yaxis.major_tick_out = 0

        fig.yaxis.major_tick_line_color = "white"
        fig.yaxis.minor_tick_line_color = "white"
        fig.yaxis.minor_tick_in = 0
        fig.yaxis.minor_tick_out = 0
        fig.yaxis.axis_line_color = (150, 150, 150)
        fig.yaxis.axis_line_dash = [2, 2]

        fig.yaxis.major_label_text_color = (88, 88, 88)
        fig.xaxis.major_label_text_color = (88, 88, 88)

        fig.ygrid.grid_line_dash = [2, 2]

    if isinstance(grid_plot, list):
        if grid_plot:
            for g_plot in grid_plot:
                g_plot.sizing_mode = 'scale_width'
                g_plot.height = 600


def opensignals_color_pallet():
    """
    -----
    Brief
    -----
    Function that automatically returns one of the available OpenSignals colors.

    -----------
    Description
    -----------
    OpenSignals has a set of predefined colours that can be applied in plots.

    This functions returns one of those colors as a hexadecimal code.

    Returns
    -------
    out : str
        Hexadecimal color.

    """

    return COLOR_LIST.__next__()


def opensignals_kwargs(obj):
    """
    -----
    Brief
    -----
    Function used to automatically apply the OpenSignals graphical style to the toolbar of Bokeh grid plots.

    -----------
    Description
    -----------
    Bokeh grid plots have numerous options in order to personalise the visual aspect and functionalities of plots.
    OpenSignals uses a specific graphical design that limits this options and unifies the aspect of its plots.

    This function applies the graphical aspect of the toolbar of OpenSignals to a given Bokeh figure object given as
    input.

    ----------
    Parameters
    ----------
    obj : str
        String that identifies if the kwargs will be the input of "figure" or "gridplot".

    Returns
    -------
    out : dict
        Dictionary with toolbar parameters.

    """

    out = None
    if obj == "figure":
        out = {}
    elif obj == "gridplot":
        out = {"toolbar_options": {"logo": None}, "sizing_mode": 'scale_width'}
    elif obj == "line":
        out = {"line_width": 2, "line_color": opensignals_color_pallet()}

    return out


def plot_android_sensor_timeline(sensor_data, report, plot_until_seconds=-1, line_thickness=1):

    """
    Function to visualise the sensor acquisition timeline of android sensors contained in the sensor data list. The time
    axes of the sensors are shifted to start at zero and converted to seconds.

    Parameters
    ----------
    sensor_data (list): A list containing the android sensor data (including the time axis). The list can be obtained by
                        calling the load_android_data(...) function.

    report (dict): A dictionary containing information on the sensors. The dictionary can be obtained by calling the
                   load_android_data(...) function.

    plot_until_seconds (int or float, optional): Int or float indicating how many seconds of the timeline should be plotted.
                                                 The value can be either -1 for plotting the entire timeline or a value > 0.
                                                 If not specified, then -1 is used.

    line_thickness (float, optional): Float indicating how thickness of the timeline lines. If not specified a thickness
                                      of 1 is used.

    Returns
    -------

    """

    # create new bokeh plot
    p = figure()

    # create a color iterator
    colors = itertools.cycle(palette)

    # for overriding y axis ticks
    label_dict = {}

    # get the earliest starting time
    start_time = numpy.min(report['starting times'])

    # cycle through the names (enumertaed to get list index)
    for i, name in enumerate(report['names']):

        # get the data
        data = sensor_data[i]

        # setup y axis labels
        label_dict[i + 1] = name

        # check for dimensionality
        if (data.ndim == 1):  # 1D array

            # get the time axis
            time_axis = data[:1]

        else:  # multidimensionl array

            # get the time axis
            time_axis = data[:, 0]

        # shift time axis to start at zero and convert to seconds
        time_axis = time_axis - start_time
        time_axis = time_axis * 1e-9

        # check for value of plot_until_seconds
        if (plot_until_seconds == -1):  # plot entire time line

            # get the number of samples from the size of the time axis
            num_samples = time_axis.size

        elif (plot_until_seconds > 0):

            # crop the time_axis to the correct specified time
            time_axis = time_axis[time_axis <= plot_until_seconds]

            # get the number of samples from the size of the time axis
            num_samples = time_axis.size

        else:  # invalid input

            raise IOError(
                'The value you entered for \'plot_until_seconds\' is invalid. Please specify either -1 for plotting the entire timeline or a value > 0.')

        # create y axis values for plot (ones array of length num_samples times the index number + 1)
        y_vals = numpy.ones((num_samples,), dtype=int) * (i + 1)

        # plot the sensor timeline depending on how many samples the user wants to plot
        # using colors iterator (size: 20 colors) when more than 20 sensors are plotted the colors are repeated
        p.segment(time_axis, y_vals - 0.25, time_axis, y_vals + 0.25, color=next(colors), line_width=line_thickness)

    # override y axis ticks
    p.yaxis.ticker = numpy.arange(1, len(sensor_data) + 1)
    p.yaxis.major_label_overrides = label_dict

    # add x axis label
    p.xaxis.axis_label = 'Time (s)'

    opensignals_style([p])  # apply biosignalsnotebooks style
    show(p)


# ==================================================================================================
# ================================= Private Functions ==============================================
# ==================================================================================================


def _check_validity_of_inputs(data, input_arg, input_name, grid_plot, dimension):
    """
    Function that verifies when an input ('input_arg') of function 'plot' has a valid structure.

    ----------
    Parameters
    ----------
    data : list or list of lists
        Structure with the data that will be plotted.

    input_arg : list or list of lists
        The input data to be verified.

    input_name : str
        Name of the input_arg variable.

    grid_plot : bool
        A flag that identifies when the input_arg is a matrix or not.

    dimension : int
        Level of verification in the matrix format structure.

    Returns
    -------
    out : list or list of lists
        Returns the same value as input_arg or a modified version.
    """
    if input_arg is not None:
        if grid_plot is True:
            if isinstance(input_arg, list):
                if numpy.shape(input_arg)[:dimension] != numpy.shape(data)[:dimension]:
                    raise RuntimeError("The shape of " + input_name + " does not match with data "
                                       "input.")

            else:
                raise RuntimeError("The specified data type of " + input_name +
                                   " field is not valid. Input must be a list.")
        else:
            if not isinstance(input_arg, str):
                raise RuntimeError("Taking into account that only one time-series had been "
                                   "specified at 'data', the " + input_name + " field must be a "
                                   "string")
    elif grid_plot is True:
        input_arg = numpy.ndarray(shape=numpy.shape(data)[:dimension], dtype=numpy.object)

    return input_arg

# 07/11/2018  20h28m :)
