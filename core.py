import os
import json
import statistics
import time
import regex as re
import struct as st
import numpy as np
import math as m 
import tkinter.filedialog
import tkinter as tk
from itertools import product
import customtkinter



    

class Path():
    
       
    
    def find_file(self):
        
   
        for root, dirs, files in os.walk(self.path_exp):  
            if self.filename in files:
               return(os.path.normpath( f'{root}/{self.filename}'))
           
  
    def find_subdir (self):
        for root, dirs, files in os.walk(self.path_exp):  
            if self.subdir in dirs:
               return(os.path.normpath( f'{root}/{self.subdir}'))
        
    def get_subdir(self):
        
        path_file=self.find_subdir()
        try:
            if os.path.relpath(path_file):
                return(path_file)
            else:
                return(False)
        except TypeError:
            
            tk.messagebox.showerror(title='Can not find subdir.', 
                                    message=f'Can not find file "{self.subdir}" in {self.path_exp} .')
            return(False)

    
    def get_path_file(self):
        
        path_file=self.find_file()
        try:
            if os.path.relpath(path_file):
                return(path_file)
            else:
                return(False)
        except TypeError:
            
            tk.messagebox.showerror(title='Can not find file.', 
                                    message=f'Can not find file "{self.filename}" in {self.path_exp} .')
            return(False)
        


            

class Load():
   
        
    def get_file(self):
        """
        

        Returns
        -------
        Content in file in bvte format

        """
        with open(self.path_file, 'r') as file:
            raw=file.read()
            
            file.close()
            
        self.len_raw=len(raw)
        return(raw)  
        
    
    def get_file_byte(self):
        """
        

        Returns
        -------
        Content in file in bvte format

        """
        with open(self.path_file, 'rb') as file:
            raw=file.read()
            
            file.close()
            
        self.len_raw=len(raw)
        return(raw)
    def get_len_raw(self):
        """
        

        Returns
        -------
        Return length of raw file

        """
        return(self.len_raw)
    
    def len_conv(self):
        return(len(self.conv_data))
    
    def get_file_conv(self,form_char='H',size = 2):
        """
        

        Parameters
        ----------
        form_char : CHAR, optional
            DESCRIPTION. The default is 'H'. 'H' refers to unsigned short more:
                struct.unpack() help
                
        size : INT, optional
            DESCRIPTION. The default is 2. Size of the packed value in bytes 
            

        Returns
        -------
        None.

        """
        
        self.conv_data=(st.unpack( form_char * ((self.len_raw // size)), 
                         self.get_file_byte()
                         )
               )
        
        return(self.conv_data)
    
class ExtractPar:
    def __init__(self,
                 file,
                 path_file,
                 start_pattern='\#\#', 
                 find_pattern='((.*)(\=(.*)))', 
                 delete_pattern='[ )(\#\#\$]',):
        
        self.file = file
        self.path_file = path_file
        self.s_pattern=re.compile(start_pattern)
        self.f_pattern=re.compile(find_pattern)
        self.d_pattern=re.compile(delete_pattern)
        self.file_dict= {'name':[],
                         'value':[],
                         'other': []}
        
        self.file_to_dict()
        
    def file_to_dict(self):
        
        splitstr_file = self.file.splitlines()  #split lines in str_file
        
        
        
        for i in range(len(splitstr_file)):
            
            if self.s_pattern.match(splitstr_file[i]):  #find match with start pattern
                
                    lines=re.sub(self.d_pattern,'',splitstr_file[i])    #
                                        
                    reg_val=re.findall(self.f_pattern, lines)
                    
                    self.file_dict['name'].append(reg_val[0][1])
                    self.file_dict['value'].append(reg_val[0][3])
                    
                    k=1
                    prop_other=[]
                    
                    while self.s_pattern.match(splitstr_file[i+k]) is None:

                        prop_other.append(splitstr_file[i+k])
                        k+=1  
                        
                        if i+k == len(splitstr_file):
                            break
                        
                    self.file_dict['other'].append(prop_other)
                    #skip lines from i to k
                    i=k+i       
                           
    
    def return_dict(self):
        
        return(self.file_dict)
    
    def extract(self,path_file,column_dict,item_name):
        
        name= os.path.basename(os.path.normpath(path_file))
        
        if name in path_file:
            for idefix,item in enumerate(self.file_dict['name']):
                if item == item_name:
                    return(self.file_dict[column_dict][idefix])
        
       
                        
    def get_par(self,where,want,form=''):
        
        self.value=self.extract(self.path_file,where,want)
       
        try:
            
            
            if form == 'int':
                return(tuple(map(int,self.value.split(' '))))
            elif form == 'float':
                return(tuple(map(float,self.value.split(' '))))
            elif form == 'perc':
                return(tuple(map(float,self.value.split(' '))))
            else:
                return(self.value)
            
            
        except AttributeError:
            
            if form == 'int':
                return(tuple(map(int,self.value[0].split(' '))))
            elif form == 'float':
                return(tuple(map(float,self.value[0].split(' '))))
            elif form == 'perc':
                return(tuple(map(float,self.value[0].split(' '))))
            else:
                return(self.value)
            
        except TypeError:
            
            self.e_not_found(want)
            
    
    def e_not_found(self,want):
        print(f'Can not find {want} in {self.path_file}')
        
        
    def get_timestamp(self):
        
        return(re.findall('[\d]+',self.get_par('other','OWNER')))

class MultiplePath:
    def assign_path (self):
        if self.multiple and self.filename == 'method':
            
            self.path_exp = self.path_temp
            self.path_file = self.get_path_file()   
           
        elif self.multiple:
            self.path_exp = self.path_subdir
            self.path_file = self.get_path_file()
        else:
            self.path_file = self.get_path_file()
                
    def check_multiple(self):
        if self.multiple:
            split = os.path.split(self.path_exp)
            self.path_temp=split[0]
            self.subdir=split[1]
            self.path_exp=self.path_temp
            self.path_subdir=self.get_subdir()
        else:
            pass      
    
class GetParam(Load,Path,MultiplePath):
    def __init__(self,path,multiple):
        self.multiple = multiple
        self.path_exp = path
        
        self.check_multiple()
        
   
        
        

              
        
        
        self.patch_layout = self.get_patch_layout('int')
        self.patch_size = self.get_patch_size('int')
        self.patch_overlap = self.get_patch_overlap('perc')[0]
        
        self.all_param =  self.patch_size +self.patch_layout  + self.get_patch_overlap('float')
        
                  

    
    def get_patch_layout(self,form):
        self.filename = 'method'
        self.assign_path()
       
        return( ExtractPar(self.get_file(), self.path_file).get_par('other','MPI_PatchLayout',form))
        
    
    def get_patch_size(self,form):
        self.filename = 'reco'
        self.assign_path()
        
        return(ExtractPar(self.get_file(), self.path_file).get_par('other','RECO_size',form))
        
    
    def get_patch_overlap(self,form):
        self.filename = 'method'
        self.assign_path()
        return(ExtractPar(self.get_file(), self.path_file).get_par('value','MPI_PatchOverlap',form))
    
    def get_conv_data(self):
        self.get_conv_data()
        self.filename = '2dseq'
        self.assign_path()
        self.get_file_byte()
        self.conv_data = self.get_file_conv()
        self.len_conv_data=self.len_conv()
                                                          
    
    
    
class Merge(Load,Path,MultiplePath):
    def __init__(self,path,param,method,multiple):
        
        try:
            self.path_exp= path.get()
        except TypeError and AttributeError:
            self.path_exp= path
        
        self.multiple= multiple
        self.method = method
        self.param=param
        self.check_multiple()
        self.filter_param()
        self.get_pix_per_img()
        self.get_conv_data()
        self.get_num_img()
        self.get_mat_size()
        self.get_seq()
        self.get_mat_layout()
        self.ones=self.get_zeros_mat()
        
        
        
        self.compose_img()
        
    def get_mat_layout(self):
        space_coord=self.get_space_coord()
        self.mat_layout= [x+1 for x in list(space_coord)[-1]]
        
    def filter_param(self):

        self.patch_size = self.param[0:3]
        self.patch_layout = self.param[3:6]
        self.patch_overlap = self.param[-1]*0.01
  

        
        
    def get_seq(self):
        """
        Function rescale converted 1D images to sequences of size x, y and 
        z*patch_layout.
        
        Rescale is defined by size given from file reco

        Returns
        -------
        Final sequences

        """
        seq=[]
        for idefix in range(self.num_img):
            if idefix == 0:
                img_one=self.conv_data[0:self.pix_per_img]
                seq.append(np.reshape(img_one,[self.patch_size[0],self.patch_size[1]]))
            else:
                img_one=self.conv_data[self.pix_per_img*idefix:self.pix_per_img*(idefix+1)]
                
                seq.append(np.reshape(img_one,[self.patch_size[0],self.patch_size[1]]))
        
        
        self.seq=seq                                                        
    
    def get_pix_per_img(self):
        self.pix_per_img=self.patch_size[0]*self.patch_size[1]
    
    
    def get_conv_data(self):
        
        self.filename = '2dseq'
        self.assign_path()
        self.get_file_byte()
        self.conv_data = self.get_file_conv()
        self.len_conv_data=self.len_conv()
    
    def get_num_img(self):
        self.num_img=int(self.len_conv_data/self.pix_per_img)
    
    
    def get_mat_size(self):
        
        mat_size=[]
        for idefix,size in enumerate(self.patch_size):
            
            if (self.patch_layout == 1) | (self.patch_overlap==0):
                mat_size.append(size*self.patch_layout[idefix])
                
            elif self.patch_overlap == 1 :
                mat_size.append(size)
                
            else:

                mat_size.append( int(self.patch_layout[idefix]*size-(np.round(size*self.patch_overlap)*(self.patch_layout[idefix]-1))))
        
        return mat_size
        
    def get_zeros_mat(self):
        """
        Returns
        -------
        Function return pre computed amtrix for final image sequences using
        numpy zeros
        """
        zeros_mat= np.zeros(self.get_mat_size()[::-1])
        return zeros_mat
    
    def get_ones_mat(self):
        """
        Returns
        -------
        Function return matrix filled with 1. Matrix is then used as add mat 
        for computing average of intersection in final sequences
        """
        ones_mat = np.ones([self.patch_size[0],self.patch_size[1]])
        return ones_mat
    
    def get_gaussian(self,x,r,alpha):
        
        return(1./(np.sqrt(alpha**m.pi))*np.exp(-alpha*np.power((x - r), 2.)))
    
    def get_gaussian_vect(self,alpha,length,r):
        """
        Parameters
        ----------
        alpha : Int/Float
        length : Int
        r : Int/Float

        Returns
        -------
        final_vect : Vector with symetrical gauss distribution

        """
        if length%2 == 1:
            x = np.linspace(0,2,int(round(length/2))+1)
                        
            vect = self.get_gaussian(x,r, alpha)
                                   
            final_vect= np.concatenate([vect[::-1],vect[1:]])
            #final_vect[final_vect>1] =1
        else:
       
            x=np.linspace(0,2,int(round(length/2)))
            
            vect= self.get_gaussian(x,r, alpha)
            
            final_vect= np.concatenate([vect[::-1],vect])
            #final_vect[final_vect>1] =1
            #final_vect[final_vect>0.2]=
            
        return final_vect
    
    def get_gauss_mat(self,sup=False):
        """
        Function get 3 gaussian distribution then computed 3D gaussian space
        Returns
        -------
        gauss_3D : 3D gaussian distribution

        """
        
        self.alpha=1
        
        gm_x = self.get_gaussian_vect(self.alpha,self.patch_size[0],0)
        gm_y = self.get_gaussian_vect(self.alpha,self.patch_size[1],0)
        gm_z = self.get_gaussian_vect(self.alpha,self.patch_size[2],0)
        
        gauss_3D=np.einsum('i,j,k->kji',gm_y,gm_x,gm_z)
        gauss_3D[gauss_3D[0,:,:].max()>gauss_3D]=gauss_3D[0,:,:].max()
        #gauss_3D[gauss_3D<0.2]=0.2
        
        if sup:
            gauss_3D[gauss_3D>0.1]=1
            return gauss_3D
        else:
            return gauss_3D
    
  
        
    
    def get_space_coord(self):
        """
        Calculate cartesian product of patch layout to moving in precomputed 
        final matrix

        Returns
        -------
        List of coordinations

        """
        return(product(np.arange(0,self.patch_layout[2],1),
                       np.arange(0,self.patch_layout[1],1),
                       np.arange(0,self.patch_layout[0],1)
                       )
               )
    
    def median_patch(self):
        

               
        pactch_len=len(list(self.get_space_coord()))
        med_sub=np.zeros([self.patch_size[2],self.patch_size[0],self.patch_size[1]])
        
        
        
        for l in range(self.patch_layout[0]):
            for k in range(self.patch_layout[1]):
                for i in range(self.patch_layout[2]):
                    patch_med=[]
                    for j in range(pactch_len):
                        patch_med.append( self.seq[i+j*self.mat_layout[2]][l,k])
                
                    med_sub[i,l,k]=statistics.median(patch_med)
                
        return(med_sub)
    
    def border_supress(self):
        
        mask_xy=np.ones([self.patch_size[0],self.patch_size[1]])
        mask_yz=np.ones([self.patch_size[1],self.patch_size[2]])
        
        supress_level=0.0001
        pix=3
        
        
        mask_xy[0:pix,:]=supress_level
        mask_xy[:,0:pix]=supress_level
        mask_xy[-pix:,:]=supress_level
        mask_xy[:,-pix:]=supress_level
        
        mask_yz[0:pix,:]=supress_level
        mask_yz[:,0:pix]=supress_level
        mask_yz[-pix:,:]=supress_level
        mask_yz[:,-pix:]=supress_level
        
        
        supress3D=np.einsum('ij,jk->kji',mask_xy,mask_yz)
        supress3D[supress3D<1]=supress_level 
        return(supress3D)
    
    def from_to(self,coord,idx):
        from_ = int(coord* self.patch_size[idx]-(round(self.patch_size[idx]*self.patch_overlap)*coord))
        to_= int((1+coord)* self.patch_size[idx]-(round(self.patch_size[idx]*self.patch_overlap)*coord))
        return(from_,to_)
    
    def compose_img(self):
        """
        Function for completing images from seq to compose_mat. Then computing
        weighted average and arithmetic average. Weight are defined by gaussian
        distribution.

        """
        
        if self.method == 'Mean':
            
            self.compose_mat_a = self.get_zeros_mat()
            self.divide_mat = self.get_zeros_mat()
            add_mat = self.get_ones_mat()
        elif self.method == 'Gauss':
            gauss_mat = self.get_gauss_mat()
            self.divide_mat = self.get_zeros_mat()
            self.compose_mat_wa= self.get_zeros_mat()
        
        elif self.method == 'Gauss sup':
            gauss_mat = self.get_gauss_mat(sup=True)
            self.divide_mat = self.get_zeros_mat()
            self.compose_mat_wa_sup= self.get_zeros_mat()
        
        elif self.method == 'Supress':
           supress_mat=self.border_supress()
           self.divide_mat = self.get_zeros_mat()
           self.compose_mat_supr= self.get_zeros_mat()
        elif self.method == 'Median':
            med_sub=self.median_patch()
            self.divide_mat_med = self.get_zeros_mat()
            self.divide_mat = self.get_zeros_mat()
            add_mat = self.get_ones_mat()
        
        

        
        space_coord = self.get_space_coord()
        

        
        for idx,[z,y,x] in enumerate(space_coord):
                
                    
            from_seq=int(self.patch_size[2]*idx)
            to_seq=int(self.patch_size[2]*(idx+1))
            
            x_from,x_to=self.from_to(x,0)
            y_from,y_to=self.from_to(y,1)
            z_from,z_to=self.from_to(z,2)
                
                
            if self.method == 'Mean':
                self.compose_mat_a[z_from:z_to,y_from:y_to,x_from:x_to]+=self.seq[from_seq:to_seq]
                self.divide_mat[z_from:z_to,y_from:y_to,x_from:x_to]+=add_mat
            
            elif self.method == 'Gauss':
                self.compose_mat_wa[z_from:z_to,y_from:y_to,x_from:x_to]+=np.multiply(self.seq[from_seq:to_seq],gauss_mat)
                self.divide_mat[z_from:z_to,y_from:y_to,x_from:x_to]+=gauss_mat
                
            elif self.method == 'Supress':
                self.compose_mat_supr[z_from:z_to,y_from:y_to,x_from:x_to]+=np.multiply(self.seq[from_seq:to_seq],supress_mat)
                self.divide_mat[z_from:z_to,y_from:y_to,x_from:x_to]+=supress_mat
                
            elif self.method == 'Median':
                self.divide_mat_med[z_from:z_to,y_from:y_to,x_from:x_to]+=(self.seq[from_seq:to_seq]-med_sub)
                self.divide_mat[z_from:z_to,y_from:y_to,x_from:x_to]+=add_mat
                
            elif self.method == 'Gauss sup':
                self.compose_mat_wa_sup[z_from:z_to,y_from:y_to,x_from:x_to]+=np.multiply(self.seq[from_seq:to_seq],gauss_mat)
                self.divide_mat[z_from:z_to,y_from:y_to,x_from:x_to]+=gauss_mat
    
        

    
        
        
    def get_compose_img(self):
        """
        Returns
        -------
        Return composed sequence. 
    
        """
        if self.method == 'Mean':
            self.divide_mat[self.divide_mat==0]=1     
            self.done_mat= np.divide(self.compose_mat_a,self.divide_mat)
        
        elif self.method == 'Gauss':
             
            self.done_mat=np.divide(self.compose_mat_wa,self.divide_mat)
            
        elif self.method == 'Gauss sup':
             
            self.done_mat=np.divide(self.compose_mat_wa_sup,self.divide_mat)
            
        elif self.method == 'Supress':
            self.done_mat = np.divide(self.compose_mat_supr,self.divide_mat) 
            
        elif self.method == 'Median':
            self.divide_mat[self.divide_mat<0]=0
            self.done_mat= np.divide(self.divide_mat_med,self.divide_mat)
            
         
        return(self.done_mat.astype('uint16'))


 
class DCMHeader: 
    def __init__ (self):
            
        with open('./default.json', 'r') as def_file:
            file = json.load(def_file)
            def_file.close()
        self.dcm_header=file['dcm_header']  
            
    def reset_default(self):
        with open('./default.json', 'r') as def_file:
            file = json.load(def_file)
            def_file.close()
        self.dcm_header=file['dcm_header']  
        return(self.str_to_tk())
    
    def set_new_default(self,new_header):
        for idefix,item in enumerate(new_header):
            str_item = new_header[item].get()
            new_header[item] =str_item
        
        header={'dcm_header':''}
        header['dcm_header'] = new_header 
        
        with open('./default.json', 'w') as out:
            
            json.dump(header, out)
            out.close
            
    def str_to_tk (self):
        tk_str=self.dcm_header
        for idefix,item in enumerate(tk_str):
            str_item = tk_str[item]
            tk_str[item] = tk.StringVar()
            tk_str[item].set(str_item)
            
        return(tk_str)
    
    def get_default(self): 
        
        return(self.dcm_header)
    
    def get_default_tk(self): 
        
        return(self.str_to_tk())
    
class ImageEnhancement:
    
    
    def contrast_brightness(self,image,alpha,beta,max_pix=65535):

        out=np.clip(alpha * image + beta, 0, max_pix)
        return(out.astype(np.uint16))
        
    

if __name__ == '__main__':

    bb=GetParam(tkinter.filedialog.askdirectory())
    

    
# =============================================================================
#     test2=Load(ahoj).get_file()
#     test3=ExtractPar(test2,ahoj)
#     print(test3.get_timestamp())
#     aa=test3.get_par('other','OWNER')
#     bb=Merge(ahoj)
#     print(aa)
# =============================================================================
