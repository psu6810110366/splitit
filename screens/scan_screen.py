from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import threading
import os

try:
    from plyer import filechooser
except ImportError:
    filechooser = None

from core.ai_service import scan_receipt

class ScanScreen(Screen):
    
    def on_enter(self, *args):
        pass  # Camera widget removed; handled via gallery/manual

    def on_leave(self, *args):
        pass

    def go_back(self):
        self.manager.current = 'dashboard' # Fixed from 'dashboard_screen'

    def on_scan_press(self):
        """
        Callback 1: Camera Capture (delegates to gallery on desktop)
        """
        print("Action: Capture Photo")
        self.on_gallery_press()

    def on_gallery_press(self):
        """
        Callback 2: Gallery Picker — uses plyer on mobile, fallback on desktop
        """
        print("Action: Open Gallery")

        # Try plyer first (works on Android/iOS)
        if filechooser is not None:
            try:
                filechooser.open_file(
                    on_selection=self.handle_gallery_selection,
                    filters=["*.jpg", "*.jpeg", "*.png"],
                )
                return
            except Exception as e:
                print(f"plyer filechooser failed: {e}")

        # Desktop fallback: look for a test image, otherwise skip to manual
        test_paths = ["test_receipt.jpg", "test_receipt.png"]
        for path in test_paths:
            if os.path.exists(path):
                print(f"Using test image: {path}")
                self.start_ai_analysis(path)
                return

        # Nothing found — just go to manual entry
        print("No image source available, opening manual entry.")
        self.manager.current = 'new_split_screen'
                
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
            return

        # ถ้าสำเร็จ ส่งข้อมูลข้ามไปหน้า New Split Screen
        new_split = self.manager.get_screen('new_split_screen')
        
        # Phase A: ส่งผลลัพธ์จาก AI ไปยัง New Split Screen
        if hasattr(new_split, 'populate_data_from_ai'):
            new_split.populate_data_from_ai(result)
        
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
