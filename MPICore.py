import os
import struct
import re
import numpy as np
import pandas as pd
from itertools import product




class RawData:
    def __init__(self,path):
        self.path_raw=path
        
        with open(self.path_raw,'rb') as byte_file:
            self.raw_data = byte_file.read()
            byte_file.close()
            
        self.conv_data = struct.unpack("H" * ((len(self.raw_data))//2), self.raw_data)
        
    def get_raw(self):
        return(self.raw_data)
    
    
    def get_converted(self):
        return (self.conv_data)
    
    def lenght(self):
        return (len(self.conv_data))
    
    
class CalParamCalSeq:
    def __init__(self,conv_data,patch_layout,patch_overlap,size_XYZ):
        
        self.patch_layout = patch_layout
        self.patch_overlap = patch_overlap
        self.size_XYZ = size_XYZ
        self.conv_data=conv_data
        self.len_data = len(conv_data)
        self.seq = []
        
        #cubes refer to one sequence of measuring (x y 1)
        #patch_layout[0] => x, patch_layout[1] => y, patch_layout[2] => z,
        self.num_cubes = self.patch_layout[0]*self.patch_layout[1]*self.patch_layout[2]
        
        #size_XYZ[0] => size in x, size_XYZ[1] => size in y
        self.pix_per_img=self.size_XYZ[0]*self.size_XYZ[1]
        
        #numbers of image
        self.num_img = int(self.len_data/self.pix_per_img)
        
        
        self.mat_size=[]
        
        for idx,size in enumerate(self.size_XYZ):
            
            if (self.patch_layout == 1) | (self.patch_overlap==0):
                self.mat_size.append(size*self.patch_layout[idx])
                
            elif self.patch_overlap == 1 :
                self.mat_size.append(size)
                
            else:

                self.mat_size.append( int(self.patch_layout[idx]*size-(round(size*self.patch_overlap)*(self.patch_layout[idx]-1))))
                
        
        
    def get_num_img(self):
        return(self.num_img)
    
    def get_pix_per_img(self):
        return (self.pix_per_img)
    
    def get_num_cubes(self):
        return (self.num_cubes)
    
    def get_mat_size(self):
        return (self.mat_size)

    
    def get_seq(self):
        
        for idx in range(self.num_img):
            if idx == 0:
                img_one=self.conv_data[0:self.pix_per_img]
                self.seq.append(np.reshape(img_one,[self.size_XYZ[0],self.size_XYZ[1]]))
            else:
                img_one=self.conv_data[self.pix_per_img*idx:self.pix_per_img*(idx+1)]
                
                self.seq.append(np.reshape(img_one,[self.size_XYZ[0],self.size_XYZ[1]]))
        
        
        return(self.seq)
    
    def get_mat(self):
        return(np.zeros(self.mat_size[::-1]))
        
    def get_add_mat(self):
        return(np.ones([self.size_XYZ[0],self.size_XYZ[1]]))
    
    def get_space_coord(self):
        return(product(np.arange(0,self.patch_layout[2],1),
                       np.arange(0,self.patch_layout[1],1),
                       np.arange(0,self.patch_layout[0],1)
                       )
               )

        
    
class MPIMerge:
    def __init__(self,seq,comp_mat,div_mat,add_mat,space_coord,patch_layout,patch_overlap):
        self.seq = seq
        self.compose_mat = comp_mat
        self.divide_mat = div_mat        
        self.add_mat = add_mat
        self.space_coord= space_coord
        self.patch_overlap = patch_overlap
        self.patch_layout = patch_layout
        

        
    def get_compose_img(self):
        
        for idx,[z,y,x] in enumerate(self.space_coord):
                
                    
                from_seq=int(self.patch_layout[2]*idx)
                to_seq=int(self.patch_layout[2]*(idx+1))
            
                from_x_comp = int(x* self.patch_layout[0]-(round(self.patch_layout[0]*self.patch_overlap)*x))
                to_x_comp = int((1+x)* self.patch_layout[0]-(round(self.patch_layout[0]*self.patch_overlap)*x))
                
                from_y_comp = int(y* self.patch_layout[1]-(round(self.patch_layout[1]*self.patch_overlap)*y))
                to_y_comp = int((1+y)* self.patch_layout[1]-(round(self.patch_layout[1]*self.patch_overlap)*y))
                
                from_z_comp=int((z)* self.patch_layout[2]-(round(self.patch_layout[2]*self.patch_overlap)*z))
                to_z_comp=int((1+z)* self.patch_layout[2]-(round(self.patch_layout[2]*self.patch_overlap)*z))
                
                
                self.compose_mat[from_z_comp:to_z_comp,from_y_comp:to_y_comp,from_x_comp:to_x_comp]+=self.seq[from_seq:to_seq]
                self.divide_mat[from_z_comp:to_z_comp,from_y_comp:to_y_comp,from_x_comp:to_x_comp]+=self.add_mat
                
        self.divide_mat[self.divide_mat==0]=1       
        self.done_mat= np.divide(self.compose_mat,self.divide_mat) 
        
        return(self.done_mat.astype('uint16'))
    
    
class GetPath:
    def __init__(self, path_dir, filename ):
        
        self.path_dir = path_dir 
        self.filename = filename
        
        
        for root, dirs, files in os.walk(self.path_dir):  
            if filename in files:
               self.froot=( f'{root}/{self.filename}')
                
    def __call__(self):
        
        
        try:
            return (os.path.relpath(self.froot))
        except AttributeError:
            return(False)
            pass
        
        
            
                
class LoadProperties:
    def __init__(self, path_str_file, path_dir, filename, start_pattern='\#\#', find_pattern='((.*)(\=(.*)))', delete_pattern='[ )(\#\#\$]',dcm_name='./MRIm180.dcm'):
        
        self.path_str_file=path_str_file
        
        with open(self.path_str_file,'r') as str_file:
            self.str_content = str_file.read()
            str_file.close()
        
    
        self.path_dir = path_dir
        self.filename=filename
        self.s_pattern=re.compile(start_pattern)
        self.f_pattern=re.compile(find_pattern)
        self.d_pattern=re.compile(delete_pattern)
        self.dcm_name = dcm_name
        self.prop_dict= {'name':[],
                         'value':[],
                         'other': []}
    

        
        splitstr_file = self.str_content.splitlines()  #split lines in str_file
        
        
        
        for i in range(len(splitstr_file)):
            
            if self.s_pattern.match(splitstr_file[i]):  #find match with start pattern
                
                    lines=re.sub(self.d_pattern,'',splitstr_file[i])    #
                                        
                    reg_val=re.findall(self.f_pattern, lines)
                    
                    self.prop_dict['name'].append(reg_val[0][1])
                    self.prop_dict['value'].append(reg_val[0][3])
                    
                    k=1
                    prop_other=[]
                    
                    while self.s_pattern.match(splitstr_file[i+k]) is None:

                        prop_other.append(splitstr_file[i+k])
                        k+=1  
                        
                        if i+k == len(splitstr_file):
                            break
                        
                    self.prop_dict['other'].append(prop_other)
                    i=k+i
        
    
    def rec_param(self):
        
        
        if 'reco' in self.path_str_file:
                       
            for idx,item in enumerate(self.prop_dict['name']):
                if item == 'RECO_size':
                    self.size_px=tuple(map(int,self.prop_dict['other'][idx][0].split(' ')))
            
            self.out=self.size_px
            
        if 'method' in self.path_str_file:
            
            for idx,item in enumerate(self.prop_dict['name']):
                if item == 'MPI_PatchOverlap':
                    self.overlap = int(self.prop_dict['value'][idx][:] )
                    
                    
                    
                elif item == 'MPI_PatchLayout':
                    self.layout = tuple(map(int,self.prop_dict['other'][idx][0].split(' ')))
                    
                elif item == 'OWNER':
                    
                    self.time_str = self.prop_dict['other'][idx][0]
                    
            self.out=[self.overlap,self.layout]
                
        return self.out
    
    def get_timestamp(self):
        
        self.splitted = self.time_str.split(' ')
        self.time_stamp=re.findall('[\d]+',self.time_str)
            
        return(self.time_stamp)
        
            
    def file2csv(self):
        
        #get rid of [] and ''
        pd.DataFrame.from_dict(self.prop_dict).to_csv(os.path.join(self.path_dir,self.filename))
    
