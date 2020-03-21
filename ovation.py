#!/usr/bin/env python3
import subprocess
import os
from tkinter import *
from PIL import ImageTk, Image
import time
import re

last_time = time.time()
file_substr_regex = r'([\w.-]+?)(\d*).png$'

def convert_pdf(src, dest):
    p = subprocess.Popen(["pdftoppm", src, dest, "-png", "-rx", "100", "-ry", "100"])
    while True:
        if p.poll() is None:
            yield len([i for i in os.listdir(os.dirname(dest)) if i.startswith(dest+'-')])
        else:
            return None

class ModalWindow:
    def __init__(self, parent):
        w, h = parent.w, parent.h
        self.parent = parent
        self.win = Toplevel()
        self.defaultColor = self.win.cget('bg')
        self.label1 = Label(self.win, pady=20, width=64, font=('Helvetica', 24))
        self.label2 = Label(self.win, pady=20, width=64, font=('Helvetica', 24), bg="red")
        self.label3 = Label(self.win, pady=20, width=64, font=('Helvetica', 24))
        self.label4 = Label(self.win, pady=20, width=64, font=('Helvetica', 24))
        self.label1.pack()
        self.label2.pack()
        self.label3.pack()
        self.label4.pack()
        # take a guess at screen center
        self.win.geometry("+%d+%d" % (w/2 - 500, h/2 - 150))
        self.win.update()
        size = (self.win.winfo_width(), self.win.winfo_height())
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        self.win.geometry("+%d+%d" % (x, y))
        self.win.title("Select song to load")
        self.index = 0
        self.displayIndex = 0
        self.options = ['Import new song'] + os.listdir('data')
        self.update()
        self.win.bind("<Key>", self.onKeyPress)
        self.win.bind("<Return>", self.onEnterPress)

    def update(self):
        self.label1['text'] = self.options[self.index]
        self.label2['text'] = self.options[self.index+1] if len(self.options) > self.index+1 else ""
        self.label3['text'] = self.options[self.index+2] if len(self.options) > self.index+2 else ""
        self.label4['text'] = self.options[self.index+3] if len(self.options) > self.index+3 else ""
        self.label1['bg'] = 'white' if self.displayIndex==0 else self.defaultColor
        self.label2['bg'] = 'white' if self.displayIndex==1 else self.defaultColor
        self.label3['bg'] = 'white' if self.displayIndex==2 else self.defaultColor
        self.label4['bg'] = 'white' if self.displayIndex==3 else self.defaultColor

    def onKeyPress(self, event):
        global last_time
        ctime = time.time()
        if ctime - last_time > 0.25:
            if event.char in '123456qwertyasdfgzxcvb':
                last_time = ctime
                if self.index > 0 and self.displayIndex==0:
                    self.index -= 1
                elif self.displayIndex > 0:
                    self.displayIndex-=1
            elif event.char in '890-=uiop[]hjkl;\'nm,./ ':
                last_time = ctime
                if self.index < len(self.options) - 4 and self.displayIndex==3:
                    self.index+=1
                elif self.displayIndex < 3:
                    self.displayIndex += 1
            self.update()

    def onEnterPress(self, event=None):
        if self.index+self.displayIndex > 0:
            self.win.destroy()
            folder = 'data/'+self.options[self.index+self.displayIndex]
            img = os.listdir(folder)[0]
            print(img)
            self.parent.loadImageSet(folder+'/'+img)

class MStandWindow:
    def __init__(self):
        self.tk = Tk()
        self.tk.attributes("-fullscreen", True)
        self.w, self.h = self.tk.winfo_screenwidth(), self.tk.winfo_screenheight()
        #self.frame = Frame(self.tk)
        #self.frame.pack()
        self.canvas = Canvas(self.tk, width=self.w, height=self.h)
        self.canvas.pack()

        self.tk.bind("<Key>", self.onKeyPress)
        self.tk.bind("<Return>", self.onReturnPress)
        self.image_cache = {}
        self.images = []
        self.index = 0
        #self.loadImageSet("data/moonlight-a4.png/moonlight-a4.png-01.png")
        self.tk.update()
        mwin = ModalWindow(self)

    def onKeyPress(self, event):
        global last_time
        ctime = time.time()
        if ctime - last_time > 1:
            if event.char in '123456qwertyasdfgzxcvb':
                last_time = ctime
                if self.index > 0:
                    self.index -= 1
                    self.setImages(self.images[self.index], self.images[self.index+1])
            elif event.char in '890-=uiop[]hjkl;\'nm,./ ':
                last_time = ctime
                if self.index < len(self.images) - 2:
                    self.index += 1
                    self.setImages(self.images[self.index], self.images[self.index+1])

    def onReturnPress(self, event=None):
        print("launched modal")
        mwin = ModalWindow(self)

    def setImages(self, img1, img2=None):
        if img1 in self.image_cache:
            image1 = self.image_cache[img1]['image']
        else:
            image1 = Image.open(img1)
            i1w, i1h = image1.size
            if img2 is not None:
                ratio1 = min((self.w/2)/i1w, self.h/i1h)
            else:
                ratio1 = min(self.w/i1w, self.h/i1h)
            i1w = int(i1w*ratio1)
            i1h = int(i1h*ratio1)
            image1 = image1.resize((i1w, i1h), Image.ANTIALIAS)
            self.image_cache[img1] = {'image': image1}
        tkImage1 = ImageTk.PhotoImage(image1)
        if img2 is not None:
            isprite1 = self.canvas.create_image(self.w/4, self.h/2, image=tkImage1)
        else:
            isprite1 = self.canvas.create_image(self.w/2, self.h/2, image=tkImage1)
        self.canvas.image1 = tkImage1
        if img2 is not None:
            if img2 in self.image_cache:
                image2 = self.image_cache[img2]['image']
            else:
                image2 = Image.open(img2)
                i2w, i2h = image2.size
                ratio2 = min(self.w/i2w, self.h/i2h)
                i2w = int(i2w*ratio2)
                i2h = int(i2h*ratio2)
                image2 = image2.resize((i2w, i2h), Image.ANTIALIAS)
                self.image_cache[img2] = {'image':image2}
            tkImage2 = ImageTk.PhotoImage(image2)
            isprite2 = self.canvas.create_image(self.w*3/4, self.h/2, image=tkImage2)
            self.canvas.image2 = tkImage2
        self.tk.update_idletasks()
        self.tk.update()

    def loadImageSet(self, first):
        self.image_cache = {}
        folder, first_filename = os.path.split(first)
        res = re.match(file_substr_regex, first_filename)
        if res:
            substr = res.group(1)
            self.images = [folder+'/'+i for i in os.listdir(folder) if i.startswith(substr)]
        else:
            self.images = [first]
        self.images.sort()
        self.setImages(self.images[0], self.images[1] if len(self.images) > 1 else None)
        self.index = 0

if __name__=="__main__":
    w = MStandWindow()
    w.tk.mainloop()
