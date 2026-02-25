from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import threading
import time
import os

# Note: In a real app we would use plyer.filechooser for mobile, but for desktop testing
# we can use kivy's built-in file chooser or plyer depending on OS.
try:
    from plyer import filechooser
except ImportError:
    filechooser = None

from core.ai_service import scan_receipt

class ScanScreen(Screen):
    
    def on_enter(self, *args):
        # เปิดกล้องเมื่อเข้าสู่หน้านี้
        if 'camera' in self.ids:
            self.ids.camera.play = True
            
    def on_leave(self, *args):
        # ปิดกล้องเมื่อออกจากหน้านี้เพื่อประหยัดแบต
        if 'camera' in self.ids:
            self.ids.camera.play = False

    def go_back(self):
        self.manager.current = 'dashboard_screen'

    def on_scan_press(self):
        """
        Callback 1: Camera Capture
        """
        print("Action: Capture Photo")
        camera = self.ids.camera
        
        # ถ่ายรูปและเซฟชั่วคราว
        image_path = "temp_receipt.jpg"
        camera.export_to_png(image_path) # export_to_png exports based on extension if supported, but png is fine
        
        # เริ่มกระบวนการวิเคราะห์
        self.start_ai_analysis(image_path)

    def on_gallery_press(self):
        """
        Callback 2: Gallery Picker
        """
        print("Action: Open Gallery")
        if filechooser:
            filechooser.open_file(on_selection=self.handle_gallery_selection)
        else:
            print("Plyer not installed. Cannot open gallery on this device.")
            # For testing without plyer, hardcode a test image if exists
            if os.path.exists("test_receipt.jpg"):
                self.start_ai_analysis("test_receipt.jpg")
                
    def handle_gallery_selection(self, selection):
        if selection:
            image_path = selection[0]
            self.start_ai_analysis(image_path)

    def on_manual_press(self):
        """
        Skip AI and go straight to manual entry
        """
        print("Action: Manual Entry")
        self.manager.current = 'new_split_screen'

    def start_ai_analysis(self, image_path):
        """
        แสดง Loading overlay และโยนงานให้ Thread รองทำ เพื่อไม่ให้ UI ค้าง
        """
        self.show_loading(True)
        
        # ปิดกล้องชั่วคราวระหว่างรอ
        if 'camera' in self.ids:
            self.ids.camera.play = False
            
        # สร้าง Thread ให้ AI คิดงานหลังบ้าน
        threading.Thread(target=self._run_ai_task, args=(image_path,), daemon=True).start()
        
        # เริ่มแอนิเมชันเปลี่ยนข้อความรอ
        self.loading_step = 0
        self.loading_event = Clock.schedule_interval(self._update_loading_text, 2.0)

    def _update_loading_text(self, dt):
        texts = [
            "กำลังอัปโหลดรูปภาพ...",
            "กำลังให้ AI อ่านบิล...",
            "กำลังแยกราคาสินค้า...",
            "กำลังคำนวณภาษี...",
            "เกือบเสร็จแล้ว..."
        ]
        self.loading_step = (self.loading_step + 1) % len(texts)
        self.ids.loading_text.text = texts[self.loading_step]

    def _run_ai_task(self, image_path):
        """ท่วงทำอยู่เบื้องหลัง (Background Thread)"""
        # เรียก AI ฟังก์ชันจาก core
        result = scan_receipt(image_path)
        
        # เมื่อเสร็จแล้ว ต้องกลับมาอัปเดต UI บน Main Thread เท่านั้น
        Clock.schedule_once(lambda dt: self.on_ai_result(result))

    def on_ai_result(self, result):
        """
        Callback 3: AI Result Handler (Runs on Main Thread)
        """
        # หยุดข้อความโหลด
        if hasattr(self, 'loading_event'):
            self.loading_event.cancel()
            
        self.show_loading(False)
        print(f"AI Result: {result}")
        
        if "error" in result:
            print(f"Failed: {result['error']}")
            # ในแอปจริงควรมี Popup หรือ Snackbar แจ้งเตือนตรงนี้
            # เปิดกล้องให้ลองใหม่
            if 'camera' in self.ids:
                self.ids.camera.play = True
            return

        # ถ้าสำเร็จ ส่งข้อมูลข้ามไปหน้า New Split Screen
        # (เดี๋ยวเราจะดึง instance ของ new_split_screen ออกมาเตรียมข้อมูล)
        new_split = self.manager.get_screen('new_split_screen')
        
        # FIXME: ในอนาคต (Phase 3) จะต้องมีฟังก์ชันรับข้อมูลใน NewSplitScreen
        # new_split.populate_data_from_ai(result)
        
        # นำทางไปหน้าถัดไป
        self.manager.current = 'new_split_screen'

    def show_loading(self, show: bool):
        overlay = self.ids.loading_overlay
        spinner = self.ids.spinner
        if show:
            overlay.opacity = 1
            spinner.active = True
            self.ids.loading_text.text = "กำลังส่งรูปภาพ..."
        else:
            overlay.opacity = 0
            spinner.active = False
