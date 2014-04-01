import requests
import collections
import string
import codecs

def get_items():
   url = "http://moridb.com/items/"
   categories = ["hats", "accessories", "tops", "bottoms", "dresses", "socks", "shoes", "umbrellas", "furniture", "wallpaper", "flooring", "music", "bugs", "fish", "fossils", "art", "trees", "fruit", "flowers", "mushrooms", "seashells", "ore", "gyroids", "tools", "balloons", "stationery"]
   #categories = ["furniture"]  #TESTING
   dict = {}
   key_list = {}
   
   for cat in categories:
      print cat
      if cat in ["hats", "accessories", "tops", "bottoms", "dresses", "socks", "shoes", "umbrellas"]:
         key_list[cat] = ["name","Interior Theme","Fashion Theme","Obtained From","Sells For","Set","Purchase Price","reorderable"]
      elif cat in ["furniture", "wallpaper", "flooring"]:
         key_list[cat] = ["name","Interior Theme","Obtained From","Sells For","Set","Purchase Price","reorderable"]
      elif cat in ["music"]:
         key_list[cat] = ["name","Interior Theme","Obtained From","Sells For","Purchase Price","reorderable"]
      elif cat in ["bugs", "fish"]:
         key_list[cat] = ["name","Appears","Obtained From","Sells For","reorderable"]
      elif cat in ["fossils","gyroids","balloons"]:
         key_list[cat] = ["name","Interior Theme","Obtained From","Sells For","reorderable"]
      elif cat in ["art"]:
         key_list[cat] = ["name","Interior Theme","Obtained From","Sells For","Purchase Price","reorderable"]
      elif cat in ["trees","fruit","mushrooms","seashells", "ore","tools"]:
         key_list[cat] = ["name","Obtained From","Sells For","reorderable"]
      elif cat in ["stationery","flowers"]:   
         key_list[cat] = ["name","Obtained From","Sells For","Purchase Price","reorderable"]
      key_list[cat].append("cataloged")   
         
      output = codecs.open(cat+".csv","w",'utf-8')      #since repeated callings is slow, requires internet, and it locks you out if you make repeated calls
      
      for item_cat in sorted(key_list[cat]):
         output.write(item_cat)
         output.write("`")   
      output.write("\n")
      
      more_pages = True
      webpage = url+cat
      page_limit = 1000 # trying to make it 10000 breaks the website, therefore going to need at least two pages for furniture
      page_start = 0

      while(more_pages): 
         dict = {}      #this needs to be here so that prev_dict can be set

         limit = str(page_limit)
         offset = str(page_start)
         payload = {'limit': limit, 'offset': offset}
         f = requests.get(webpage,params=payload).text
         
         itemlist_start = f.find("<a class=")      #need to do this first since this exists for MoriDB name 
         for i in range(page_start,page_start+page_limit):
            prev_dict = dict
            if 'name' not in prev_dict:      #if first pass through no keys in dict -> no keys in prev_dict
               prev_dict['name'] = [0,itemlist_start]
               
            dict = {}
            
            name_start = f.find("<a class=",itemlist_start+len("<a class="))
            info_start = f.find('">', name_start)+len('">')
            info_end   = f.find('</a>', info_start)
            dict['name'] = [info_start,info_end]
            if prev_dict['name'][1] > dict['name'][0]:   #it looped to the top
               dict = {}
               break
            
            more_info = True
            dict["reorderable"] = "False"
            dict['cataloged'] = "False"
            while(more_info):
               info_name_start = f.find("<dt>",info_end)+len("<dt>")
               
               info_name_end = f.find("</dt>",info_name_start)
               key = f[info_name_start:info_name_end].strip()
               
               info_start = f.find("<dd>",info_name_end)+len("<dd>")
                  
               if info_start < info_end or "</div>" in f[info_end:info_start]:    #if a new item there will be multiple div breaks between end of previous info to start of next
                  more_info = False
                  itemlist_start = info_end
                  break
                  
               info_end = f.find("</dd>",info_start)
               
               if "Set" in key:     #has a hyperlink to the set name
                  info_start = f.find(">",info_start)+len(">")
                  info_end = f.find("</a>",info_start)
               if "Purchase Price" in key:   #if can be reordered there is a book img
                  if f.find("catalog",info_start,info_end) != -1:
                     dict["reorderable"] = "True"
                     info_end = f.find("<abbr",info_start)
               
               dict[key] = [info_start,info_end]

            for k in key_list[cat]:
               if not k in dict.keys():
                  dict[k] = "non-existent"
            
            sorted_dict = collections.OrderedDict(sorted(dict.items()))
            for k,v in sorted_dict.iteritems():
               if v == "non-existent":    #no info for particular category
                  output.write("-")
               elif v == "True":
                  output.write("True")
               elif v == "False":
                  output.write("False")
               elif "&amp;" in f[v[0]:v[1]]:
                  output.write(f[v[0]:v[1]].replace("&amp;","&").strip())
               elif "&#39;" in f[v[0]:v[1]]:
                  output.write(f[v[0]:v[1]].replace("&#39;","'").strip())
               else:
                  output.write(f[v[0]:v[1]].strip())
               output.write("`")
            output.write("\n")
         
         if "next disabled" in f:
            more_pages = False
         else:
            page_start += page_limit
         
      output.close()
      
get_items()
   
   