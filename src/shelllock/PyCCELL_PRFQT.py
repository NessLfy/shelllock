#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statistics
import re 
import warnings 

warnings.filterwarnings("ignore")

def excelreader(path,gain):
    # Open the file
    df = pd.read_excel(path)
    
    # find where there is data
    
    start = 0
    stop = 0

    for l,i in enumerate(df[df.columns[1]]):
        if i == 'Time':
            start = l
        elif start != 0:
            if str(i) == 'nan':
                stop = l
        if start and stop != 0:
            break

    leng = stop - start
    
    #truncate the dataframe
    
    if gain == 0:
        df = df.truncate(before = start , after = stop - 1)
    else:
        df = df.truncate(before = start + (gain*leng) + (gain*3) , after = stop + (gain*leng) + (gain*3)-1)
    
    #drop the first column (nan)
    
    df.drop(columns=df.columns[0], axis=1,  inplace=True)
    
    # make the first row as header
    
    df.columns = df.iloc[0]
    df = df[1:]
    
    df.reset_index(inplace=True)
    df.drop(columns=df.columns[0], axis=1,  inplace=True)
    
    return df

def plot_raw_data(data,nr,nc):
    fig,axs = plt.subplots(nr, nc, sharex = True, sharey = True,figsize=(30, 30))
    counter = 0
    for i in range(nr):
        for j in range(nc):
            if data.columns[counter] != 'Time':
                axs[i,j].plot(data['Time'],data[data.columns[counter]])
                counter+=1
            else:
                counter+=1
        #plt.ylim(0,0.9)
    #plt.show()


def collapse(data,tripl,control):
    
    #create a variable with names of the columns
    
    col=[]
    name =[]
    
    for ch in data.columns[2:]:
        col.append(ch)
    #if the imput is line then the triplicate are a list of the column name 3 by 3 
    if tripl == 'line': 

        i = 0
        j = 0
        while i < round((len(col)/3),0):
            name.append([col[j],col[j+1],col[j+2]])
            i= i +1
            j = j+3 
            
    elif tripl == 'col':
        #create a list of the repeating letters
        duplicates = []
        for char in re.findall('[a-zA-Z]',str(col)):
            '''
             checking whether the character have a duplicate or not             
            '''
            if str(col).count(char) > 1:
                []
            ## appending to the list if it's already not present

            if char not in duplicates :

                duplicates.append(char)
        
        #create a list of the repeated number
        b = list(np.array_split(re.findall(r'\d+ ?',str(col)),len(duplicates))[0])

        #for each repeating number add the repeating letter 

        li = []

        for i in b :
            for j in duplicates :
                li.append(j+str(i))

        #create a list of list containing 3 by 3 the name of the previous list

        i = 0 
        j = 0
        name=[]

        while i < len(li)/3:
            name.append([li[j],li[j+1],li[j+2]])
            i= i +1
            j = j+3  
            
    else : 
        name = col
        
    pos = []
    collapse = name
    list_bg = control
    
    df_Fbg = data[list_bg]
    df_Fbg['mean'] = df_Fbg.mean(axis=1)
    std = []
    for col,i in zip(collapse,range(len(collapse))):
        
        x = [x for x in col if x in data.columns]
        df_flu = data[x]
        df_flu['mean'] = df_flu.mean(axis=1)
        std.append(df_flu.std(axis=1))
        df_flu['cor'] = df_flu['mean']-df_Fbg['mean']

        # Build the Backgruond Table...
        # TIME
        df_flut = data['Time']

        # MEAN
        df_flut['mean'] = df_flu['mean']
        df_flut['cor'] = df_flu['cor']

        #df_flut.head()

        data[str(col)] = df_flut['cor']
    
    for i in range(len(name)):
        pos.append(str(name[i]))
    
    df_Fcollapse = data[pos]
    
    df_Fcollapse[df_Fcollapse<0]=0
    
    df_Fcollapse['Time'] = data['Time']
    
    # add the std value to a dataframe to concatenate to the new dataframe
    
    df = pd.DataFrame(std)
    df = df.T
    
    df_Fcollapse = pd.concat([df_Fcollapse,df],axis=1)
    
    return (df_Fcollapse)


def plot_triplicates(data,sa):
    std = []
    for i in data.columns:
        std.append(statistics.stdev(data[i]))
    yerr=std
    if sa == "NO":
        for col,i in zip(data.columns,range(len(data.columns.values)-1)):
            plt.errorbar(data['Time'],data[col],yerr=yerr[i],label=data.columns.values[:-1][i])
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.show()
    elif sa =="YES":
        for col,i in zip(data.columns,range(len(data.columns.values)-1)):
            plt.errorbar(data['Time'],data[col],yerr=yerr[i],label=data.columns.values[:-1][i])
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #plt.show()


def main(data,gain,nr,nc,tripl,control,sa):
    
    file = excelreader(data,gain)
        
    plot_raw_data(file,nr,nc)
    
    fileC = collapse(file,tripl,control)
    
    plot_triplicates(fileC,sa)
        
    return fileC

def mainf(data,gain,tripl,control):
    
    file = excelreader(data,gain)
        
    fileC = collapse(file,tripl,control)
    
    return fileC
    
#test = main('results/SHERLOCK/1st_try_probe_dilution/first_sherlock_probe_concentr_modif.xlsx',50
            #,"NO",3,5,'col',['M23', 'N23', 'O23'],"YES")

