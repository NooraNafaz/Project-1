from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from qr_reader import QrRedar
from bidi.algorithm import get_display
import arabic_reshaper
import mysql.connector as sql
import re

Window.clearcolor = (255, 255, 255, 0)  # Screen color changes
Window.size = (400, 630)  # Change the screen size


def letters_only(instance, value):
    pattern = re.compile(r"[^a-zA-Z\u0600-\u06FF\s]+")
    instance.text = pattern.sub("", value)


# الصنف الرئيسي الشاشة الرئيسية
class MyMainApp(App):
    def build(self):
        self.myredar = QrRedar(
            data_list=[
                "Laboratory No. 208",
                "Laboratory No. 212",
                "Laboratory No. 213",
                "Laboratory No. 215",
                "Teaching hall No. 201",
                "Teaching hall No. 202",
                "Teaching hall No. 203",
                "Teaching hall No. 204",
                "Teaching hall No. 205",
            ]
        )
        layout = FloatLayout()
        self.title = "تطبيق تسجيل حضور هيئة أعضاء التدريس"  # Home screen title
        # خلفية الشاشة
        background = Image(
            source="image/background.png", allow_stretch=True, keep_ratio=False
        )
        background.opacity = 0.5

        layout.add_widget(background)
        # اللوغو
        logo = Image(
            source="image/logo.png",
            size_hint=(None, None),
            size=(400, 400),
            pos_hint={"center_x": 0.5, "center_y": 0.8},
        )
        layout.add_widget(logo)
        # عنوان الواجهة
        title = Label(
            text="Al-Quds Open University",
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            font_size=20,
            color=(0, 0, 0, 1),
        )
        layout.add_widget(title)
        # عنصر ادخال الاسم
        reshap_text = arabic_reshaper.reshape("")
        self.name_input = TextInput(
            hint_text="Name of the faculty member",
            text=get_display(reshap_text),
            multiline=False,
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            size_hint=(0.6, 0.07),
            font_name=("arial"),
        )

        layout.add_widget(self.name_input)
        self.name_input.bind(text=letters_only)
        # عنصر ادخال الرقم
        self.number_input = TextInput(
            hint_text="Faculty member number",
            multiline=False,
            pos_hint={"center_x": 0.5, "center_y": 0.47},
            size_hint=(0.6, 0.07),
            input_filter="int",
            font_name=("arial"),
        )
        layout.add_widget(self.number_input)
        # عنصر الارسال
        send = Button(
            text="LOGIN",
            size_hint=(0.6, 0.07),
            pos_hint={"center_x": 0.5, "center_y": 0.37},
        )

        layout.add_widget(send)
        send.bind(on_press=self.check_function)
        return layout

    def show_message(self, message):
        popup = Popup(
            title="Message",
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 200),
        )
        popup.open()

    # دالة قراءة qr code
    def call_myredar_function(self):
        return self.myredar.redar()

    # دالة الاختيار
    def check_function(self, instance):
        text1 = self.name_input.text.strip()
        text2 = self.number_input.text.strip()

        if not text1 or not text2:
            self.show_message("You must enter the faculty\n member's name and number")
        elif text1 and text2:
            if not text2.isdigit() or len(text2) != 11 or not text2.startswith("01500"):
                self.show_message("You entered the wrong number")
            else:
                qr_valid = self.call_myredar_function()
                if qr_valid:
                    self.sub()

    # دالة الربط مع قاعدة البيانات
    def sub(self):
        uname = self.name_input.text
        unum = self.number_input.text
        rnum = self.myredar.mydata
        time = self.myredar.mytime
        try:
            con = sql.connect(
                host="localhost", user="root", password="", database="employees"
            )
            cur = con.cursor()
            query = (
                "Insert into users(username,usernumber,data,time) values(%s,%s,%s,%s)"
            )
            val = (uname, unum, rnum, time)
            cur.execute(query, val)
            con.commit()
            con.close()
        except sql.Error as e:
            print("error")


if __name__ == "__main__":
    MyMainApp().run()
