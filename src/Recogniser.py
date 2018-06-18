import cv2
import sqlite3 as lite

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.graphics import Line
from kivy.config import Config

class RecogClass(FloatLayout):
    name = StringProperty()
    def __init__(self, **kwargs):
        super(RecogClass, self).__init__(**kwargs)
        self.add_widget(Label(text="UserName::",size_hint=(.1,.1),pos=(50, 15)))
        self.lbl = Label(text=self.name,size_hint=(.1, .1),pos=(150, 15))
        self.add_widget(self.lbl)
        self.btn = Button(text="Recognise",size_hint=(.9, .1),pos=(25, 70))
        self.btn.bind(on_press=self.auth)
        self.add_widget(self.btn)
        with self.canvas:
            Line(points=[20, 20, 480, 20, 480, 60, 20, 60, 20, 20], width=2)
        #----camera coding starts here----
        self.img1 = Image(source='images/1.jpg',size_hint=(.9,.75),pos=(25, 120))
        self.add_widget(self.img1)
        self.capture = cv2.VideoCapture(0)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read('recogniser/trainner.yml')
        self.cascadePath = "xml/haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(self.cascadePath);
        self.fontface = cv2.FONT_HERSHEY_SIMPLEX
        self.fontscale = 1
        self.fontcolor = (255, 255, 255)
        self.con = lite.connect('User_Data.db')

        Clock.schedule_interval(self.update, 1.0 / 1000)


    # Recogniser function that recognised data
    def update(self, dt):

        # display image from cam in opencv window
        ret, im = self.capture.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            # cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
            Id, conf = self.recognizer.predict(gray[y:y + h, x:x + w])
            if (conf < 100):
                with self.con:
                    cur = self.con.cursor()
                    cur.execute("SELECT Name from Users where Id='" + str(Id) + "'")
                    self.name = ("%s" % cur.fetchone())

            else:
                self.name = "Unknown"
                print("Denied")
            # Enable the nex line to enable live recognising
            # cv2.putText(im, self.name, (x, y + h), self.fontface, self.fontscale, self.fontcolor)
        print(self.name)
        # convert it to texture
        buf1 = cv2.flip(im, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(im.shape[1], im.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1

    # function that reflects the recognised data
    def auth(self,instance):
        self.lbl.text = self.name



class Recog(App):
    def build(self):
        Config.set('graphics', 'resizable', '0')
        Config.set('graphics', 'width', '500')
        Config.set('graphics', 'height', '500')
        self.icon = 'img/ico.png'
        self.title = 'Recogniser'
        Config.write()
        return RecogClass()


if __name__ == '__main__':
    Recog().run()
