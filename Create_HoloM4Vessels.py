#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from Tkinter import *
import ttk
import os, sys


def setWellParameters(well, name="", radius=1, height=0, width=1, y_pos=0, x_pos=0, areatype=2, type=2):
	well.set("Name", name) # Name of Container, used in "Capture pattern setup"
	well.set("Radius", str(radius).replace('.', ','))
	well.set("Height", str(height).replace('.', ','))
	well.set("Width", str(width).replace('.', ','))
	well.set("Y", str(y_pos).replace('.', ','))
	well.set("X", str(x_pos).replace('.', ','))
	well.set("Number", "1")
	well.set("AreaType", str(areatype))
	well.set("Type", str(type))


def createPlateWells(vessel):
	for row in range(WELL_NUMBER_Y.get()):
		for column in range(WELL_NUMBER_X.get()):
			well_parameters = {
				'name': WELL_ROWNAME[row] + str(column +1),
				'height': 0,
				'width': 1,
				'y_pos': WELL_DIST_EDGE_Y.get() + row * WELL_DIST_Y.get(),
				'x_pos': PLATE_SIZE_X - WELL_DIST_EDGE_X.get() - column * WELL_DIST_X.get(),
				'type': 2,
				'radius': WELL_RADIUS.get(),
				'areatype': 2}
			well = ET.SubElement(vessel, "VesselObject")
			setWellParameters(well, **well_parameters)

			well_parameters['radius'] = WELL_RADIUS.get() - RIM_NOTUSABLE.get()
			well_parameters['areatype'] = 1
			well = ET.SubElement(vessel, "VesselObject")
			setWellParameters(well, **well_parameters)

def createMicroslideWells(vessel):
	for n in range(3):
		slide_parameters = {
				'name': WELL_ROWNAME[n],
				'height': 76,
				'width': 26,
				'y_pos': 5,
				'x_pos': 11 + 40 * n,
				'type': 1,
				'radius': 1,
				'areatype': 2}

		slide = ET.SubElement(vessel, "VesselObject")
		setWellParameters(slide, **slide_parameters)

		for well_number in range(WELL_NUMBER_X.get() * WELL_NUMBER_Y.get()):
			outerwell_parameters = {
				'name': WELL_ROWNAME[n] + str(well_number + 1),
				'height': WELL_HEIGHT.get(),
				'width': WELL_WIDTH.get(),
				'y_pos': 5 + WELL_TOP_SPACING.get() + WELL_WALL.get() + (well_number // WELL_NUMBER_X.get()) * (WELL_WALL.get() + WELL_HEIGHT.get()),
				'x_pos': 11 + 40 * n + WELL_WALL.get() + (well_number % WELL_NUMBER_X.get()) * (WELL_WALL.get() + WELL_WIDTH.get()),
				'type': 1,
				'radius': 1,
				'areatype': 2}
			outerwell = ET.SubElement(vessel, "VesselObject")
			setWellParameters(outerwell, **outerwell_parameters)


			innerwell_parameters = {
				'name': WELL_ROWNAME[n] + str(well_number + 1),
				'height': WELL_HEIGHT.get() - 2 * RIM_NOTUSABLE.get(),
				'width': WELL_WIDTH.get() - 2 * RIM_NOTUSABLE.get(),
				'y_pos': 5 + WELL_TOP_SPACING.get() + WELL_WALL.get() + RIM_NOTUSABLE.get() + (well_number // WELL_NUMBER_X.get()) * (WELL_WALL.get() + WELL_HEIGHT.get()),
				'x_pos': 11 + 40 * n + WELL_WALL.get() + RIM_NOTUSABLE.get() + (well_number % WELL_NUMBER_X.get()) * (WELL_WALL.get() + WELL_WIDTH.get()),
				'type': 1,
				'radius': 1,
				'areatype': 1}
			innerwell = ET.SubElement(vessel, "VesselObject")
			setWellParameters(innerwell, **innerwell_parameters)



# pretty prints .xml
def indent(elem, level=0): # indent function from: http://effbot.org/zone/element-lib.htm (Fredrik Lundh)
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

#build the whole Template element tree including header, pretty print it and and save it to disk, bound to the "Create button"
def createTemplate():
	template_root = ET.Element("Vessels")
	vessel = ET.SubElement(template_root, "Vessel", RefPosY=str(OFFSET_Y), RefPosX=str(OFFSET_X), Name= VESSEL_NAME.get())
	frame_parameters = {
				'name': VESSEL_NAME.get(),
				'height': PLATE_SIZE_Y + OFFSET_Y,
				'width': PLATE_SIZE_X + OFFSET_X,
				'y_pos': 0,
				'x_pos': 0,
				'type': 1,
				'radius': 1,
				'areatype': 2}
	frame = ET.SubElement(vessel, "VesselObject")
	setWellParameters(frame, **frame_parameters)

	if CREATE_PLATE_TEMPLATE.get():
		createPlateWells(vessel)
	else:
		createMicroslideWells(vessel)

	tree = ET.ElementTree(template_root)
	indent(template_root)

	try:
		if not os.path.exists(SAVE_DIRECTORY.get()):
			os.makedirs(SAVE_DIRECTORY.get())
		if str(SAVE_DIRECTORY).endswith(os.sep):
			tree.write(SAVE_DIRECTORY.get() + VESSEL_NAME.get() + ".xml")
		else:
			tree.write(SAVE_DIRECTORY.get() + os.sep + VESSEL_NAME.get() + ".xml")
	except Exception as e:
		print(str(e))
	else:
		print('Template successfully created!')

#Create a Description, entry field and optional unit entity
def createEntry(parent_frame, label_text, store_input, entrywidth, grid_column, grid_row, unit=''):
	label = ttk.Label(parent_frame, text=label_text)
	label.grid(column=grid_column, row=grid_row, sticky=E)
	entry = ttk.Entry(parent_frame, textvariable=store_input, width=entrywidth)
	entry.grid(column=grid_column + 1, row=grid_row)
	entry.bind('<Return>', enterPressed)
	if unit:
		unit_label = ttk.Label(parent_frame, text=unit)
		unit_label.grid(column=grid_column + 2, row=grid_row)
		return label, entry, unit_label
	else:
		return label, entry

#Create carrier outline for Plates or Slides
def create_Layout(parent, is_slide):
	widget = Canvas(parent, width=600, height=400)
	widget.grid(column=0, row=0)
	widget.columnconfigure(0, weight=1)
	widget.rowconfigure(0, weight=1)
	widget.create_rectangle(COORD_OFFSET_X, COORD_OFFSET_Y, COORD_OFFSET_X + PLATE_SIZE_X * LAYOUT_SCALE, COORD_OFFSET_Y + PLATE_SIZE_Y * LAYOUT_SCALE, fill='black')
	if is_slide:
		drawing_offset_x = (600 - PLATE_SIZE_X * LAYOUT_SCALE) / 2
		drawing_offset_y = (400 - PLATE_SIZE_Y * LAYOUT_SCALE) / 2
		slide_width = 26 * LAYOUT_SCALE
		slide_height = 76 * LAYOUT_SCALE
		dist_frame_y = 5 * LAYOUT_SCALE
		dist_frame_x = 11 * LAYOUT_SCALE
		distance_slides = 40 * LAYOUT_SCALE
		for n in range(3):
			x_coord = drawing_offset_x + dist_frame_x + n * distance_slides
			y_coord = drawing_offset_y + dist_frame_y
			widget.create_rectangle(x_coord, y_coord, x_coord + slide_width, y_coord + slide_height, fill='darkgrey')
	return widget

#Create the actual Plate wells in the layout
def create_PlateWell_Layout(parent):
	drawing_offset_x = (600 - PLATE_SIZE_X * LAYOUT_SCALE) / 2
	drawing_offset_y = (400 - PLATE_SIZE_Y * LAYOUT_SCALE) / 2
	for row in range(WELL_NUMBER_Y.get()):
		for column in range(WELL_NUMBER_X.get()):
			outer_radius = WELL_RADIUS.get() * LAYOUT_SCALE
			inner_radius = (WELL_RADIUS.get() - RIM_NOTUSABLE.get()) * LAYOUT_SCALE
			name = WELL_ROWNAME[row] + str(column + 1)
			x_center = drawing_offset_x + (WELL_DIST_EDGE_X.get() + column * WELL_DIST_X.get()) * LAYOUT_SCALE
			y_center = drawing_offset_y + (WELL_DIST_EDGE_Y.get() + row * WELL_DIST_Y.get()) * LAYOUT_SCALE

			parent.create_oval(x_center - outer_radius, y_center - outer_radius, x_center + outer_radius, y_center + outer_radius, fill='lightgrey')
			parent.create_oval(x_center - inner_radius, y_center - inner_radius, x_center + inner_radius, y_center + inner_radius, fill='white')

#Create the actual Slide wells in the layout
def create_SlideWell_Layout(parent):
	drawing_offset_x = (600 - PLATE_SIZE_X * LAYOUT_SCALE) / 2
	drawing_offset_y = (400 - PLATE_SIZE_Y * LAYOUT_SCALE) / 2
	dist_frame_y = 5 * LAYOUT_SCALE
	dist_frame_x = 11 * LAYOUT_SCALE
	distance_slides = 40 * LAYOUT_SCALE
	for n in range(3):
		height = WELL_HEIGHT.get() * LAYOUT_SCALE
		width = WELL_WIDTH.get() * LAYOUT_SCALE
		rim = RIM_NOTUSABLE.get() * LAYOUT_SCALE

		for well_number in range(WELL_NUMBER_X.get() * WELL_NUMBER_Y.get()):
			name = WELL_ROWNAME[n] + str(well_number + 1),
			y_pos = drawing_offset_y + dist_frame_y + (WELL_TOP_SPACING.get() + WELL_WALL.get() + (well_number // WELL_NUMBER_X.get()) * (WELL_WALL.get() + WELL_HEIGHT.get())) * LAYOUT_SCALE
			x_pos = drawing_offset_x + dist_frame_x + n * distance_slides + (WELL_WALL.get() + (well_number % WELL_NUMBER_X.get()) * (WELL_WALL.get() + WELL_WIDTH.get())) * LAYOUT_SCALE
			parent.create_rectangle(x_pos, y_pos, x_pos + width, y_pos + height, fill='lightgrey')
			parent.create_rectangle(x_pos + rim, y_pos + rim, x_pos + width - rim, y_pos + height - rim, fill='white')


#Functions for the buttons
def createButton(parent_frame, label_text, command_call, grid_column):
	b = ttk.Button(parent_frame, text=label_text, command=command_call)
	b.grid(column=grid_column, row=0, sticky=E)
	return b

def cancelCreation():
	root.destroy()

def enterPressed(event):
	updateLayouts()

# Creates outline layouts, the recreates the appropriate layout
def updateLayouts():
	plate_layout = create_Layout(plate_layout_frame, False)
	slide_layout = create_Layout(slide_layout_frame, True)
	if CREATE_PLATE_TEMPLATE.get():
		create_PlateWell_Layout(plate_layout)
	else:
		create_SlideWell_Layout(slide_layout)

# Disables not selected Tk widgets, Checkbutton in template selection
def selectActiveTemplate():
	if CREATE_PLATE_TEMPLATE.get():
		for child in plate_template_frame.winfo_children():
			set_widget_state(child, 'normal')
		for child in slide_template_frame.winfo_children():
			set_widget_state(child, 'disable')
	else:
		for child in slide_template_frame.winfo_children():
			set_widget_state(child, 'normal')
		for child in plate_template_frame.winfo_children():
			set_widget_state(child, 'disable')
	updateLayouts()

# Tk frames can't be disabled, recursive call walks to associated child elements
def set_widget_state(parent, mode):
	if parent.winfo_class() == 'TFrame':
		for child in parent.winfo_children():
			set_widget_state(child, mode)
	else:
		parent.configure(state=mode)


root = Tk()
root.title("Create templates for the Holomonitor M4 stage")

# Global parameters - default values in mm
#predefined
PLATE_SIZE_X = 128	# length of standard plate format
PLATE_SIZE_Y = 85	# width of standard plate format
OFFSET_X = -8		# offsets used by PHI
OFFSET_Y = -5		# offsets used by PHI
LAYOUT_SCALE = 4 	# 4px/mm
COORD_OFFSET_X, COORD_OFFSET_Y = (600 - PLATE_SIZE_X * LAYOUT_SCALE) / 2, (400 - PLATE_SIZE_Y * LAYOUT_SCALE) / 2
WELL_ROWNAME = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

#Tk Values for interaction
CREATE_PLATE_TEMPLATE = BooleanVar()
CREATE_PLATE_TEMPLATE.set(True)
VESSEL_NAME = StringVar()
VESSEL_NAME.set("Please Enter the Name of the Template")
SAVE_DIRECTORY = StringVar()
SAVE_DIRECTORY.set('D:' + os.sep)
RIM_NOTUSABLE = DoubleVar()								# not usable area from edge
WELL_NUMBER_X = IntVar()
WELL_NUMBER_Y = IntVar()

# Plate layout (measurements in mm)
WELL_DIST_EDGE_X = DoubleVar()  							# distance of center of first well from edge
WELL_DIST_EDGE_Y = DoubleVar()
WELL_DIST_X = DoubleVar() 									# distance between wells
WELL_DIST_Y = DoubleVar()
WELL_RADIUS = DoubleVar() 									# radius of a circular well

# Slide layout (measurements in mm)
WELL_HEIGHT = DoubleVar()									# y-extension of a rectangular well
WELL_WIDTH = DoubleVar()									# x-extension of a rectangular well
WELL_WALL = DoubleVar()									# thickness of a well wall
WELL_TOP_SPACING = DoubleVar()								# start of the first wall from edge


#Create main frame
mainframe = ttk.Frame(root, padding="3 3 12 12",)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

#Subframes for template selection, settings, layout and buttons
select_template_frame = ttk.Frame(mainframe, padding="3 3 12 12")
select_template_frame.grid(column=0, row=0, columnspan=2)
select_template_frame.columnconfigure(0, minsize=600)
select_template_frame.columnconfigure(1, minsize=600)

generic_settings_frame = ttk.Frame(mainframe, padding="3 3 12 12")
generic_settings_frame.grid(column=0, row=1, columnspan=2, sticky=(W,E))

plate_template_frame = ttk.Frame(mainframe, padding="3 3 12 12")
plate_template_frame.grid(column=0, row=2)
slide_template_frame = ttk.Frame(mainframe, padding="3 3 12 12")
slide_template_frame.grid(column=1, row=2)

control_frame = ttk.Frame(mainframe)
control_frame.grid(column=0, row=3, columnspan=2)

#Create Checkbuttons for template selection
create_plate_template = ttk.Radiobutton(select_template_frame, text="Create a Plate template", variable=CREATE_PLATE_TEMPLATE, value=True, command=selectActiveTemplate)
create_plate_template.grid(column=0, row=0, sticky=W)
create_slide_template = ttk.Radiobutton(select_template_frame, text="Create a Slide template", variable=CREATE_PLATE_TEMPLATE, value=False, command=selectActiveTemplate)
create_slide_template.grid(column=1, row=0, sticky=W)

#Create the labeled entry fields
#Generic settings
vessel_name_text, vessel_name = createEntry(generic_settings_frame, 'Name: ', VESSEL_NAME, 40, 0, 0)
save_dir_text, save_dir = createEntry(generic_settings_frame, 'Save directory: ', SAVE_DIRECTORY, 40, 0, 1)
well_number_x_text, well_number_x = createEntry(generic_settings_frame, '   Number of wells in X: ', WELL_NUMBER_X, 3, 2, 0)
well_number_y_text, well_number_y = createEntry(generic_settings_frame, '   Number of wells in Y: ', WELL_NUMBER_Y, 3, 2, 1)
rim_text, rim, _ = createEntry(generic_settings_frame, '   Width of unusable rim: ', RIM_NOTUSABLE, 3, 4, 0, 'mm')

#Plate settings
plate_settings_frame = ttk.Frame(plate_template_frame, padding="3 3 12 12")
plate_settings_frame.grid(column=0, row=2, sticky=W)
edge_x_text, edge_x, _ = createEntry(plate_settings_frame, 'Distance of first well center from edge in X: ', WELL_DIST_EDGE_X, 5, 0, 0, 'mm')
edge_y_text, edge_y, _ = createEntry(plate_settings_frame, 'Distance of first well center from edge in Y: ', WELL_DIST_EDGE_Y, 5, 0, 1, 'mm')
well_radius_text, well_radius, _ = createEntry(plate_settings_frame, '   Radius of wells: ', WELL_RADIUS, 5, 0, 2, 'mm')
well_dist_x_text, well_dist_x, _ = createEntry(plate_settings_frame, '   Distance between wells in X: ', WELL_DIST_X, 5, 3, 0, 'mm')
well_dist_y_text, well_dist_y, _ = createEntry(plate_settings_frame, '   Distance between wells in Y: ', WELL_DIST_Y, 5, 3, 1, 'mm')

#Slide settings
slide_settings_frame = ttk.Frame(slide_template_frame, padding="3 3 12 12")
slide_settings_frame.grid(column=1, row=2, sticky=W)
top_space_text, top_space, _ = createEntry(slide_settings_frame, 'Distance of first wall from the top: ', WELL_TOP_SPACING, 5, 0, 0, 'mm')
wall_thickness_text, wall_thickness, _ = createEntry(slide_settings_frame, 'Thickness of walls between wells: ', WELL_WALL, 5, 0, 1, 'mm')
well_width_text, well_width, _ = createEntry(slide_settings_frame, '   Width of wells : ', WELL_WIDTH, 5, 3, 0, 'mm')
well_height_text, well_height, _ = createEntry(slide_settings_frame, '   Height of wells : ', WELL_HEIGHT, 5, 3, 1, 'mm')
empty_line = ttk.Label(slide_settings_frame, text="")
empty_line.grid(column=0, row=2, columnspan=6)

#Create the frames for the layouts
plate_layout_frame = ttk.Frame(plate_template_frame, padding="3 3 12 12")
plate_layout_frame.grid(column=0, row=3)
plate_layout = create_Layout(plate_layout_frame, False)
create_PlateWell_Layout(plate_layout)

slide_layout_frame = ttk.Frame(slide_template_frame, padding="3 3 12 12")
slide_layout_frame.grid(column=1, row=3)
slide_layout = create_Layout(slide_layout_frame, True)

#Create the buttons
ok_button = createButton(control_frame, 'Create', createTemplate, 0)
cancel_button = createButton(control_frame, 'Cancel', cancelCreation, 1)
update_button = createButton(control_frame, 'Update', updateLayouts, 2)

selectActiveTemplate()
root.mainloop()
