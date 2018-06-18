import time
import os.path
from pathlib import Path
import cv2
import sqlite3 as lite

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.uix.textinput import TextInput
from kivy.graphics import Line
from kivy.uix.progressbar import ProgressBar
from kivy.config import Config


class DataGen(FloatLayout):
    newid = NumericProperty()

    def __init__(self, **kwargs):
        super(DataGen, self).__init__(**kwargs)
        self.add_widget(Label(text='Enter The Id:', size_hint=(.05, .05), pos=(55, 30)))
        self.Id = TextInput(multiline=False, size_hint=(.2, .05), pos=(120, 30))
        self.add_widget(self.Id)
        self.progress = ProgressBar(max=100, size_hint=(.99, .05), pos=(5, 75))
        self.add_widget(self.progress)

        self.buttn = Button(text="Generate", size_hint=(.6, .05), pos=(260, 30))
        self.buttn.bind(on_press=self.gen)
        self.add_widget(self.buttn)
        with self.canvas:
            Line(points=[12, 20, 690, 20, 690, 75, 12, 75, 12, 20], width=2)
        self.sampleNum = 0
        # ----camera coding starts here----
        self.img1 = Image(source='images/1.jpg', size_hint=(.9, .80), pos=(40, 100))
        self.add_widget(self.img1)
        self.capture = cv2.VideoCapture(0)
        self.cascadePath = "xml/haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(self.cascadePath);
        Clock.schedule_interval(self.still, 1.0 / 1000)

    def gen(self, obj):
        con = lite.connect('User_Data.db')
        with con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(Id)FROM Users")
            id = ("%s" % cur.fetchone())
            self.newid = int(id)
            cur.execute("SELECT Name from Users where Name='" + self.Id.text + "' ")
            newname = ("%s" % cur.fetchone())

        self.file_path = Path("dataset/user." + str(self.newid) + ".1.jpg")
        if os.path.exists(self.file_path) or os.path.exists("dataset/user..1.jpg") or newname==self.Id.text:
            box = BoxLayout(orientation='vertical', padding=(10))
            box.add_widget(Label(text="""The User(Id) Already Exist.
             Re-Edit!!!"""))
            btn1 = Button(text="Retry", pos=(23, 23))
            box.add_widget(btn1)

            popup = Popup(title='Alert!', title_size=(20),
                          title_align='center', content=box,
                          size_hint=(None, None), size=(200, 200),
                          auto_dismiss=True)
            btn1.bind(on_press=popup.dismiss)
            popup.open()

        else:
            con = lite.connect('User_Data.db')
            with con:
                cur = con.cursor()
                cur.execute("INSERT INTO Users VALUES(" + str(self.newid) + ",'" + self.Id.text + "')")
            Clock.schedule_interval(self.update, 1.0 / 1000)
        self.progress.value = 0
        self.sampleNum = 0

    # function that works as a camera
    def still(self, obj):
        # display image from cam in opencv window
        ret, img = self.capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # convert it to texture
        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1

    # function that generates Images for data set
    def update(self, obj):
        # display image from cam in opencv window
        ret, img = self.capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # incrementing sample number
            self.sampleNum = self.sampleNum + 1
            self.progress.value += 1
            # saving the captured face in the dataset folder
            cv2.imwrite("dataSet/User." + str(self.newid) + '.' + str(self.sampleNum) + ".jpg", gray[y:y + h, x:x + w])
            print(self.progress.value)
            # convert it to texture
            buf1 = cv2.flip(img, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.img1.texture = texture1

            if self.sampleNum > 100:
                popup = Popup(title='Completed', title_size=(20),
                              title_align='center', content=Label(text='User Registered'),
                              size_hint=(None, None), size=(200, 200),
                              auto_dismiss=True)
                popup.open()
                popup.dismiss()
                self.capture.release()
                cv2.destroyAllWindows()


class MyApp(App):
    def build(self):
        Config.set('graphics', 'resizable', '0')
        Config.set('graphics', 'width', '700')
        Config.set('graphics', 'height', '600')
        self.icon = 'img/ico.png'
        self.title = 'DataSet Generator'
        Config.write()
        return DataGen()


if __name__ == '__main__':
    MyApp().run()