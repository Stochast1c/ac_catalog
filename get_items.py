import requests
url = "http://www.thonky.com/animal-crossing-new-leaf/list-of-furniture/"
def get_items():
   output = open("furniture.txt","w")      #since repeated callings is slow, requires internet,
                                           #and it locks you out if you make repeated calls
   f = requests.get(url).text
   first_item = f.find("1-Up Mushroom") - 10
   source_end = first_item
   for i in range(0,12000):
      if f.find("</table>",source_end) - source_end <= 100:
         break
      item_start = f.find("<tr><td>",source_end)+len("<tr><td>")
      item_end = f.find("</td>",item_start)
      buy_start = item_end + len("</td><td>")
      buy_end = f.find("</td>",buy_start)
      sell_start = buy_end + len("</td><td>")
      sell_end = f.find("</td>",sell_start)
      color1_start = sell_end + len("</td><td>")
      color1_end = f.find("</td>",color1_start)
      color2_start = color1_end + len("</td><td>")
      color2_end = f.find("</td>",color2_start)
      theme_start = color2_end + len("</td><td>")
      theme_end = f.find("</td>",theme_start)
      style_start = theme_end + len("</td><td>")
      style_end = f.find("</td>",style_start)
      source_start = style_end + len("</td><td>")
      source_end = f.find("</td>",source_start) 
      output.write(f[item_start:item_end]+";"+f[buy_start:buy_end]+";"+f[sell_start:sell_end]+";"+f[color1_start:color1_end]+";"+f[color2_start:color2_end]+";"+f[theme_start:theme_end]+";"+f[style_start:style_end]+";"+f[source_start:source_end]+"\n")
   output.close()
      

   
   