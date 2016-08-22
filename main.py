import sys
from math import pi

from bokeh.models.ranges import FactorRange
from bokeh.models.widgets import Panel, Tabs
from bokeh.plotting import figure, output_file, show
from format_data import (attrs_to_sort_tuple, attrs_to_str, name_to_attrs,
                         read_data)
from pprint import pprint

input_data = {}


def tagger_sort(x):
    return attrs_to_sort_tuple(name_to_attrs(x))


def prettify_name(x):
    return attrs_to_str(name_to_attrs(x))

input_data = read_data(sys.argv[1:])
languages = input_data.keys()
pprint(input_data)

sorted_tagger_names = {}
all_tagger_names = set()
for lang in languages:
    sorted_tagger_names[lang] = []
    for tagger in input_data[lang].keys():
        tagger_data = input_data[lang][tagger]
        if isinstance(tagger_data, int):
            continue
        sorted_tagger_names[lang].append(tagger)
        all_tagger_names.add(tagger)
    sorted_tagger_names[lang].sort(key=tagger_sort)

all_tagger_name = sorted(all_tagger_names, key=tagger_sort)

tabs = []

VERY_SMALL = 0.00001

x_range = FactorRange(factors=[prettify_name(x) for x in all_tagger_name])
y_range = (0.59, 1.01)

for lang in languages:
    lang_data = input_data[lang]

    # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    tagger_names = sorted_tagger_names[lang]
    mins = []
    means = []
    stddevs = []
    lowers = []
    uppers = []
    maxes = []
    taggers = []
    for tagger in tagger_names:
        tagger_data = lang_data[tagger]
        #taggers.append(prettify_name(tagger))
        taggers.append(tagger)
        if hasattr(tagger_data[1], "__getitem__"):
            mins.append(tagger_data[1][0])
            means.append(tagger_data[1][2])
            stddevs.append(tagger_data[1][3])
            lowers.append(tagger_data[1][2] - tagger_data[1][3])
            uppers.append(tagger_data[1][2] + tagger_data[1][3])
            maxes.append(tagger_data[1][1])
        else:
            mins.append(tagger_data[1])
            means.append(tagger_data[1])
            stddevs.append(0)
            lowers.append(tagger_data[1])
            uppers.append(tagger_data[1])
            maxes.append(tagger_data[1])

    p = figure(
        title="",
        x_range=x_range,
        y_range=y_range,
        plot_width=20 * len(all_tagger_names),
        tools='crosshair,hover,save,reset,ywheel_zoom,ypan,resize')
    p.yaxis.bounds = (0.6, 1.0)
    x_range = p.x_range
    y_range = p.y_range

    # stems
    p.segment(taggers, maxes, taggers, uppers, line_width=1, line_color="black")
    p.segment(taggers, mins, taggers, lowers, line_width=1, line_color="black")

    # boxes
    p.rect(taggers, means, 0.7, [q * 2 for q in stddevs],
           fill_color="#eeeeee", line_width=1, line_color="black")
    p.rect(taggers, means, 0.7, VERY_SMALL, line_width=1, line_color="black")

    # whiskers (almost-0 height rects simpler than segments)
    p.rect(taggers, mins, 0.2, VERY_SMALL, line_width=1, line_color="black")
    p.rect(taggers, maxes, 0.2, VERY_SMALL, line_width=1, line_color="black")

    # Grid/Axes
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    #p.xaxis.major_label_text_font_size="12pt"
    p.xaxis.major_label_orientation = pi / 2

    tabs.append(Panel(child=p, title=lang))

output_file("taggers.html", title="Apertium taggers comparison")

show(Tabs(tabs=tabs))
