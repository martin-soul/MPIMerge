
"""
Created on Mon Jan  9 16:48:23 2023

@author: Martin Duša
"""
import tkinter as tk
import tkinter.messagebox
import customtkinter
import numpy as np
import os
import time

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.image import imread
from pydicom import dcmread
from core import Load,Path,GetParam,Merge,DCMHeader,ImageEnhancement
from customwidgets import CTkComboboxDialog

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue") # Themes: "blue" (standard), "green", "dark-blue"

class main(ImageEnhancement):
    def __init__(self):
        
        self.rec = []
        self.img =[]
        self.font_size= 13
        self.to_slider = 100
        self.on_name = 'RUN_-1'
        self.moving=False
        self.position_cache = {}
        self.contrast_cache = {}
        self.brightness_cache = {}
        
        #Build main window
        self.main_window = customtkinter.CTk()
        self.main_window.title('VOMMPI')
        self.main_window.iconbitmap("merge.ico")
        self.main_window.grid_rowconfigure(0, weight=2)
        self.main_window.grid_columnconfigure(0, weight=1)


        self.desired_font = tkinter.font.Font(family = 'Arial black', size = 12,weight = 'normal')
        
        self.dcm = DCMHeader()
        self.dcm_header_json = self.dcm.get_default_tk()
        self.dcm_header = {
            'Rows':0,
            'Columns':0,
            'NumberOfFrames':0,
            'PixelRepresentation':0,
            'PixelData':0,
          
            }
        
        #def variable
        self.path_exp=tk.StringVar()    #variable with path to experiment 
        self.path_dcm_save = tk.StringVar()
        self.path_dcm_save.set(os.getcwd())
        self.current_show = tk.IntVar ()
        self.contrast_value= tk.DoubleVar()
        self.bright_value = tk.DoubleVar()
        
        self.dict_param = {
            'Patch size x' : tk.StringVar(),
            'Patch size y' : tk.StringVar(),
            'Patch size z' : tk.StringVar(),
            'Patch layout x' : tk.StringVar(),
            'Patch layout y' : tk.StringVar(),
            'Patch layout z' : tk.StringVar(),
            'Patch overlap' : tk.StringVar(),
            }
        

     
        #build tabs bar
        self.tab_m = self.tab_main()
        
        #build merge page 
        self.frames_rec = self.frames_merge()
        self.labels_rec = self.labels_merge()
        self.entry_rec = self.entry_merge() 
        self.button_rec = self.button_merge()
        self.optins_rec = self.options_merge()
        self.slider_rec = self.slider_merge()
        self.slider_tool =self.slider_tool_merge()
        #build dcm setting page
        self.frames_dcm = self.dcm_setting_frames()
        self.dcm_entry = self.dcm_header_entry()
        self.dcm_label = self.dcm_header_label()
        self.dcm_button = self.dcm_header_button()
# =============================================================================
#         #build visual setting page
#         self.frame_vis = self.visual_setting_frames()
# =============================================================================
        
        self.tab_show()
        self.count=0
        self.label_tool_init()
    
    
    def tab_main(self):
        self.TopTab_tabview=customtkinter.CTkTabview(self.main_window, 
                                                     
                                                     
                                                     )
        self.TopTab_tabview.grid(row =0, 
                                 column =0, 
                                 pady=4,
                                 padx=4,
                                 sticky="nsew")
        
        self.TopTab_tabview.grid_rowconfigure(0, weight=0)
        self.TopTab_tabview.grid_columnconfigure(0, weight=1)
        
        self.TopTab_tabview.add("Merge Sequence")
        self.TopTab_tabview.add("Dcm header setting")
        

        
        self.TopTab_tabview.tab("Merge Sequence").grid_rowconfigure(0, weight=1)
        self.TopTab_tabview.tab("Merge Sequence").grid_rowconfigure(1, weight=20)
            
        
        self.TopTab_tabview.tab("Merge Sequence").grid_columnconfigure(0, weight=1)                                                                       
        self.TopTab_tabview.tab("Merge Sequence").grid_columnconfigure(1, weight=10)
        self.TopTab_tabview.tab("Merge Sequence").grid_columnconfigure(2, weight=5)
        
        self.TopTab_tabview.tab("Dcm header setting").grid_rowconfigure(1, weight=1)
        self.TopTab_tabview.tab("Dcm header setting").grid_columnconfigure(0, weight=1)
        
# =============================================================================
#         self.TopTab_tabview.add("Visual settings")
#         self.TopTab_tabview.tab("Visual settings").grid_columnconfigure(0, weight=1)
#         self.TopTab_tabview.tab("Visual settings").grid_rowconfigure(0, weight=1)
#         
# =============================================================================
    def tab_show(self):
        
        self.Show_tab=customtkinter.CTkTabview(self.Show_frame)
        
        self.Show_tab.grid(row =0, 
                            column = 0,
                            columnspan = 2,
                            pady=4,
                            padx=4,
                            sticky="nsew")
        
        

        
        
        for idx,(records) in enumerate(self.rec):
            
            self.Show_tab.add(records)
            self.Show_tab.tab(records).grid_rowconfigure(0, weight=1)
            self.Show_tab.tab(records).grid_columnconfigure(0, weight=1)
            records_nmr= records.split('_')
            if not records in self.position_cache:
                self.position_cache.update({records:0})
                self.brightness_cache.update({records:0}) 
                self.contrast_cache.update({records:1})
            self.show_seq(records,int(records_nmr[-1]))
            
        
    
    def frames_merge(self):

        #Frame for selection directory to experiment
        self.SelectDir_frame = customtkinter.CTkFrame(self.TopTab_tabview.tab("Merge Sequence"), 
                                                   corner_radius=4
                                                   )
        self.SelectDir_frame.grid(row =0, 
                                    column = 0, 
                                    columnspan = 3,
                                    sticky = 'nsew', 
                                    padx = 4,
                                    pady = 4,
                                    )
        for i in range(3):
            if i ==1:
                self.SelectDir_frame.grid_columnconfigure(i, weight=5)
            else:
                self.SelectDir_frame.grid_columnconfigure(i, weight=1)
            
        self.SelectDir_frame.grid_rowconfigure(0, weight=1)
       
        
        #Frame for parameter for merge
        self.Properties_frame = customtkinter.CTkFrame(self.TopTab_tabview.tab("Merge Sequence"), 
                                                   corner_radius=4
                                                   )
        self.Properties_frame.grid(row = 1, 
                               column = 0,
                               sticky = 'nsew', 
                               padx = 4,
                               pady = 4,
                               )
   
        
        for i in range(8):
            self.Properties_frame.grid_rowconfigure(i, weight=2)
            if i == 7 :
                self.Properties_frame.grid_rowconfigure(i, weight=6)
        for i in range(3):
            self.Properties_frame.grid_columnconfigure(i, weight=1)

        #Frame for showing merge
        self.Show_frame = customtkinter.CTkFrame(self.TopTab_tabview.tab("Merge Sequence"), 
                                                   corner_radius=4
                                                   )
        self.Show_frame.grid(row = 1, 
                               column = 1,
                               sticky = 'nsew', 
                               padx = 4,
                               pady=4
                               )

        self.Show_frame.grid_columnconfigure(0, weight=1)
        self.Show_frame.grid_columnconfigure(1, weight=1)
        self.Show_frame.grid_columnconfigure(2, weight=1)
        
        self.Show_frame.grid_rowconfigure(0, weight=10)
        self.Show_frame.grid_rowconfigure(1, weight=1)
        self.Show_frame.grid_rowconfigure(2, weight=1)
        
        
        
        #Frame for saving merge
        self.Tool_frame = customtkinter.CTkFrame(self.TopTab_tabview.tab("Merge Sequence"), 
                                                   corner_radius=4
                                                   )
        
        self.Tool_frame.grid(row = 1, 
                               column = 2,
                               sticky = 'nsew',  
                               padx = 4,
                               pady = 4,
                               )
        for i in range(4):
            self.Tool_frame.grid_rowconfigure(i, weight=1)
            
        self.Tool_frame.grid_columnconfigure(0, weight=6)
        self.Tool_frame.grid_columnconfigure(1, weight=1)
        
        self.Tool_frame.grid_rowconfigure(i+1, weight=100)
        self.Tool_frame.grid_columnconfigure(i+1, weight=100)

        

    def dcm_setting_frames(self):
    
        self.dcm_header_frame=customtkinter.CTkFrame(self.TopTab_tabview.tab("Dcm header setting"),
                              corner_radius = 4
                              )
        
        self.dcm_header_frame.grid(row=0,
                                   column=0,
                                   sticky='nswe',
                                   padx=4,
                                   pady=4
                                   
                                   )
        
        self.dcm_header_frame.grid_rowconfigure(0, weight=1)
        self.dcm_header_frame.grid_columnconfigure(0, weight=1)
        
        
        self.dcm_set_frame=customtkinter.CTkFrame(self.TopTab_tabview.tab("Dcm header setting"),
                              corner_radius = 4
                              )
        

        
        self.dcm_set_frame.grid(row=1,
                                   column=0,
                                   sticky='nswe',
                                   padx=4,
                                   pady=4
                                   )
        
        self.dcm_set_frame.grid_rowconfigure(0, weight=1)
        self.dcm_set_frame.grid_columnconfigure(0, weight=1)
        
# =============================================================================
#     def visual_setting_frames(self):
#         self.visual_set_frame=customtkinter.CTkFrame(self.TopTab_tabview.tab("Visual settings"),
#                               corner_radius = 4
#                               )
#         
#         self.visual_set_frame.grid(row=0,
#                                    column=0,
#                                    sticky='nswe',
#                                    padx=4,
#                                    pady=4
#                                   )
#         
#         self.visual_set_frame.grid_rowconfigure(0, weight=1)
#         self.visual_set_frame.grid_columnconfigure(0, weight=1)
#         
#         
#         self.visual_set_frame=customtkinter.CTkFrame(self.TopTab_tabview.tab("Visual settings"),
#                               corner_radius = 4
#                               )
#         
#         self.visual_set_frame.grid(row=1,
#                                    column=0,
#                                    sticky='nswe',
#                                    padx=4,
#                                    pady=4
#                                    )     
#         
#         self.visual_set_frame.grid_rowconfigure(0, weight=1)
#         self.visual_set_frame.grid_columnconfigure(0, weight=1)
# =============================================================================
        
    def labels_merge(self):
        self.label_path=customtkinter.CTkLabel(self.SelectDir_frame,
                                               text='Path to experiment: ',
                                               font=customtkinter.CTkFont(
                                                   size=self.font_size,
                                                   weight="bold"
                                                   
                                                   )
                                               )
        
            
        self.label_path.grid(row=0, column=0,padx=4,pady=4)
        self.label_path.configure(self.desired_font)
        
        properties=['Patch size [X Y Z]','Patch layout','Patch overlap']
        
        for i,text in enumerate(properties):
            
        
            self.label_prop_size = customtkinter.CTkLabel(self.Properties_frame,
                                                   text = text,
                                                   font = customtkinter.CTkFont(
                                                       size=self.font_size,
                                                       weight="bold",
                                                       )
                                                   )
            self.label_prop_size.grid(row = i*2,
                                        column = 0,
                                        columnspan =3,
                                        padx = 2, 
                                        pady = 2, 
                                        sticky = 'nsew')
        
        self.label_bright = customtkinter.CTkLabel(self.Tool_frame,
                                               text = 'Brightness',
                                                font = customtkinter.CTkFont(
                                                    size=self.font_size,
                                                    weight="bold",
                                                    )
                                               )
        self.label_bright.grid(row = 0,
                                column = 0,
                                columnspan = 1,
                                padx = 2, 
                                pady = 2, 
                                sticky = 'nsew')

        self.label_contrast = customtkinter.CTkLabel(self.Tool_frame,
                                               text = 'Contrast',
                                                font = customtkinter.CTkFont(
                                                    size=self.font_size,
                                                    weight="bold",
                                                    )
                                               )
        
        self.label_contrast.grid(row = 2,
                                    column = 0,
                                    columnspan = 1,
                                    padx = 2, 
                                    pady = 2, 
                                    sticky = 'nsew')
        

        self.brigh_label=customtkinter.CTkLabel(self.Tool_frame, 
                                                text =self.get_current_value_b(),
                                                width=50,
                                                font = customtkinter.CTkFont(
                                                    size=self.font_size,
                                                    weight="bold",
                                                    )
                                                
                                               )
        self.brigh_label.grid(row = 1,
                            column = 1, 
                            
                            padx = 4, 
                            pady = 4, 
                            sticky = 'nsew')

        self.contrast_label=customtkinter.CTkLabel(self.Tool_frame, 
                                                text =self.get_current_value_c(),
                                                font = customtkinter.CTkFont(
                                                    size=self.font_size,
                                                    weight="bold",
                                                    )
                                                
                                               )
        self.contrast_label.grid(row = 3,
                            column = 1, 
                            
                            padx = 4, 
                            pady = 4, 
                            sticky = 'nsew')
        
        
        
    def entry_merge(self):
        self.Select_dir_entry=customtkinter.CTkEntry(self.SelectDir_frame, 
                                                     #placeholder_text="Write or select path",
                                                     textvariable = self.path_exp

                                                     )
        
        self.Select_dir_entry.grid(row=0, 
                                   column=1,
                                   padx = 4, 
                                   pady = 4,
                                   sticky = 'nsew')
        
        
        properties=['Patch size ','Patch layout ','Patch overlap']
        coords = ['x','y','z']
        
        
        for i,text_i in enumerate(properties):
              
            if i < 2: 
                
                for j,text_j in enumerate(coords):
             
                    self.prop_entry=customtkinter.CTkEntry(self.Properties_frame, 
                                                           placeholder_text = text_j,
                                                           textvariable = self.dict_param[f'{text_i}{text_j}']
                                                           )
                    self.prop_entry.grid(row = (i*2)+1,
                                        column = j, 
                                        
                                        padx = 4, 
                                        pady = 4, 
                                        sticky = 'nsew')

                    
            else: 
                    self.prop_entry=customtkinter.CTkEntry(self.Properties_frame, 
                                                           placeholder_text = text_i,
                                                           textvariable = self.dict_param[f'{text_i}']
                                                           )
                    self.prop_entry.grid(row = (i*2)+1,
                                        column = 0,
                                        columnspan=3,
                                        padx = 4, 
                                        pady = 4, 
                                        sticky = 'nsew')
            
                    
                    

        
               

        
    def button_merge(self):
        self.SelectDir_button = customtkinter.CTkButton(self.SelectDir_frame,
                                                        text= 'Select dir',
                                                        command = self.select_dir_cmd,

                                                         
                                                        )
        self.SelectDir_button.grid(row = 0,
                                    column = 2, 
                                    padx = 4, 
                                    pady = 4, 
                                    sticky = 'nsew'
                                    )
        
        self.merge_button =  customtkinter.CTkButton(self.Properties_frame,
                                                           text = 'Run',
                                                           command=self.run_merge,

                                                           )
        self.merge_button.grid(row = 8,
                                     column = 0,
                                     columnspan=3,
                                     padx = 4, 
                                     pady = 4, 
                                     sticky = 'nsew')
        
        self.Close_button = customtkinter.CTkButton(self.Show_frame,
                                                           text = 'Close view',
                                                           command=self.close_view_cmd,

                                                           )
        self.Close_button.grid(row=2,
                              column= 0,
                              pady=4,
                              padx=4,
                              sticky='nsew'
                              )
        
        self.Save_button =  customtkinter.CTkButton(self.Show_frame,
                                                           text = 'Save as .dcm',
                                                           command=self.save_dcm_cmd,

                                                           )
        self.Save_button.grid(row=2,
                              column= 1,
                              pady=4,
                              padx=4,
                              sticky='nsew'
                              )
        

    
    def options_merge(self):
        
        self.merge_optins = customtkinter.CTkSegmentedButton(master=self.Properties_frame,
                                       values=['Mean','Gauss','Gauss sup','Supress'],
                                       command=self.chosen_options,
                                       
                                       )
        self.merge_optins.grid(row = 7,
                                column = 0,
                                columnspan=3,
                                padx = 4, 
                                pady = 4, 
                                sticky = 'nsew')
        self.merge_optins.set('Mean')
        self.chosen_options(self.merge_optins.get())
    def slider_tool_merge(self):
        self.slider_brigth = customtkinter.CTkSlider(self.Tool_frame,
                                                     from_ =  0 ,
                                                     to = 65553,
                                                     
                                                     command=self.change_cb
                                                     )
        self.slider_brigth.grid(row= 1,
                                column=0,
                                padx = 4, 
                                pady = 4, 
                                sticky = 'ew')
        
        self.slider_contrast = customtkinter.CTkSlider(self.Tool_frame,
                                                     from_ = 0 ,
                                                     to = 3,
                                                     
                                                     command=self.change_cb
                                                     )
        self.slider_contrast.grid(row= 3,
                                column=0,
                                padx = 4, 
                                pady = 4, 
                                sticky = 'ew')
        
        self.slider_contrast.set(1)
        self.slider_brigth.set(0)
        self.slider_contrast.bind('<Enter>',self.enter)
        self.slider_brigth.bind('<Enter>',self.enter)
        
    def slider_merge(self):
        self.slider_show  = customtkinter.CTkSlider(self.Show_frame, 
                                                    from_=0, 
                                                    to=self.to_slider, 
                                                    command=self.update_show,
                                                    variable=self.current_show,
                                                    number_of_steps = self.to_slider
                                                    )
        self.slider_show.grid(row = 1,
                            column = 0,
                            columnspan = 2,
                            padx = 4, 
                            pady = 4, 
                            sticky = 'nsew')
        
        self.slider_show.bind('<Enter>',self.enter)
        self.slider_show.bind('<ButtonRelease>', self.update_cache)
        
    
        

    
    
    def dcm_header_label(self):
        

        self.Dcm_label_save=customtkinter.CTkLabel(self.dcm_header_frame, 
                                               text='Path to sace .dcm'
                                               )
        self.Dcm_label_save.grid(row = 0,
                            column = 0,
                            columnspan=2,
                            padx = 4, 
                            pady = 4, 
                            sticky = 'nsew')
        
        for idefix,item in enumerate(self.dcm_header_json):
            
            self.Dcm_label=customtkinter.CTkLabel(self.dcm_header_frame, 
                                                   text=item
                                                   )
            self.Dcm_label.grid(row =2+idefix*2,
                                column = 0,
                                columnspan=2,
                                padx = 4, 
                                pady = 4, 
                                sticky = 'nsew')
            
                

            
    def dcm_header_entry(self):
        
        self.Dcm_entry_save=customtkinter.CTkEntry(self.dcm_header_frame, 
                                               textvariable=self.path_dcm_save
                                               )
        self.Dcm_entry_save.grid(row = 1,
                            column = 0, 
                            padx = 4, 
                            pady = 4, 
                            sticky = 'nsew')
        
        for idefix,item in enumerate(self.dcm_header_json):
            
            self.Dcm_entry=customtkinter.CTkEntry(self.dcm_header_frame, 
                                                   textvariable = self.dcm_header_json[item]
                                                   )
            
            self.Dcm_entry.grid(row =(idefix*2)+3,
                                column = 0, 
                                columnspan= 2,
                                padx = 4, 
                                pady = 4, 
                                sticky = 'nsew')
       
            
    
    def dcm_header_button(self):
        
        self.dcm_save_button = customtkinter.CTkButton(self.dcm_header_frame, 
                                                      text = 'Select save dir',
                                                       command=self.get_save_path
                                                       )
        self.dcm_save_button.grid(row = 1,
                            column = 1, 
                            padx = 4, 
                            pady = 4, 
                            sticky = 'nsew')
        
        
        self.dcm_set_button =  customtkinter.CTkButton(self.dcm_set_frame,
                                                           text = 'Set .dcm',
                                                           command=self.update_dcm_header,

                                                           )
        self.dcm_set_button.grid(row=0,
                              column= 0,
                              pady=4,
                              padx=4,
                              sticky='nsew'
                              )
        
        self.dcm_set_default_button =  customtkinter.CTkButton(self.dcm_set_frame,
                                                           text = 'Set setting as default',
                                                           command=self.set_as_default

                                                           )
        self.dcm_set_default_button.grid(row=0,
                              column= 1,
                              pady=4,
                              padx=4,
                              sticky='nsew'
                              )
        
        self.dcm_reset_default_button =  customtkinter.CTkButton(self.dcm_set_frame,
                                                           text = 'Reset to default',
                                                           command=self.reset_default

                                                           )
        self.dcm_reset_default_button.grid(row=0,
                              column= 2,
                              pady=4,
                              padx=4,
                              sticky='nsew'
                              )
    def update_dcm_header(self):
        
        
        for idefix,item in enumerate(self.dcm_header_json):
            
            self.dcm_header_json[item].set(self.dcm_header_json[item].get())
            print(self.dcm_header_json[item].get())
            
    def update_cache(self,event):
        idefix,self.curent_name=self.visible_tab()
        
        self.position_cache[self.curent_name]=self.slider_show.get()

        
    def enter(self,event):
        
        try:
            
            idefix,self.curent_name=self.visible_tab()
            
            if self.on_name != self.curent_name:
                self.slider_show.set(self.position_cache[self.curent_name])
                self.on_name = self.curent_name
                self.to_show = self.img[idefix]
                img_shape=self.img[idefix].shape
                self.to_slider = img_shape[0]-1
                #self.change_cb(0)
                self.slider_merge()
                self.show_seq(self.curent_name,idefix)
                self.update_show(int(self.position_cache[self.curent_name]))
   
            else:
                
                pass
            
        except ValueError:
            pass
        except AttributeError:
            pass
        except TypeError:
            pass

    def get_current_value_c(self):
        return '{: .2f}'.format(self.contrast_value.get())
            
    def get_current_value_b(self):
        return '{: .0f}'.format(self.bright_value.get())     
    
    def slider_changed(self):
        self.contrast_label.configure(text=self.get_current_value_c())
        self.brigh_label.configure(text=self.get_current_value_b())
    
    def label_tool_init(self):
        self.bright_value.set(self.slider_brigth.get())
        self.contrast_value.set(self.slider_contrast.get())
        self.slider_changed()
    
    def change_cb(self,value):
        try:
            idefix,curent_name=self.visible_tab()
    
            
            
                 
            self.bright_value.set(self.slider_brigth.get())
            self.contrast_value.set(self.slider_contrast.get())
            self.slider_changed()
            self.contrast_cache[curent_name]=(self.slider_contrast.get())
            self.brightness_cache[curent_name]=(self.slider_brigth.get())
            self.to_show=self.contrast_brightness(self.img[idefix],
                                                  float(self.contrast_value.get()),
                                                  float(self.bright_value.get()))
            
            self.update_show(int(self.position_cache[self.curent_name]))
            
        except TypeError:
            pass
       
    
    def update_show(self,value):
        idefix = int(value)
        
        self.sub.imshow(self.to_show[idefix],
                        cmap='gray',
                        vmax= 65535,
                        vmin = 0)
        self.canvas.draw()
    
    def chosen_options(self,value):
        self.merge_method = value    
    
    def curent_parameters(self):
        try:
            idefix,_=self.visible_tab()
            img_shape=self.img[idefix].shape
            
            self.dcm_header = {
                'Rows':img_shape[1],
                'Columns':img_shape[2],
                'NumberOfFrames':img_shape[0],
                'PixelRepresentation':0,
                'PixelData':self.img[idefix].tobytes() ,
              
                }
        except ValueError:
            pass
        
    def get_save_path_dcm(self):
        self.pop_up_save_name()
        path = os.path.join(self.path_dcm_save.get(),
                     self.save_name_pop.get_input())
        path_temp = path
        path=f'{path}.dcm'
        count=0
        
        while  os.path.isfile(path):
            path=path_temp
            count+=1
            path=f'{path}_{count}.dcm'
        
        return(path)
        
    def save_dcm_cmd(self):
        
        self.curent_parameters()
        path = self.get_save_path_dcm()
        try:
            d=dcmread("./MRIm180.dcm")
            
            d.Rows=self.dcm_header['Rows']
            d.Columns=self.dcm_header['Columns']
            d.NumberOfFrames=self.dcm_header['NumberOfFrames']
            d.PixelRepresentation=self.dcm_header['PixelRepresentation']
            
            d.PixelData= self.dcm_header['PixelData']
                   
            d.InstitutionName=self.dcm_header_json['InstitutionName'].get()
            d.ReferringPhysicianName=self.dcm_header_json['ReferringPhysicianName'].get()
            d.TimezoneOffsetFromUTC= self.dcm_header_json['TimezoneOffsetFromUTC'].get()
            d.PatientBirthDate=self.dcm_header_json['PatientBirthDate'].get()
            d.ResponsibleOrganization= self.dcm_header_json['ResponsibleOrganization'].get()
            d.SliceThickness=self.dcm_header_json['SliceThickness'].get()
            d.DeviceSerialNumber=self.dcm_header_json['DeviceSerialNumber'].get()
            d.SoftwareVersions= self.dcm_header_json['SoftwareVersions'].get()
            
            d.save_as(path) 
            
            tk.messagebox.showinfo(title='Saved', 
                                   message=f'File was saved at {path}') 
        except FileNotFoundError:
            
            tk.messagebox.showerror(title='Something is wrong', 
                                    message='Make sure you have file MRIm180.dcm in same directory.')

    def visible_tab(self):
        try:
            name_visible= self.Show_tab.get()
            idefix = int(name_visible.split('_')[-1])
            return(idefix,name_visible)
        except ValueError:
            pass
        
    def close_view_cmd(self):
        idefix,name_visible=self.visible_tab()
        self.img[idefix] = []
        self.rec.remove(name_visible)
        self.Show_tab.delete(name_visible)
        
    def get_save_path(self):
        self.path_dcm_save.set(tk.filedialog.askdirectory())
        
    def get_params(self,multiple=False,*argv):
        try:
            self.path_exp.set( os.path.join(self.path_exp.get(),*argv[0]))
            self.params=GetParam(self.path_exp.get(),multiple)
        except IndexError:
            
            self.params=GetParam(self.path_exp.get(),multiple)
        
        self.try_set()
        
   

    def select_dir_cmd(self):
# =============================================================================
#         try:
# =============================================================================
        self.path_exp.set(tk.filedialog.askdirectory())
        
        
        if self.check_subdir():
            self.multiple = True
            self.popup = CTkComboboxDialog(
                value =self.subdirs,
                command =lambda txt: self.get_params(self.multiple,txt))
            


        else:
            self.multiple=False
            self.get_params()

# =============================================================================
#         except OSError:
#             tk.messagebox.showerror(title='No path.', 
#                                     message='The path to experiment was not defined ')
# =============================================================================
    
    
    def set_as_default(self):
        self.dcm.set_new_default(self.dcm_header_json)
        #self.update_dcm_header()
        
    
    def reset_default(self):
        self.dcm_header_json = self.dcm.reset_default()
        self.dcm_header_entry()
       # self.update_dcm_header()
            
    def pop_up_save_name(self):
        self.save_name_pop = customtkinter.CTkInputDialog(text='Type save name:',
                                                          title='Save .dcm')

        
    def try_set(self):
        
        for idx,item in enumerate(self.dict_param):
            try :
                self.dict_param[item].set(self.params.all_param[idx])
            except TypeError:
                self.dict_param[item].set('None')
                
    def transform_dict(self):
        self.merge_param=[]
        try:
            for idx,item in enumerate(self.dict_param):
                if '.' in self.dict_param[item].get():
                    self.merge_param.append(float(self.dict_param[item].get()))
                else: 
                    self.merge_param.append( int(self.dict_param[item].get()))
        except ValueError:
            print('Wrong input')
                
    def run_merge(self):
        try:
            self.transform_dict()
            self.Merge = Merge(self.path_exp,
                               self.merge_param,
                               self.merge_method,
                               self.multiple)
            
            self.img.append(self.Merge.get_compose_img())
            
            
            self.rec.append(f'RUN_{self.count}')
            self.count+=1
            self.tab_show()
            self.enter('')
            
            
            
        except IndexError:
            tk.messagebox.showwarning(title='Warning',
                                      message='Something is wrong. Try reload parameters or set up right righ parameters.')
            
        except AttributeError:
           
            tk.messagebox.showwarning(title='Warning',
                                      message='Please select a experiment before Run')
        
        except ValueError:
            tk.messagebox.showwarning(title='Warning',
                                      message='Submitted values could not be processed.')

          
    def show_seq(self,tab_name,img_number):
        self.to_show = self.img[img_number]
        
        
        self.figure = Figure()
        self.sub = self.figure.add_subplot(111)
        self.sub.imshow(self.to_show[int(self.position_cache[tab_name])],
                        cmap='gray',
                        vmax= 65535,
                        vmin = 0)
        
        current=self.current_show.get()
        
        
        self.canvas = FigureCanvasTkAgg(self.figure, 
                                        master=self.Show_tab.tab(tab_name)
                                        )
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row = 0,
                                    column = 0,
                                    sticky='nswe')
        
        self.canvas.get_tk_widget().grid_columnconfigure(0, weight=1)
        self.canvas.get_tk_widget().grid_rowconfigure(0, weight=1)
        
        self.canvas._tkcanvas.grid(row = 0,
                                    column = 0,
                                    sticky='nswe')
        
        self.canvas._tkcanvas.grid_columnconfigure(0, weight=1)
        self.canvas._tkcanvas.grid_rowconfigure(0, weight=1)
        
   
        
       
    def check_subdir (self):
        
        try:
            walk = list(os.walk(self.path_exp.get()))
            
            if len(walk[2][1])>1:
                # popup=self.ToplevelWindow(walk[2][1])
                self.subdirs = walk[2][1]
                return True
                    
            else:
                return False
        except IndexError:
            pass
        
    def run(self):
    
        self.main_window.mainloop()



if __name__ == '__main__':
    MPIMergeApp = main()
    MPIMergeApp.run()
   