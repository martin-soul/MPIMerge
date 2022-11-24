import os
from struct import unpack
from re import findall, sub, compile
from numpy import ones, zeros, divide, reshape, arange, einsum, exp, power,linspace,concatenate,multiply,average
from math import pi, sqrt
from itertools import product
#from scipy.signal import gaussian
# import pandas as pd


class RawData:
    def __init__(self,path):
        """
        Function for opening data as rb (read byte),
        then converted to 16 bit unsign int

        Parameters
        ----------
        path : string 
            path to file with 2dseq
        Returns
        -------
        
        """
        self.path_raw=path
        
        with open(self.path_raw,'rb') as byte_file:
            self.raw_data = byte_file.read()
            byte_file.close()
            
        self.conv_data = unpack("H" * ((len(self.raw_data))//2), self.raw_data)
        
    def get_raw(self):
        """
        Returns
        -------
        Function return raw data.

        """
        return(self.raw_data)
    
    
    def get_converted(self):
        """
        Returns 
        -------
        Function return coverted data in little edian 16 bit unsign

        """
        return (self.conv_data)
    
    def lenght(self):
        """
        Returns
        -------
        Function return lenght in z axis of converted data 
        """
        return (len(self.conv_data))
    
    
class CalParamCalSeq:
    def __init__(self,conv_data,patch_layout,patch_overlap,size_XYZ):
        """
    
        Parameters
        ----------
        conv_data : List of arrays
            Converted dat
        patch_layout : Tuple 
            Patch layout of all images from file method 
        patch_overlap : Int
            Patch overlap in percent from file method 
        size_XYZ : Tuple
            Size of on patch in px i order x, y, z from file reco 

        Returns
        -------
        None.

        """
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
        """
        Returns
        -------
        Numbers of images

        """
        return(self.num_img)
    
    def get_pix_per_img(self):
        """
        Returns
        -------
        Return length in px of one image
        
        """
        return (self.pix_per_img)
    
    def get_num_cubes(self):
        """
        Returns
        -------
        Return number of all cubes/patch in sequences

        """
        return (self.num_cubes)
    
    def get_mat_size(self):
        """
        Returns
        -------
        Return size of outcome/final sequence 
        """
        return (self.mat_size)

    
    def get_seq(self):
        """
        Function rescale converted 1D images to sequences of size x, y and 
        z*patch_layout.
        
        Rescale is defined by size given from file reco

        Returns
        -------
        Final sequences

        """
        for idx in range(self.num_img):
            if idx == 0:
                img_one=self.conv_data[0:self.pix_per_img]
                self.seq.append(reshape(img_one,[self.size_XYZ[0],self.size_XYZ[1]]))
            else:
                img_one=self.conv_data[self.pix_per_img*idx:self.pix_per_img*(idx+1)]
                
                self.seq.append(reshape(img_one,[self.size_XYZ[0],self.size_XYZ[1]]))
        
        
        return(self.seq)
    
    def get_mat(self):
        """
        Returns
        -------
        Function return pre computed amtrix for final image sequences using
        numpy zeros
        """
        return(zeros(self.mat_size[::-1]))
        
    def get_ones_mat(self):
        """
        Returns
        -------
        Function return matrix filled with 1. Matrix is then used as add mat 
        for computing average of intersection in final sequences
        """
        return(ones([self.size_XYZ[0],self.size_XYZ[1]]))
    

    def get_gaussian(self,alpha,length,r):
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
            x1 = linspace(0,2,int(round(length/2))+1)
                        
            vect1=1./(sqrt(alpha**pi))*exp(-alpha*power((x1 - r), 2.))
                                   
            final_vect= concatenate([vect1[::-1],vect1[1:]])
            #final_vect[final_vect>1] =1
        else:
       
            x=linspace(0,2,int(round(length/2)))
            
            vect=1./(sqrt(alpha**pi))*exp(-alpha*power((x - r), 2.))
            
            final_vect= concatenate([vect[::-1],vect])
            #final_vect[final_vect>1] =1
            #final_vect[final_vect>0.2]=
        return final_vect
    
    def get_gauss_mat(self):
        """
        Function get 3 gaussian distribution then computed 3D gaussian space
        Returns
        -------
        gauss_3D : 3D gaussian distribution

        """
        
        self.alpha=1
        gm_x = self.get_gaussian(self.alpha,self.size_XYZ[0],0)
        gm_y = self.get_gaussian(self.alpha,self.size_XYZ[1],0)
        gm_z = self.get_gaussian(self.alpha,self.size_XYZ[2],0)
        gauss_3D=einsum('i,j,k->kji',gm_y,gm_x,gm_z)
        gauss_3D[gauss_3D[0,:,:].max()>gauss_3D]=gauss_3D[0,:,:].max()
        #gauss_3D[gauss_3D<0.2]=0.2
        return gauss_3D+2


    def get_space_coord(self):
        """
        Calculate cartesian product of patch layout to moving in precomputed 
        final matrix

        Returns
        -------
        List of coordinations

        """
        return(product(arange(0,self.patch_layout[2],1),
                       arange(0,self.patch_layout[1],1),
                       arange(0,self.patch_layout[0],1)
                       )
               )

        
    
class MPIMerge:
    def __init__(self,seq,comp_mat,div_mat,add_mat,gauss_mat,space_coord,patch_layout,patch_overlap):
        """
        

        Parameters
        ----------
        seq : List of arrays
            Sequention of images
        comp_mat : List of arrays
            Compose matrix for inserting images from seq
        div_mat : List of arrays
            Divison matrix (same matrix as comp) for calculate average 
        in intersection
        add_mat : Array of int
            Addition matrix for add to div_mat
        gauss_mat : List of arrays
            Gaussian matrix with weight defined by gaussian distribution
        space_coord : List of Tuple
            Coordination for moving in space defined by patch layout
        patch_layout : Tuple
            Layout of patches
        patch_overlap : Tuple
            Overlap of patches

        """
        
        self.seq = seq
        self.compose_mat_a = comp_mat
        self.divide_mat_a = div_mat   
        self.divide_mat_wa =div_mat.copy()
        self.add_mat = add_mat
        self.gauss_mat = gauss_mat
        self.space_coord= space_coord
        self.patch_overlap = patch_overlap
        self.patch_layout = patch_layout
        self.compose_mat_wa=comp_mat.copy()

        
    def compose_img(self):
        """
        Function for completing images from seq to compose_mat. Then computing
        weighted average and arithmetic average. Weight are defined by gaussian
        distribution.

        """
        
        for idx,[z,y,x] in enumerate(self.space_coord):
                
                    
                from_seq=int(self.patch_layout[2]*idx)
                to_seq=int(self.patch_layout[2]*(idx+1))
            
                from_x_comp = int(x* self.patch_layout[0]-(round(self.patch_layout[0]*self.patch_overlap)*x))
                to_x_comp = int((1+x)* self.patch_layout[0]-(round(self.patch_layout[0]*self.patch_overlap)*x))
                
                from_y_comp = int(y* self.patch_layout[1]-(round(self.patch_layout[1]*self.patch_overlap)*y))
                to_y_comp = int((1+y)* self.patch_layout[1]-(round(self.patch_layout[1]*self.patch_overlap)*y))
                
                from_z_comp=int((z)* self.patch_layout[2]-(round(self.patch_layout[2]*self.patch_overlap)*z))
                to_z_comp=int((1+z)* self.patch_layout[2]-(round(self.patch_layout[2]*self.patch_overlap)*z))
                
                
                self.compose_mat_a[from_z_comp:to_z_comp,from_y_comp:to_y_comp,from_x_comp:to_x_comp]+=self.seq[from_seq:to_seq]
                self.divide_mat_a[from_z_comp:to_z_comp,from_y_comp:to_y_comp,from_x_comp:to_x_comp]+=self.add_mat
                self.compose_mat_wa[from_z_comp:to_z_comp,from_y_comp:to_y_comp,from_x_comp:to_x_comp]+=multiply(self.seq[from_seq:to_seq],self.gauss_mat)
                self.divide_mat_wa[from_z_comp:to_z_comp,from_y_comp:to_y_comp,from_x_comp:to_x_comp]+=self.gauss_mat
                
        #self.divide_mat[self.divide_mat==0]=1       

      
        
    def get_compose_img_a(self):
        """
        Returns
        -------
        Return composed sequence. 

        """
        
        self.done_mat_a= divide(self.compose_mat_a,self.divide_mat_a) 
        return(self.done_mat_a.astype('uint16'))
    
    def get_compose_img_wa(self):
        """
        Returns
        -------
        Return composed sequence. 

        """
        self.done_mat_a= divide(self.compose_mat_a,self.divide_mat_a) 
        self.done_mat_wa=divide(self.compose_mat_wa,self.divide_mat_wa) #*10+1
        return(self.done_mat_wa.astype('uint16'))
    
class GetPath:
    def __init__(self, path_dir, filename ):
        """
        

        Parameters
        ----------
        path_dir : String
            Path to directory with experiment
        filename : String
            Name of file to open

        """
        self.path_dir = path_dir 
        self.filename = filename
        
        
        for root, dirs, files in os.walk(self.path_dir):  
            if filename in files:
               self.froot=( f'{root}/{self.filename}')
                
    def __call__(self):
        """
        Returns
        -------
        After call return path or False
        False mean path was not found

        """
        
        try:
            return (os.path.relpath(self.froot))
        except AttributeError:
            return(False)
            pass
        
        
            
                
class LoadProperties:
    def __init__(self, 
                 path_str_file, 
                 path_dir, 
                 filename, 
                 start_pattern='\#\#', 
                 find_pattern='((.*)(\=(.*)))', 
                 delete_pattern='[ )(\#\#\$]',
                 dcm_name='./MRIm180.dcm'):
        
        """
        
        Parameters
        ----------
        path_str_file : String
            Path to string file (default is reco,method,2dseq)
        path_dir: String
            Path dir to experiment
        filename : String
            Name of file.
        start_pattern : String, 
            Pattern start every new line in  file. The default is '\#\#'.
        find_pattern : String, optional
            Pattern for fiding parameters. The default is '((.*)(\=(.*)))'.
        delete_pattern : String, optional
            Pattern what has to be deleted. The default is '[ )(\#\#\$]'.
        dcm_name : String, optional
            Path to file with dcm (must stay in same dir as app).
            The default is './MRIm180.dcm'.

        """
        self.path_str_file=path_str_file
        
        with open(self.path_str_file,'r') as str_file:
            self.str_content = str_file.read()
            str_file.close()
        
    
        self.path_dir = path_dir
        self.filename=filename
        self.s_pattern=compile(start_pattern)
        self.f_pattern=compile(find_pattern)
        self.d_pattern=compile(delete_pattern)
        self.dcm_name = dcm_name
        self.prop_dict= {'name':[],
                         'value':[],
                         'other': []}
    

        
        splitstr_file = self.str_content.splitlines()  #split lines in str_file
        
        
        
        for i in range(len(splitstr_file)):
            
            if self.s_pattern.match(splitstr_file[i]):  #find match with start pattern
                
                    lines=sub(self.d_pattern,'',splitstr_file[i])    #
                                        
                    reg_val=findall(self.f_pattern, lines)
                    
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
        """
        Find and return necessary parameters from string file (methods, reco)
        
        Returns
        -------
        string
            Needed parameters

        """
        
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
        """
        

        Returns
        -------
        String
            Return timestamp of measurment

        """
        
        self.splitted = self.time_str.split(' ')
        self.time_stamp=findall('[\d]+',self.time_str)
            
        return(self.time_stamp)
        
            
# =============================================================================
#     def file2csv(self):
#         
#         #get rid of [] and ''
#         from_dict(self.prop_dict).to_csv(os.path.join(self.path_dir,self.filename))
# =============================================================================

    
