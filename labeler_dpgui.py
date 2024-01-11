# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 19:07:53 2023

@author: Vasiliy Stepanov
"""

import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image, ImageDraw, ExifTags, ImageFont
import os
import matplotlib.pyplot as plt

dpg.create_context()
dpg.create_viewport(title = "Main Window", width = 1500, height = 1200)

dpg.setup_dearpygui()

label_colors = ((),(24,29,242,255),(196,47,166,255),(255,156,10,255),(190,62,52,255))

class FileSelector():
    def __init__(self, startdir = "F:/"):
        self.startdir = startdir
        self.activedir = startdir
        self.activefile = ""
        self.savedir = ""
        self.extensions = (".png",".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG")
        self.flist=[]

    def GetFileList(self):
        #print (self.activedir)
        fpath, files = self.checkpath(self.activedir)
        self.flist=[]
        if fpath:
            self.flist = [file for file in files if os.path.splitext(file)[1] in self.extensions]

        return self.flist

    def NextFile(self):
        if self.activefile != "":
            fcount = self.flist.index(self.activefile)
            if fcount<(len(self.flist)-1):
                self.activefile = self.flist[fcount+1]
        return

    def PrevFile(self):
        if self.activefile != "":
            fcount = self.flist.index(self.activefile)
            if fcount>0:
                self.activefile = self.flist[fcount-1]
        return

    def SetActiveFile(self, fname):
        self.activefile = fname

    def GetActiveFile(self):
        return (self.activedir + self.activefile)

    def SetActiveFolder(self, foldername):
        if foldername[-1] != "/" or foldername[-1] != "\\":
            foldername = foldername + "/"
        foldername = foldername.replace("\\","/")
        self.activedir = foldername

    def GetActiveFolder(self):
        return self.activedir

    def GetActiveFileName(self):
        return (self.activefile)

    def checkpath(self, path):

        try:
            tfiles = os.listdir(path)
        except OSError as err:
            path = ""
            tfiles = ""
        return path, tfiles


class Canvas():
    def __init__(self):

        self.canvas_size = (512,512)
        self.brush_size = 20
        self.labels_path = ""
        self.bg_image_path = ""
        self.bg_image_file_name = ""
        self.colors = ((0,255,78,255),(24,29,242,255),(196,47,166,255),(255,156,10,255),(190,62,52,255))
        self.current_label = 0
        self.view_scale = 2
        self.canvas = Image.new("RGBA", self.canvas_size)
        self.draw = ImageDraw.Draw(self.canvas)
        self.mode = 1 # 1 = Draw, 0 - Erase

    def SetLabelValue(self):
        pass

    def LoadBackground(self, file_name = ""):
        message = ""
        try:
            self.background_image = Image.open(file_name)
            message = f"{file_name} loaded succesfully!"
        except:
            self.background_image = Image.new("RGB", (512,512), color = (127,127,127,255))
            message = "Failed to open file"

        self.background_image.putalpha(255)

        if self.background_image.size != (512,512):
            self.background_image = self.background_image.resize((512,512))
            message = "Opened, but size did not match! Resized to 512x512"

        temp_image = self.background_image.resize((self.background_image.size[0]*self.view_scale,
                                                   self.background_image.size[1]*self.view_scale))
        return self.ConvertToPyGui(temp_image), message

    def SaveLabels(self, savedir = "", filename = ""):
        labels = Image.new("RGBA", (512,512))
        labels.paste((0,0,0,0),[0,0,512,512])
        composite = Image.alpha_composite(labels,self.canvas)
        fname = savedir + os.path.splitext(filename)[0]+ "_labels" + ".png"
        print (f"{fname} saved!")
        try:
            composite.save(fname)
            return f"{fname} Saved!"
        except:
            return "Failed to save!"

    def Clear(self):
        self.canvas.paste((0,0,0,0),[0,0,512,512])

    def Stroke(self, coords):
        x1 = coords[0]-self.brush_size/2
        y1 = coords[1]-self.brush_size/2
        if self.mode == 1:
            color = self.colors[self.current_label]
        else:
            color = (0,0,0,0)
        self.draw.ellipse((x1, y1, x1 + self.brush_size, y1+ self.brush_size), fill = color, outline = color)

    def SetColor(self, index):
        self.current_label = index

    def GetColor(self):
        return self.colors[self.current_label]

    def GetCanvasToPyGui(self):
        temp_image = self.canvas.resize((self.canvas.size[0]*self.view_scale,
                                         self.canvas.size[1]*self.view_scale))
        return self.ConvertToPyGui(temp_image)

    def ConvertToPyGui(self, image):
        return np.frombuffer(image.tobytes(), dtype=np.uint8) / 255.0

c = Canvas()
images = FileSelector()

with dpg.window(tag = "Primary", no_scrollbar = True, no_resize = True):
    with dpg.window(tag = "DrawWindow", width = 1030, height = 1062, pos = (10,10)):
        with dpg.drawlist(pos = (0,0), width = 1024, height = 1024, tag = "drawlist", show = True) as canvas:
            with dpg.draw_layer(tag = "background"):
                pass
            with dpg.draw_layer(tag = "mask"):
                pass
            with dpg.draw_layer(tag = "draw"):
                pass
            with dpg.draw_layer(tag = "mouse_cursor"):
                dpg.draw_circle((512,512),c.brush_size, tag = "cursor")
    with dpg.window(tag = "Options", width = 400, height = 205, pos = (1050,10)):
        with dpg.table(header_row=False, borders_innerH = True, borders_outerH = True,
                       borders_innerV = True, borders_outerV = True,
                       ):
            dpg.add_table_column(width = 75, width_fixed = True)
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_color_button(default_value = (0,255,78,255), width = 70, height = 30, label = "Label1", no_border = True, tag = "button1")
                dpg.add_text("1 - Small round skin defects")
            with dpg.table_row():
                dpg.add_color_button(default_value = (24,29,242,255), width = 70, height = 30, label = "Label2", no_border = True, tag = "button2")
                dpg.add_text("2 - Long and stretched skin defects")
            with dpg.table_row():
                dpg.add_color_button(default_value = (196,47,166,255), width = 70, height = 30, label = "Label3", no_border = True, tag = "button3")
                dpg.add_text("3 - Folds, creases")
            with dpg.table_row():
                dpg.add_color_button(default_value = (255,156,10,255), width = 70, height = 30, label = "Label4", no_border = True, tag = "button4")
                dpg.add_text("4 - Body hairs")
            with dpg.table_row():
                dpg.add_color_button(default_value = (190,62,52,255), width = 70, height = 30, label = "Label5", no_border = True, tag = "button5")
                dpg.add_text("4 - Reserved")



labels_texture = c.GetCanvasToPyGui()
bg_texture, msg = c.LoadBackground()

with dpg.texture_registry():
    dpg.add_dynamic_texture(1024, 1024, labels_texture, tag="labels")
    dpg.add_dynamic_texture(1024, 1024, bg_texture, tag="background_image")

dpg.draw_image("background_image", pmin = (0,0), pmax =(1024, 1024),
               uv_min=(0.0, 0,0), uv_max=(1, 1), tag = "bg_image", parent = "background")


dpg.draw_image("labels", pmin = (0,0), pmax =(1024, 1024),
               uv_min=(0.0, 0,0), uv_max=(1, 1), tag = "labels_image", parent = "mask")





strokes = []

#%% Callbacks
def FolderSelection_callback(sender, app_data):
    images.SetActiveFolder(app_data.get("file_path_name"))
    dpg.configure_item("filelist", items = images.GetFileList())
    dpg.configure_item("folder_selection", default_path = images.GetActiveFolder())
    dpg.configure_item("dirbutton", label = images.GetActiveFolder())
    #print (img_list.GetActiveFolder())

def SaveFolder_callback(sender, app_data):

    foldername = app_data.get("file_path_name")
    if foldername[-1] != "/" or foldername[-1] != "\\":
        foldername = foldername + "/"
    foldername = foldername.replace("\\","/")
    images.savedir = foldername
    c.labels_path = foldername
    dpg.configure_item("savefolder_selection", default_path = images.savedir)
    dpg.configure_item("targetdir", label = images.savedir)

def cancel_callback(sender, app_data):
    pass

def MoveCursor(sender, data):
    pos = dpg.get_drawing_mouse_pos()
    dpg.configure_item("cursor", center = pos)

def ReDraw():
    labels_texture = c.GetCanvasToPyGui()
    for i in strokes:
        dpg.delete_item(i)
    strokes.clear()
    dpg.set_value("labels", labels_texture)

def ReDrawBG(filename):
    strokes.clear()
    c.Clear()
    bg_texture, msg = c.LoadBackground(filename)
    dpg.set_value("background_image", bg_texture)
    dpg.configure_item("message_window", default_value = msg)

def Draw(sender, data):
    if dpg.is_item_hovered("drawlist"):
        pos = dpg.get_drawing_mouse_pos()
        if c.mode == 1:
            color = c.GetColor()
        else:
            color = (127,127,127,255)

        c.Stroke((pos[0]//2, pos[1]//2))
        strokes.append(dpg.draw_circle((pos[0], pos[1]), c.brush_size,
                                       parent = "draw",
                                       color = color, fill = color))

def KeyDown(sender, key):
    print (key)
    if key == 69:
        c.mode = 0
    if key == 66 or key == 87:
        c.mode = 1
    if key >= 49 and key <=53:
        c.SetColor(key-49)
    if key == 83:
        if images.savedir != "":
            msg = c.SaveLabels(images.savedir, images.GetActiveFileName())
            dpg.configure_item("message_window", default_value = msg)

    if key == 8:
        c.Clear()
        ReDraw()

    if key == 39:
        if images.GetActiveFileName() !="":
            images.NextFile()
            load_new_image(0, images.GetActiveFileName())

    if key == 37:
        if images.GetActiveFileName() !="":
            images.PrevFile()
            load_new_image(0, images.GetActiveFileName())

def BrushSize(sender, key):
    if dpg.is_item_hovered("drawlist"):
        step = 5
        c.brush_size = c.brush_size + key * step
        if c.brush_size < 1:
            c.brush_size = 1
        if c.brush_size > 512:
            c.brush_size = 512
        dpg.configure_item("cursor", radius = (c.brush_size/2 * c.view_scale))

def load_new_image(sender, data):

    images.SetActiveFile(data)

    fname = images.GetActiveFolder()+images.GetActiveFileName()
    ReDrawBG(fname)
    ReDraw()
    pass

def SaveFolder_callback(sender, app_data):

    foldername = app_data.get("file_path_name")
    if foldername[-1] != "/" or foldername[-1] != "\\":
        foldername = foldername + "/"
    foldername = foldername.replace("\\","/")
    images.savedir = foldername
    dpg.configure_item("savefolder_selection", default_path = images.savedir)
    dpg.configure_item("savedirbutton", label = images.savedir)

#%%

with dpg.window(tag = "Files", width = 400, height = 737, pos = (1050,225),
                no_title_bar = True, no_move = True, no_collapse = True, no_close = True, no_scrollbar = True):
    dpg.add_button(label=images.activedir, callback=lambda: dpg.show_item("folder_selection"), width = 400, tag = "dirbutton")
    dpg.add_listbox(items = images.GetFileList(), callback = load_new_image, num_items = 40, tag = "filelist", width = 495)
    dpg.add_file_dialog(directory_selector=True, show=False,
                        callback=FolderSelection_callback, tag="folder_selection",
                        cancel_callback=cancel_callback,
                        width = 500, height = 800,
                        default_path = images.GetActiveFolder(),
                        modal = True,
                        )

with dpg.window(tag = "SaveFolder", width = 400, height = 100, pos = (1050,972),
                no_title_bar = True, no_move = True, no_collapse = True, no_close = True, no_scrollbar = True):

    dpg.add_button(label=images.activedir, callback=lambda: dpg.show_item("savefolder_selection"), width = 400, tag = "savedirbutton")

    dpg.add_file_dialog(directory_selector=True, show=False,
                        callback=SaveFolder_callback, tag="savefolder_selection",
                        cancel_callback=cancel_callback,
                        width = 500, height = 800,
                        default_path = images.savedir,
                        modal = True,
                        )

    dpg.add_text("Select source and target folders!\nOnly JPG and PNG 512x512 allowed\nLeft, Right - navigate, W,B - brush\nE - Erase, S - Save", tag = "message_window")


with dpg.handler_registry():
    dpg.add_mouse_move_handler(callback=MoveCursor)
    dpg.add_mouse_down_handler(button=dpg.mvMouseButton_Left, callback = Draw)
    dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback = ReDraw)
    dpg.add_mouse_wheel_handler(callback=BrushSize)
    dpg.add_key_press_handler(key=- 1, callback = KeyDown)

print ("Keys: 1,2,3,4,5 = Classes\nE - Erase, W - Brush, Backspace - erase all")

dpg.show_viewport()
dpg.set_primary_window("Primary", True)
dpg.start_dearpygui()

dpg.destroy_context()