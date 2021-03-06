"""Stars indicate priority"""

"""TODO
      ****SAVE ON EXIT****
      add reorderable category
      add alphabetical category (break into a,b,c sub categories.)
      add sort by ingame sorting (art, fish, etc.)
      add super item categories, clothing -> accesories, hats, shoes, socks, etc.
"""

"""BUGS
      Program is slow when changing to categories with a large amount of items
"""      

import wx
import wx.lib.scrolledpanel as scrolled
import pickle           #how the catalogs are stored, fastest method I can think of
import numpy as np      #used for arrays from readcol and items remaining counter
import ast              #convert string trues to bool trues
import glob          
import os               #so this will work on all os, only for directory sep
import time             #used for most recent checked


########################################################################
catalog_dir = ""    #option to allow catalog files in a different directory, e.g. dropbox
pickle_path = catalog_dir+"pickles"+os.sep         #os agnostic directory separator

files = glob.glob(pickle_path+"*.pickle")
filenames = [f.replace(pickle_path,'') for f in files]     #get rid of pickles/
filenames = [f.replace('.pickle','') for f in filenames]     #get rid of .pickle
filenames = sorted(filenames)

class MyTree(wx.TreeCtrl):
   """Our customized TreeCtrl class
   """
   def __init__(self, parent, id, position, size, style):
      """Initialize our tree
      """
      wx.TreeCtrl.__init__(self, parent, id, position, size, style)
      root = self.AddRoot('ACNL Catalog')
      node = {}
      category = {}
      for f in filenames:
         with open(pickle_path+f+".pickle", 'r') as handle:
            dict, unique_dict = pickle.loads(handle.read())
         
         #Find #items not cataloged
         total_items = len(dict["cataloged"])
         items_cataloged = np.sum(np.core.defchararray.count(dict["cataloged"], "True"))   #gives an array of 1(if True) or 0(if False), then sum to get total cataloged
         catalog_remaining = total_items - items_cataloged  #obsolete right now, leaving for future
         
         node[f] = self.AppendItem(root, f+" ("+str(items_cataloged)+"/"+str(total_items)+")")
            
         for k,values in unique_dict.iteritems():
            category[f] = self.AppendItem(node[f], k.decode('utf-8'))   #may have non ascii characters
            for v in sorted(values):      #to alphebetize the subcategories
               self.AppendItem(category[f],v.decode('utf-8'))

         category[f] = self.AppendItem(node[f], "Recently Modified")  #separate since I don't want subcategories


  
class MyFrame(wx.Frame):
   '''Our customized window class
   '''
   def __init__(self, parent, id, title):
      '''Initialize our window
      '''
      
      self.number_of_buttons = 0
      self.dict = {}
      self.unique_dict = {}
      self.item_list = ""
      self.item = ""
      

      wx.Frame.__init__(self, parent, id, title,
                       wx.DefaultPosition, wx.Size(450, 350))

      # Create a splitter window
      self.splitter = wx.SplitterWindow(self, -1)

      # Create the left panel
      leftPanel = wx.Panel(self.splitter, -1)
      # Create a box sizer that will contain the left panel contents
      leftBox = wx.BoxSizer(wx.VERTICAL)

      # Create our tree and put it into the left panel
      self.tree = MyTree(leftPanel, 1, wx.DefaultPosition, (-1, -1),
                        wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT)

      # Add the tree to the box sizer
      leftBox.Add(self.tree, 1, wx.EXPAND)

      # Bind the OnSelChanged method to the tree
      self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)

      # Set the size of the right panel to that required by the tree
      leftPanel.SetSizer(leftBox)

      
      self.rightPanel = scrolled.ScrolledPanel(self.splitter, -1)
      # Create the right panel
      #self.rightPanel = wx.Panel(self.splitter, -1)
      # Create the right box sizer that will contain the panel's contents
      self.rightBox = wx.BoxSizer(wx.VERTICAL)
      # Create a widget to display static text and store it in the right
      # panel
      # Add the display widget to the right panel
      # Set the size of the right panel to that required by the
      # display widget
      self.rightPanel.SetSizer(self.rightBox)
      
      self.rightPanel.SetAutoLayout(True)
      self.rightPanel.SetupScrolling()
      self.rightPanel.Layout()
      # Put the left and right panes into the split window
      self.splitter.SplitVertically(leftPanel, self.rightPanel, sashPosition=200)  #Added sash size, different computers would make the default size 0
      # Create the window in the centre of the screen
      self.Centre()

   def OnSelChanged(self, event):
      '''Method called when selected item is changed
      '''
      # Get the selected item object
      self.saveDict()
      
      
      pieces = []
      
      self.item =  event.GetItem()     #need this to dynamically update tree
      selected_item = self.item
      while self.tree.GetItemParent(selected_item):
         piece = self.tree.GetItemText(selected_item)
         pieces.insert(0, piece)
         selected_item = self.tree.GetItemParent(selected_item)

      item_cat = ''
      item_indiv_cat = ''


      """Get item path and break into appropriate variables
         This is somewhat hardcoded in"""
      
      for p in pieces:        #find what item list that was selected
         p = p.split("(")[0].strip()   #split by (, corresponds to item remaining to catalog
         if p in filenames:
            self.item_list = p

            
      with open(pickle_path+self.item_list+".pickle", 'r') as handle:
         self.dict, self.unique_dict = pickle.loads(handle.read())
      
         
      for p in pieces:
         if p in self.dict.keys():
            item_cat = p
                                                                  #not Recently Modified since no subcategories for it (not even in unique_dict which would break if run) 
      if item_cat != '' and item_cat != "Recently Modified":      #if item_cat is none, then the dict call would break
         for p in pieces:
            if p.encode('utf-8') in self.unique_dict[item_cat]:      #grabs a unicode string, must compare against an non-unicode one
               item_indiv_cat = p

      self.DisplayItems(item_cat, item_indiv_cat)
        
   def DisplayItems(self, item_cat, item_indiv_cat):
      self.removeWidget()    #remove any previously made checkboxes (reset when switching categories)

      self.displayWidget(item_cat, item_indiv_cat)         #display new checkboxes   
      self.Layout()
      self.rightPanel.FitInside()

   
   def addWidget(self, name, cataloged, reorderable):
      """"""
      self.number_of_buttons += 1
      new_button = wx.CheckBox(self.rightPanel, label=name, name=name)
      if not reorderable:
         new_button.SetForegroundColour((255,0,0))   #change text color if can't be reordered   
      new_button.SetValue(cataloged)
      new_button.Bind(wx.EVT_CHECKBOX, self.checked)#lambda e: self.checked(e, dict))
      self.rightBox.Add(new_button, 0, wx.ALL, 5)
      self.rightPanel.Layout()


   def removeWidget(self):
      """"""
      if self.rightBox.GetChildren():
         for i in range(self.number_of_buttons-1, -1, -1):
            self.rightBox.Hide(i)
            self.rightBox.Remove(i)
            self.rightPanel.Layout()

         self.number_of_buttons = 0  
      
   def displayWidget(self, item_cat, item_indiv_cat):
      """
         All strings here are converted to unicode, may contain special characters that don't display correctly
      """  
      num_items = len(self.dict["name"])  #all items in the category

      #Item List 
      if item_cat == '':
         for j in range(num_items):        
            self.addWidget(self.dict["name"][j].decode('UTF-8'),ast.literal_eval(self.dict["cataloged"][j]),ast.literal_eval(self.dict["reorderable"][j]))   #name, cataloged, reorderable
      
      #Subcategory
      if item_cat != '' and item_indiv_cat == '':     #first subcategory 
         
         #Recently Modified Items
         if item_cat == "Recently Modified":     #this requires a loop and different output
            sorted_index = np.argsort(self.dict["Recently Modified"])[::-1]    #want most recently modified not oldest, argsort since the other lists need to be sorted as well
            
            if num_items  < 20:     #to prevent displaying more items than there actually are
               loop_number = num_items 
            else:
               loop_number = 20
            
            for j in range(loop_number):  #only return the 20 most recently modified
               self.addWidget(self.dict["name"][sorted_index[j]],ast.literal_eval(self.dict["cataloged"][sorted_index[j]]),ast.literal_eval(self.dict["reorderable"][sorted_index[j]]))   #name, cataloged, reorderable
         
         #Cataloged Items 
         elif item_cat == "cataloged":      #want to show non-cataloged items for the subcategory listing
            for j in range(num_items):
               if ast.literal_eval(self.dict["cataloged"][j]) == False:
                  self.addWidget(self.dict["name"][j].decode('UTF-8')+": "+self.dict["Obtained From"][j].decode('UTF-8'),ast.literal_eval(self.dict["cataloged"][j]),ast.literal_eval(self.dict["reorderable"][j]))   #name:obtained, cataloged, reorderable
         
         #All other subcategories
         else:
            for j in range(num_items):        
               self.addWidget(self.dict["name"][j].decode('UTF-8')+": "+self.dict[item_cat][j].decode('UTF-8'),ast.literal_eval(self.dict["cataloged"][j]),ast.literal_eval(self.dict["reorderable"][j]))   #name:category, cataloged, reorderable
     
      #Subsubcategories 
      if item_indiv_cat != '':
         for j in range(num_items):        
            if self.dict[item_cat][j].decode('UTF-8') == item_indiv_cat:               #display only items that have this category
               self.addWidget(self.dict["name"][j].decode('UTF-8'),ast.literal_eval(self.dict["cataloged"][j]),ast.literal_eval(self.dict["reorderable"][j])) 
      
      self.rightPanel.Layout()   #format the right panel so the scrollbars get reset and the list resets back up to the top
   
   def checked(self,e):
      sender = e.GetEventObject()
      isChecked = sender.GetValue()
      name = sender.GetLabel()
      
      name = name.split(":")[0]     #for when clicked on category
      name = name.encode('utf-8')
     
      #THIS IS THE PROBLEM LINE 
      item_index = np.where(name == self.dict["name"]) 
      if isChecked:
         self.dict["cataloged"][item_index] = True
      else:
         self.dict["cataloged"][item_index] = False

      self.dict["Recently Modified"][item_index] = time.time()    #to determine last changed, consider when formating output to convert this to human understandable time
         
      self.updateTree()    #right now for updating number of items left to catalog, but allows for all tree manipulation after checking items

   def updateTree(self):   #update text on tree
      total_items = len(self.dict["cataloged"])
      items_cataloged = np.sum(np.core.defchararray.count(self.dict["cataloged"], "True"))   #gives an array of 1(if True) or 0(if False), then sum to get total cataloged
      catalog_remaining = total_items - items_cataloged  #obsolete right now, leaving for future needs
      
      while self.tree.GetItemParent(self.item):       #get the top parent, only want item numbers there   EVENTUALLY, add this for all tree items so this code would be useless then
         prev_item = self.item
         self.item = self.tree.GetItemParent(self.item)
         
      self.item = prev_item   #error when not setting self.item back to the correct item
      
      tree_selection = self.tree.GetItemText(self.item).split("(")[0].strip()    
      self.tree.SetItemText(self.item, tree_selection+" ("+str(items_cataloged)+"/"+str(total_items)+")")    #update item text to correct number cataloged
         
   def saveDict(self):

      #Adding a new category that I would like to organize by without rewriting things
            
      if self.item_list != "":      #to stop it trying to save when first running program
         if "cataloged" not in self.unique_dict.keys():
            self.unique_dict["cataloged"] = ["True", "False"]
         if "Recently Modified" not in self.dict.keys():
            self.dict["Recently Modified"] = np.zeros(len(self.dict["name"]))
         with open(pickle_path+self.item_list+".pickle", 'w') as handle:
            pickle.dump((self.dict,self.unique_dict), handle)     #depositing dict by pickle, lazy and this is fast

class MyApp(wx.App):
   '''Our application class
   '''
   def OnInit(self):
      '''Initialize by creating the split window with the tree
      '''
      frame = MyFrame(None, -1, 'treectrl.py')
      frame.Layout()
      frame.Show(True)
      self.SetTopWindow(frame)
      return True 

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
