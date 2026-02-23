from kivy.app import App
from kivy.uix.label import Label


class MainApp(App):
    def build(self):
        # โหลดหน้าจอแรกขึ้นมาแสดงผล
        return Label(text="Hello Kivy! Setup Successful.")


if __name__ == "__main__":
    MainApp().run()
