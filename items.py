from readcol import *
import numpy as np
import ast
import collections
import glob
import pickle
import os

def items():
   csv_path = "csvs"+os.sep
   pickle_path = "pickles"+os.sep

   files = glob.glob(csv_path+"*.csv")
   for f in files:
      dict = readcol(f,asdict=True,fsep="`")
      dict.pop("\n", None)    #for some reason readcol grabs the newline character
      
      unique_dict = {}
      key_list = ["name","Sells For","Purchase Price","reorderable","cataloged"]    #keys that aren't useful to sort by

      for k,v in dict.iteritems():
         if k not in key_list:      #keys that I want to sort by
            unique_dict[k] = list(collections.OrderedDict.fromkeys(v))     #list removes non-unique values
            if unique_dict[k] == ['-']:      #if the only value is -, then that is not something useful to sort by
               unique_dict.pop(k, None)      
         
      with open(pickle_path+f[len(csv_path):-3]+"pickle", 'wb') as handle:
         pickle.dump((collections.OrderedDict(sorted(dict.items())), collections.OrderedDict(sorted(unique_dict.items()))), handle)     #depositing dict by pickle, lazy and this is fast
   
   #return collections.OrderedDict(sorted(dict.items())), collections.OrderedDict(sorted(unique_dict.items()))
   
items()
 



   