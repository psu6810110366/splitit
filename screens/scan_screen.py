from kivy.uix.screenmanager import Screen

class ScanScreen(Screen):
    def on_scan_press(self):
        """Callback: เปิดกล้อง"""
        print("Opening camera (Not implemented in setup phase)")
        
    def on_gallery_press(self):
        """Callback: เลือกรูปจาก Gallery"""
        print("Opening gallery (Not implemented in setup phase)")
        
    def on_ai_result(self, result):
        """Callback: จัดการผลลัพธ์จาก Gemini"""
        print(f"AI Result received: {result}")
        # นำทางไปหน้า New Split (self.manager.current = 'new_split_screen')
        pass
