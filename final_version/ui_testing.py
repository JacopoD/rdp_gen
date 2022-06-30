from distutils.file_util import copy_file
import tkinter as tk
from collections import OrderedDict
from PIL import Image
from PIL import ImageTk
from functools import partial
from img_gen import generate_img
import time
import random
# import os

CONFIG = {
        "background_path": "./backgrounds/b1_gen.png",
        "output_path": None,
        "overlays_path": "./insects/",
        "merge_path": "./backgrounds/b1_gen_rest.png",
        "n_samples": 300,
        "overlay_n":None,
        "n_clusters": 1,
        "ellipse_ranges": None,
        "ellipse_ratios": None,
        "wse_background": None,
        "ellipses_wse": None,
        "plot": False,
        "verbose": False
    }


class app(tk.Frame):
   def __init__(self,master=None, **kwargs):
      self.current = None
      self.first = None
      self.done = False
      self.gifdict=OrderedDict()
      self.configdict = dict()
      # global CONFIG
      self.current_config = None
      for i in range(100):
         self.current_config = CONFIG
         self.current_config["n_samples"] = random.randint(50,1000)
         img, config, areas = generate_img(self.current_config.copy())
         img = img.resize((img.width//3,img.height//3),Image.ANTIALIAS)
         id = str(time.time())
         self.gifdict[id]=ImageTk.PhotoImage(img)

         config["areas"] = areas
         self.configdict[id] = config
      tk.Frame.__init__(self,master,**kwargs)
      self.label=tk.Label(self)
      self.label.pack()
      # self.button=tk.Button(self,text="next",command=self.next)
      # self.button.pack()
      self.button2=tk.Button(self,text="ok",command=partial(self.vote, True))
      self.button2.pack()
      self.button3=tk.Button(self,text="bad",command=partial(self.vote, False))
      self.button3.pack()
      self.next()


      self.file_object = open('/Users/jdv/Desktop/ui_test_1E_wseFREE.csv', 'a')

   def next(self):
      #Get first image in dict and add it to the end
      img,photo=self.gifdict.popitem(last=False)
      print("next")
      self.gifdict[img]=photo
      self.current = img
      if self.first is None:
         self.first = img
      else:
         if self.current == self.first:
            self.done = True
            self.file_object.close()
      #display the image we popped off the start of the dict.
      self.label.config(image=photo)

   def vote(self, ok):
      if not self.done:
         # print(self.current, ok)
         s = "{}~{}~{}~{}~{}~{}~{}\n".format(ok,self.current, self.configdict[self.current]["n_samples"], self.configdict[self.current]["n_clusters"], self.configdict[self.current]["areas"] ,self.configdict[self.current]["wse_background"], self.configdict[self.current]["ellipses_wse"])
         s = s.replace("array(","")
         s = s.replace(")","")
         s = s.replace(",","")
         s = s.replace("~",",")

         s = s.replace("[","")
         s = s.replace("]","")
         print(s)
         self.file_object.write(s)
         self.next()

if __name__ == "__main__":
   A=tk.Tk()
   B=app(master=A,width=100,height=100)
   B.pack()
   A.mainloop()