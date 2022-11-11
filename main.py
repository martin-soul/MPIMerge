
import tkinter as tk
from tkinter import filedialog
from MPICore import RawData,CalParamCalSeq,MPIMerge,GetPath,LoadProperties
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
# =============================================================================
# import customtkinter
# =============================================================================
import os
import re
from pydicom import dcmread
#https://github.com/TomSchimansky/CustomTkinter


"""
Define styles font,color etc


"""

# =============================================================================
# customtkinter.set_appearance_mode("Dark")
# customtkinter.set_default_color_theme("dark-blue")
# =============================================================================

#ošetřit vstupy (-orvní zmačknutí compos, error při nevybrání cesty)
#kam ukladat dicom
#layout GUI
#







class Main():
    def __init__ (self):
        
        self.main_window = tk.Tk()
        self.main_window.geometry('350x150')
        self.main_window.resizable(0,0)
        self.main_window.title('Merge MPI sequence tool')
        
        self.main_window.iconbitmap("merge.ico")
        
        self.main_window.grid_rowconfigure(0, weight=0)
        self.main_window.grid_columnconfigure(0, weight=1)

          
        self.path_dir=tk.StringVar()
        self.size_XYZ = tk.StringVar()
        self.patch_overlap = tk.StringVar()
        self.patch_layout = tk.StringVar()
        
        
        
        self.save_dcm = tk.StringVar()
        self.save_dcm.set('i_am_saved_file.dcm')
        self.InstitutionName = tk.StringVar(value='Center for Advanced Preclinical Imaging') 
        self.ReferringPhysicianName=tk.StringVar(value='') 
        self.TimezoneOffsetFromUTC=tk.StringVar(value='+0100')
        self.PatientBirthDate = tk.StringVar(value='')
        self.ResponsibleOrganization = tk.StringVar(value='First Faculty of Medicine, Charles University, Praha')
        self.SliceThickness = tk.StringVar(value='1')
        self.DeviceSerialNumber = tk.StringVar(value='')
        self.SoftwareVersions = tk.StringVar(value='CAPI MPI collider 1.0')
        
        
        
        self.path_dir_dcm =tk.StringVar(self.path_dir.get())
        
        self.path_save =  self.path_dir.get()
        self.fname_save = 'i_am_save_file'
        
        self.frame_main = self.create_frames_main()
        
        self.labels_main = self.create_labels_main()
        
        self.entry_main = self.create_entry_main()
        
        self.buttons_main = self.create_buttons_main()
        
        
        
    def create_frames_main(self):
        
        self.frame_path = tk.Frame(self.main_window)
        self.frame_path.grid(row=0,stick='ew',padx=2,pady=2)
              
        self.frame_center = tk.Frame(self.main_window)
        self.frame_center.grid(stick = 'ew',padx=2,pady=2)
        
        self.frame_center.grid_rowconfigure(0, weight=0)
        self.frame_center.grid_columnconfigure(1, weight=1)
    
        
        self.frame_prop =tk.Frame(self.frame_center,)
        self.frame_prop.grid(row=0, column=0,stick='sn',padx=2,pady=2)
        
        self.frame_compute =tk.Frame(self.frame_center)
        self.frame_compute.grid(row=0,column=1,sticky = 'sn',padx=2,pady=2)
        
    def create_labels_main(self):
        self.label_path_info = tk.Label(self.frame_path,
                                   text = 'Apply path to experiment: '
                                   )
        
        self.label_path_info.grid(row=0,column=0,padx=2,pady=2)
        
        self.label_patch_size =tk.Label(self.frame_prop,
                                           text='Patch size XYZ')
        self.label_patch_size.grid(row=0, column=0,padx=2,pady=2)
        
        self.label_patch_layout =tk.Label(self.frame_prop,
                                           text='Patch layout')
        self.label_patch_layout.grid(row=1, column=0,padx=2,pady=2)
        
        self.label_patch_overlap =tk.Label(self.frame_prop,
                                           text='Patch overlap')
        self.label_patch_overlap.grid(row=2, column=0,padx=2,pady=2)
        
    def create_entry_main(self):
        self.entry_path = tk.Entry(self.frame_path, 
                                   textvariable = self.path_dir,
                                   width=45
                                   )
        
        self.entry_path.grid(row=1, column=0)
        
        self.entry_sizeXYZ = tk.Entry(self.frame_prop,
                                      textvariable= self.size_XYZ
                                      )
        self.entry_sizeXYZ.grid(row=0, column=1,padx=2,pady=2)
        
        
        self.entry_patch_layout= tk.Entry(self.frame_prop,
                                            textvariable=self.patch_layout
                                            )
        self.entry_patch_layout.grid(row=1, column=1,padx=2,pady=2)
        
        
        self.entry_patch_overlap = tk.Entry(self.frame_prop, 
                                            textvariable=self.patch_overlap
                                            )
        self.entry_patch_overlap.grid(row=2, column=1,padx=2,pady=2)
                                                                                        
    
    def create_buttons_main(self):
        self.button_path_dir = tk.Button(self.frame_path,
                                         text = 'Apply dir',
                                         command = lambda:self.try_set_var()
                                             
                                         )
        self.button_path_dir.grid(row=1,column=1)
        
        self.button_compute = tk.Button (self.frame_compute, 
                                         text = 'Compute sequence',
                                         command =lambda: self.compute_seq(),
                                         width = 15,
                                         height= 3
                                
                                         )
        self.button_compute.grid(row=1, column=2,padx=2,pady=4)
        

    def set_var(self,var_to_set):
        self.path_dir_dcm.set(var_to_set[0])
        self.path_dir.set(var_to_set[0])
        self.size_XYZ.set(var_to_set[1])
        self.patch_layout.set(var_to_set[2])
        self.patch_overlap.set(var_to_set[3])
        
    def try_set_var(self):
        try:
            var_to_set =self.get_path()
            self.set_var(var_to_set)
        
        except TypeError:
            self.path_dir.set('None')
            self.size_XYZ.set('None')
            self.patch_layout.set('None')
            self.patch_overlap.set('None') 
            
    
    def get_path(self):
        self.chosen_path = filedialog.askdirectory()
        confirmation = self.check_files()
        
        if confirmation:
            self.load_props()
            
            return(self.return_props())
        
        else:
            self.pop_up()
            
            
            
    def return_props(self):
        
        try:

            
            return(self.chosen_path,
            self.reco_prop,
            self.method_prop[1],
            round(self.method_prop[0]*0.01,2))
            
        except AttributeError:
            
            tk.messagebox.showerror(title='Something is wrong', 
                                    message='One of file is not existing or not contain default settings')
            
  
        
            
    def compute_seq(self):

                
        
        if not self.path_dir.get().strip():  
            self.path_dir.set(self.path_dir) 

        if not self.size_XYZ.get().strip() :  
            self.size_XYZ.set(self.size_XYZ)
        
        
        if not self.patch_layout.get().strip() :  
            self.patch_layout.set(self.patch_layout)
            
            
        if not self.patch_overlap.get().strip():  
            self.patch_overlap.set(self.patch_overlap)
        
        try:
            size_XYZ = self.str2int(self.size_XYZ.get())
            patch_layout = self.str2int(self.patch_layout.get())
            patch_overlap = self.str2int(self.patch_overlap.get())

            try:
                self.converted=RawData(self.path_raw).get_converted()   
                
            except TypeError:
                self.converted=RawData(self.path_raw.get()).get_converted()   
    
            self.par = CalParamCalSeq(self.converted,
                                      patch_layout,
                                      patch_overlap,
                                      size_XYZ)
            
            self.merge=MPIMerge(self.par.get_seq(),
                        self.par.get_mat(),
                        self.par.get_mat(),
                        self.par.get_add_mat(),
                        self.par.get_space_coord(),
                        size_XYZ,
                        patch_overlap
                        )
            self.show_seq()
        except:
            tk.messagebox.showwarning(title='Warning',
                                      message='Insert right parameters')
        
    def show_seq (self):
        
        self.img=self.merge.get_compose_img()
        
        self.display_seq = tk.Toplevel(self.main_window)
        self.display_seq.iconbitmap("merge.ico")
        
        
        
        self.frame_canvas = tk.Frame(self.display_seq)
        self.frame_canvas.grid(column=0, row = 0, sticky = 'ewns')
        
        self.figure = Figure()
        self.sub = self.figure.add_subplot(111)
        self.sub.imshow(self.img[0,:,:],cmap='gray',vmin=0, vmax=self.img[0,:,:].max())
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_canvas )
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
        self.canvas._tkcanvas.pack(side="top", fill="both", expand=1)
        
        
        self.frame_scale = tk.Frame(self.display_seq)
        self.frame_scale.grid(column=0, row = 1, sticky = 'ew')
        
        self.slider = tk.Scale(self.frame_scale,
                               from_=0,
                               to=self.img.shape[0]-1,
                               orient=tk.HORIZONTAL,
                               command=lambda x:self.update()
                               )
        self.slider.pack(fill='both',padx=20)
        
        self.frame_buttons = tk.Frame(self.display_seq)
       
        self.frame_buttons.grid(column=0,row=2)
        
        self.frame_buttons.grid_columnconfigure(0, weight=1)
        self.frame_buttons.grid_columnconfigure(1, weight=1)
        self.button_save = tk.Button(self.frame_buttons,
                                     text='Save as DCM',
                                     command= lambda:self.file2dcm(),
                                     height= 2,
                                     
                                     )
                                    
        self.button_save.grid(column=1,padx=5,pady=3,sticky='ew')
        
        
        self.button_modify_header = tk.Button(self.frame_buttons,
                                     text='Modify DCM header',
                                     command= lambda:self.header_dcm(),
                                     height= 2,
                                     
                                     )
        
        self.button_modify_header.grid(row=0,column=0,padx=5,pady=3,sticky='nsew')
    
    def update(self):
        self.positon = self.slider.get()
       
        self.sub.imshow(self.img[self.positon,:,:],cmap='gray',vmin=0, vmax=self.max_from_img())
        self.canvas.draw()
        
        
    def max_from_img(self):
        return(self.img[self.positon,:,:].max())
        
        
    def str2int(self,var):
        
        out=None
        if '.' in var:
            out=''
        
            for i in var:
                if re.match('\d|[.]', i):
                    out=out+i
            out=float(out)
            
        elif ',' in var:
            var=re.sub('[)(]','',var)
            var=var.split(',')
            out=[]
            for i in var:
                out.append(int(i))
        else:
            
            var=var.split(' ')
            out=[]
            for i in var:
                out.append(int(i))
                
        return out
        
        
    def check_files(self):
        self.get_method=GetPath(self.chosen_path, 'method')
        self.get_reco =GetPath(self.chosen_path, 'reco') 
        self.get_raw = GetPath(self.chosen_path,'2dseq')
        
        self.path_method =  self.get_method()
        self.path_reco =  self.get_reco()
        self.path_raw = self.get_raw()

       
        
       
        
        if not (self.path_method or self.path_reco or self.path_raw):
            
            
            return (False)
        
        else:
            
            return (True)
        
        
    
    def load_props (self):
        
        try: 
            self.reco_prop=LoadProperties(self.path_reco, 
                                          self.path_save,
                                          self.fname_save
                                          ).rec_param()
            
    
            self.method_obj=LoadProperties(self.path_method,
                                            self.path_save, 
                                            self.fname_save)
            
        except TypeError:
            self.reco_prop=LoadProperties(self.path_reco.get(), 
                                          self.path_save,
                                          self.fname_save
                                          ).rec_param()
            
    
            self.method_obj=LoadProperties(self.path_method.get(),
                                            self.path_save, 
                                            self.fname_save)
            
            
            
        self.method_prop=self.method_obj.rec_param()
        self.time_stamp = self.method_obj.get_timestamp()
            
            
    def pop_up (self):
        
        
        self.path_raw = tk.StringVar()
        self.path_method =tk.StringVar()
        self.path_reco = tk.StringVar()
        
        self.pop_false=tk.Toplevel(self.main_window)
        self.pop_false.iconbitmap("merge.ico")
        self.pop_false.geometry('400x150')
        
        self.entry_raw = tk.Entry(self.pop_false, textvariable=self.path_raw,width=45)
        self.entry_raw.grid(row=0,column=0,padx=2,pady=2)
        
        self.apply_raw = tk.Button(self.pop_false, text= 'Apply raw',
                                   width=15,
                                   command = lambda: [self.path_raw.set(
                                       tk.filedialog.askopenfile().name),self.path_dir.set(self.path_raw.get().replace(os.path.basename(self.path_raw.get()), ''))])
        self.apply_raw.grid(row=0,column=1,padx=2,pady=4)
        
        self.entry_reco = tk.Entry(self.pop_false, textvariable=self.path_reco,width=45)
        self.entry_reco.grid(row=1,column=0,padx=2,pady=2)
        
        self.apply_reco = tk.Button(self.pop_false, 
                                    text= 'Apply reco',
                                    width=15,
                                    command = lambda: self.path_reco.set(
                                       tk.filedialog.askopenfile().name))
        self.apply_reco.grid(row=1,column=1,padx=2,pady=2)
        
        self.entry_method = tk.Entry(self.pop_false, textvariable=self.path_method,width=45)
        self.entry_method.grid(row=2,column=0,padx=2,pady=2)
        
        self.apply_method = tk.Button(self.pop_false, 
                                      text= 'Apply method',
                                      width=15,
                                      command = lambda: self.path_method.set(
                                         tk.filedialog.askopenfile().name)
                                      )
        self.apply_method.grid(row=2,column=1,padx=2,pady=2)
    
        self.close_pop_up = tk.Button(self.pop_false, 
                                      text= 'Confirm path',
                                      command = lambda:[
                                          self.pop_false.destroy(),
                                          self.load_props(),
                                          self.set_var(self.return_props()),
                                          self.path_dir.set(self.path_raw.get().replace(os.path.basename(self.path_raw.get()), ''))
                                          ]
                                      )
       
        
        self.close_pop_up.grid(row=3,column=1,padx=2,pady=2)
        
    def header_dcm(self):
        
        self.pop_header = tk.Toplevel(self.main_window)
        self.pop_header.iconbitmap("merge.ico")
        self.pop_header.geometry('410x310')
        self.frame_header_lab_ent = tk.Frame(self.pop_header)
        self.frame_header_lab_ent.grid(column=0,row=0,padx=4,pady=4,sticky='we')
        
        self.header_dcm_labels()
        self.header_dcm_entry()
        

        
        self.frame_set_header_button=tk.Frame( self.pop_header)
        self.frame_set_header_button.grid(column=0,row=10,padx=4,pady=4,sticky='we')
        
        self.frame_set_header_button.grid_columnconfigure(0, weight=1)
        
        self.button_set_dcm=tk.Button(self.frame_set_header_button, 
                                      text='Set DCM header',
                                      command= lambda: self.set_dcm(),
                                      
                                      height=2
                                      )
        
        self.button_set_dcm.grid(sticky='ew')
            
    def header_dcm_entry(self):
        self.entry_save_dcm = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.save_dcm,
                                            width=40
                                            )
        self.entry_save_dcm.grid(column=1,row=0,padx=2,pady=2)
        
        
        self.entry_path_save_dcm = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.path_dir_dcm,
                                            width=40
                                            )
        self.entry_path_save_dcm.grid(column=1,row=1,padx=2,pady=2)
        
        self.entry_InstitutionName = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.InstitutionName,
                                            width=40
                                            )
        self.entry_InstitutionName.grid(column=1,row=2,padx=2,pady=2)
        
        self.entry_ReferringPhysicianName = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.ReferringPhysicianName,
                                            width=40
                                            )
        self.entry_ReferringPhysicianName.grid(column=1,row=3,padx=2,pady=2)
        
        self.entry_TimezoneOffsetFromUTC = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.TimezoneOffsetFromUTC,
                                            width=40
                                            )
        self.entry_TimezoneOffsetFromUTC.grid(column=1,row=4,padx=2,pady=2)
        
        self.entry_PatientBirthDate = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.PatientBirthDate,
                                            width=40
                                            )
        self.entry_PatientBirthDate.grid(column=1,row=5,padx=2,pady=2)
        
        self.entry_ResponsibleOrganization = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.ResponsibleOrganization,
                                            width=40
                                            )
        self.entry_ResponsibleOrganization.grid(column=1,row=6,padx=2,pady=2)
        
        self.entry_SliceThickness = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.SliceThickness,
                                            width=40
                                            )
        self.entry_SliceThickness.grid(column=1,row=7,padx=2,pady=2)
        
        self.entry_DeviceSerialNumber = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.DeviceSerialNumber,
                                            width=40
                                            )
        self.entry_DeviceSerialNumber.grid(column=1,row=8,padx=2,pady=2)
        
        self.entry_SoftwareVersions = tk.Entry(self.frame_header_lab_ent, 
                                            textvariable=self.SoftwareVersions,
                                            width=40
                                            )
        self.entry_SoftwareVersions.grid(column=1,row=9,padx=2,pady=2)
    
    def header_dcm_labels(self):
        
        self.label_save_dcm = tk.Label(self.frame_header_lab_ent,

                                       text='DCM file name: '
                                       )
        self.label_save_dcm.grid(row=0,column=0,padx=2,pady=2)
        
        
        self.label_path_save_dcm = tk.Label(self.frame_header_lab_ent,
                                            text='path for DCM file: '
                                            )
        self.label_path_save_dcm.grid(row=1,column=0,padx=2,pady=2)
        
        self.label_InstitutionName = tk.Label(self.frame_header_lab_ent, 
                                            text='Institution name: '
                                            )
        self.label_InstitutionName.grid(row=2,column=0,padx=2,pady=2)
        
        self.label_ReferringPhysicianName = tk.Label(self.frame_header_lab_ent, 
                                            text='Referring physician name: '
                                            )
        self.label_ReferringPhysicianName.grid(row=3,column=0,padx=2,pady=2)
        
        self.label_TimezoneOffsetFromUTC = tk.Label(self.frame_header_lab_ent, 
                                            text='Timezone offset from UTC: '
                                            )
        self.label_TimezoneOffsetFromUTC.grid(row=4,column=0,padx=2,pady=2)
        
        self.label_PatientBirthDate = tk.Label(self.frame_header_lab_ent, 
                                           text='Patient birth date: '
                                            )
        self.label_PatientBirthDate.grid(row=5,column=0,padx=2,pady=2)
        
        self.label_ResponsibleOrganization = tk.Label(self.frame_header_lab_ent, 
                                            text='Responsible organization: '
                                            )
        self.label_ResponsibleOrganization.grid(row=6,column=0,padx=2,pady=2)
        
        self.label_SliceThickness = tk.Label(self.frame_header_lab_ent, 
                                            text='Slice thickness: '
                                            )
        self.label_SliceThickness.grid(row=7,column=0,padx=2,pady=2)
        
        self.label_DeviceSerialNumber = tk.Label(self.frame_header_lab_ent, 
                                            text='Device serial number: '
                                            )
        self.label_DeviceSerialNumber.grid(row=8,column=0,padx=2,pady=2)
        
        self.label_SoftwareVersions = tk.Label(self.frame_header_lab_ent, 
                                            text='Software versions: '
                                            )
        self.label_SoftwareVersions.grid(row=9,column=0,padx=2,pady=2)
        
           
    def set_dcm(self):
        
        self.save_dcm.set(self.save_dcm.get())
        self.path_dir_dcm.set(self.path_dir_dcm.get())
        self.InstitutionName.set(self.InstitutionName.get())
        self.ReferringPhysicianName.set(self.ReferringPhysicianName.get())
        self.TimezoneOffsetFromUTC.set(self.TimezoneOffsetFromUTC.get())
        self.PatientBirthDate.set(self.PatientBirthDate.get())
        self.ResponsibleOrganization.set(self.ResponsibleOrganization.get())
        self.SliceThickness.set(self.SliceThickness.get())
        self.DeviceSerialNumber.set(self.DeviceSerialNumber.get())
        self.SoftwareVersions.set(self.SoftwareVersions.get())
        
        tk.messagebox.showinfo(title='Set header', 
                               message='Parameters was set')
        self.pop_header.destroy()
        
    def file2dcm(self):
        
        try:
            d=dcmread("./MRIm180.dcm")
            
           
            
            d.Rows=self.par.get_mat().shape[2]
            d.Columns=self.par.get_mat().shape[1]
            d.NumberOfFrames=self.par.get_mat().shape[0]
            d.PixelData=self.merge.get_compose_img().tobytes()
            d.InstanceCreationDate=f'{self.time_stamp[2]}.{self.time_stamp[1]}.{self.time_stamp[0]}'
            d.StudyDate=f'{self.time_stamp[2]}.{self.time_stamp[1]}.{self.time_stamp[0]}'
            d.SeriesDate=f'{self.time_stamp[2]}.{self.time_stamp[1]}.{self.time_stamp[0]}'
            d.AcquisitionDate=f'{self.time_stamp[2]}.{self.time_stamp[1]}.{self.time_stamp[0]}'
            d.InstanceCreationTime=f'{self.time_stamp[3]}:{self.time_stamp[4]}:{self.time_stamp[5]}'
            d.StudyTime=f'{self.time_stamp[3]}:{self.time_stamp[4]}:{self.time_stamp[5]}'
            d.SeriesTime=f'{self.time_stamp[3]}:{self.time_stamp[4]}:{self.time_stamp[5]}'
            d.AcquisitionTime=f'{self.time_stamp[3]}:{self.time_stamp[4]}:{self.time_stamp[5]}' #WarnMassege
            d.InstitutionName=self.InstitutionName.get()
            d.ReferringPhysicianName=self.ReferringPhysicianName.get()
            d.TimezoneOffsetFromUTC= self.TimezoneOffsetFromUTC.get()
            d.PatientBirthDate=self.PatientBirthDate.get()
            d.ResponsibleOrganization= self.ResponsibleOrganization.get()
            d.SliceThickness= self.SliceThickness.get()
            d.DeviceSerialNumber= self.DeviceSerialNumber.get()
            d.SoftwareVersions= self.SoftwareVersions.get()
            d.save_as(os.path.join(self.path_dir_dcm.get(),self.save_dcm.get()))
            
            tk.messagebox.showinfo(title='Saved', 
                                   message=f'File was saved at {self.path_dir_dcm.get()}/{self.save_dcm.get()}')
        except FileNotFoundError:
            tk.messagebox.showerror(title='Something is wrong', 
                                    message='Make sure you have file MRIm180.dcm in same directory.')
             
            
        
    def run(self):
        self.main_window.mainloop()
        

if __name__ == '__main__':
    MPIMergeApp = Main()
    MPIMergeApp.run()