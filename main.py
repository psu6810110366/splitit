from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window

# ตั้งค่าขนาดหน้าจอจำลอง (Mobile Size)
Window.size = (360, 640)

# สร้าง Class สำหรับแต่ละหน้าจอ (เดี๋ยวไปใส่รายละเอียดใน .kv)
class HomeScreen(Screen):
    pass

class CreateBillScreen(Screen):
    pass

class SummaryScreen(Screen):
    pass

# ตัวจัดการหน้าจอ (ScreenManager)
class WindowManager(ScreenManager):
    pass

class MainApp(App):
    def build(self):
        # โหลดไฟล์ UI
        return Builder.load_file('main.kv')

if __name__ == "__main__":
    MainApp().run()
