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
        """เปิดกล้องเมื่อเข้าสู่หน้านี้"""
        try:
            if 'camera' in self.ids:
                self.ids.camera.play = True
        except Exception as e:
            print(f"[ScanScreen] Camera not available: {e}")

    def on_leave(self, *args):
        """ปิดกล้องเมื่อออกจากหน้านี้เพื่อประหยัดทรัพยากร"""
        try:
            if 'camera' in self.ids:
                self.ids.camera.play = False
        except Exception:
            pass

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def go_back(self):
        self.manager.current = 'dashboard'

    def go_to_friends(self):
        self.manager.current = 'friends_screen'

    def on_scan_press(self):
        """
        Callback 1: Camera Capture — ถ่ายรูปจากกล้องและส่งไป AI
        ถ้ากล้องไม่พร้อม (desktop) จะ fallback ไปเปิด gallery
        """
        print("[Scan] Action: Capture Photo")
        try:
            camera = self.ids.camera
            image_path = "temp_receipt.jpg"
            camera.export_to_png(image_path)
            self.start_ai_analysis(image_path)
        except Exception as e:
            print(f"[Scan] Camera capture failed: {e} — falling back to gallery")
            self.on_gallery_press()

    def on_gallery_press(self):
        """
        Callback 2: Gallery Picker — ใช้ plyer บน mobile, fallback บน desktop
        """
        print("[Scan] Action: Open Gallery")

        # ลอง plyer ก่อน (ใช้ได้บน Android/iOS)
        if filechooser is not None:
            try:
                filechooser.open_file(
                    on_selection=self.handle_gallery_selection,
                    filters=["*.jpg", "*.jpeg", "*.png"],
                )
                return
            except Exception as e:
                print(f"[Scan] plyer filechooser failed: {e}")

        # Desktop fallback: หารูปทดสอบ
        test_paths = ["temp_receipt.jpg", "test_receipt.jpg", "test_receipt.png"]
        for path in test_paths:
            if os.path.exists(path):
                print(f"[Scan] Using test image: {path}")
                self.start_ai_analysis(path)
                return

        # ไม่มีรูป → ไปหน้า manual entry
        print("[Scan] No image source available, opening manual entry.")
        self.manager.current = 'new_split_screen'

    def handle_gallery_selection(self, selection):
        if selection:
            image_path = selection[0]
            self.start_ai_analysis(image_path)

    def on_manual_press(self):
        """ข้าม AI แล้วไปกรอกมือเลย"""
        print("[Scan] Action: Manual Entry")
        self.manager.current = 'new_split_screen'

    def start_ai_analysis(self, image_path):
        """
        แสดง Loading overlay และโยนงานให้ background thread
        เพื่อไม่ให้ UI ค้าง
        """
        self.show_loading(True)

        # ปิดกล้องชั่วคราวระหว่างรอ
        try:
            if 'camera' in self.ids:
                self.ids.camera.play = False
        except Exception:
            pass

        # สร้าง daemon thread ให้ AI ทำงานเบื้องหลัง
        threading.Thread(
            target=self._run_ai_task,
            args=(image_path,),
            daemon=True
        ).start()

        # เริ่ม animation เปลี่ยนข้อความรอ
        self.loading_step = 0
        self.loading_event = Clock.schedule_interval(
            self._update_loading_text, 2.0
        )

    def _update_loading_text(self, dt):
        texts = [
            "กำลังส่งรูปภาพ...",
            "กำลังให้ AI อ่านบิล...",
            "กำลังแยกราคาสินค้า...",
            "เกือบเสร็จแล้ว...",
        ]
        self.loading_step = (self.loading_step + 1) % len(texts)
        if 'loading_text' in self.ids:
            self.ids.loading_text.text = texts[self.loading_step]

    def _run_ai_task(self, image_path):
        """Background thread — เรียก AI แล้ว schedule callback กลับ main thread"""
        result = scan_receipt(image_path)
        Clock.schedule_once(lambda dt: self.on_ai_result(result))

    def on_ai_result(self, result):
        """
        Callback หลัง AI เสร็จ — ทำงานบน Main Thread เท่านั้น
        """
        if hasattr(self, 'loading_event'):
            self.loading_event.cancel()

        self.show_loading(False)
        print(f"[Scan] AI Result: {result}")

        if "error" in result:
            print(f"[Scan] AI Failed: {result['error']}")
            # TODO: แสดง MDSnackbar แจ้ง user (เพิ่มใน phase ถัดไป)
            # เปิดกล้องให้ลองใหม่
            try:
                if 'camera' in self.ids:
                    self.ids.camera.play = True
            except Exception:
                pass
            return

        # ส่งข้อมูลข้ามหน้าไปยัง NewSplitScreen
        new_split = self.manager.get_screen('new_split_screen')
        if hasattr(new_split, 'populate_data_from_ai'):
            new_split.populate_data_from_ai(result)

        self.manager.current = 'new_split_screen'

    def show_loading(self, show: bool):
        if 'loading_overlay' not in self.ids:
            return
        overlay = self.ids.loading_overlay
        spinner = self.ids.spinner
        if show:
            overlay.opacity = 1
            spinner.active = True
            if 'loading_text' in self.ids:
                self.ids.loading_text.text = "กำลังส่งรูปภาพ..."
        else:
            overlay.opacity = 0
            spinner.active = False
