"""Stars indicate priority"""

"""TODO
      sort unique_dict values, the indiv_cat values (currently sorted by item name)
      add cataloged category
      add reorderable category
      add alphabetical category (break into a,b,c sub categories.)
      ****show remaining number of items
      add sort by ingame sorting (art, fish, etc.)
      add super item categories, clothing -> accesories, hats, shoes, socks, etc.
"""

"""BUGS
      items with stupid characters (vowels with accents) display incorrectly
      *items with these characters also break saving the entire list
      
      Program is slow when changing to categories with a large amount of items
"""      

import wx
import wx.lib.scrolledpanel as scrolled
import pickle
import numpy as np
import ast
import glob
import os

########################################################################
pickle_path = "pickles"+os.sep

files = glob.glob(pickle_path+"*.pickle")
filenames = [f.replace(pickle_path,'') for f in files]     #get rid of pickles/
filenames = [f.replace('.pickle','') for f in filenames]     #get rid of .pickle

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
         with open(pickle_path+f+".pickle", 'rb') as handle:
            dict, unique_dict = pickle.loads(handle.read())
            
         #Find #items not cataloged
         total_items = len(dict["cataloged"])
         items_cataloged = np.sum(np.core.defchararray.count(dict["cataloged"], "True"))   #gives an array of 1(if True) or 0(if False), then sum to get total cataloged
         catalog_remaining = total_items - items_cataloged
         
         node[f] = self.AppendItem(root, f+" ("+str(catalog_remaining)+")")
         
         for k,values in unique_dict.iteritems():
            category[f] = self.AppendItem(node[f], k)
            for v in values:
               self.AppendItem(category[f],v)
            
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
      self.splitter.SplitVertically(leftPanel, self.rightPanel)
      # Create the window in the centre of the screen
      self.Centre()

   def OnSelChanged(self, event):
      '''Method called when selected item is changed
      '''
      # Get the selected item object
      self.saveDict()
      
      
      pieces = []
      item =  event.GetItem()
      while self.tree.GetItemParent(item):
         piece = self.tree.GetItemText(item)
         pieces.insert(0, piece)
         item = self.tree.GetItemParent(item)

      item_cat = ''
      item_indiv_cat = ''


      """Get item path and break into appropriate variables
         This is somewhat hardcoded in"""
      
      for p in pieces:        #find what item list that was selected
         p = p.split("(")[0].strip()   #split by (, corresponds to item remaining to catalog
         if p in filenames:
            self.item_list = p

            
      with open(pickle_path+self.item_list+".pickle", 'rb') as handle:
         self.dict, self.unique_dict = pickle.loads(handle.read())
            
      for p in pieces:        
         if p in self.dict.keys():
            item_cat = p
      
      if item_cat != '':      #if item_cat is none, then the dict call would break
         for p in pieces:
            if p in self.unique_dict[item_cat]:
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
      if item_cat == '':   #topmost selection, i.e. just the item list
         for j in range(len(self.dict["name"])):        #loop through all items in dict, name key just so I can find the length of the list in the dict, I want to print all items in the list
            self.addWidget(self.dict["name"][j],ast.literal_eval(self.dict["cataloged"][j]),ast.literal_eval(self.dict["reorderable"][j]))   #name, cataloged, reorderable
      if item_cat != '' and item_indiv_cat == '':
         for j in range(len(self.dict["name"])):        
            self.addWidget(self.dict["name"][j]+": "+self.dict[item_cat][j],ast.literal_eval(self.dict["cataloged"][j]),ast.literal_eval(self.dict["reorderable"][j]))   #name:category, cataloged, reorderable
      if item_indiv_cat != '':
         for j in range(len(self.dict[item_cat])):        #loop through all items in dict, dict has keys of the categories and values for each item
            if self.dict[item_cat][j] == item_indiv_cat:               #display only items that have this category
               self.addWidget(self.dict["name"][j],ast.literal_eval(self.dict["cataloged"][j]),ast.literal_eval(self.dict["reorderable"][j])) 
      self.rightPanel.Layout()
   
   def checked(self,e):
      sender = e.GetEventObject()
      isChecked = sender.GetValue()
      name = sender.GetLabel()
      
      name = name.split(":")[0]     #temporary until I fix display
      
      item_index = np.where(self.dict["name"]==name)
 
      if isChecked:
         self.dict["cataloged"][item_index] = True
      else:
         self.dict["cataloged"][item_index] = False
         
         
   def saveDict(self):
      if self.item_list != "":      #to stop it trying to save when first running program
         with open(pickle_path+self.item_list+".pickle", 'wb') as handle:
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
  