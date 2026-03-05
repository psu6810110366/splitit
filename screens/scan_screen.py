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
        Callback 2: Gallery Picker — ให้ผู้ใช้เลือกภาพใบเสร็จ
        """
        print("[Scan] Action: Open Gallery")
        
        import platform
        import threading
        
        # ใช้ Tkinter/osascript สำหรับ Desktop (Windows/Mac) เพื่อหลีกเลี่ยง Kivy Freeze
        if platform.system() == 'Darwin':
            def _open_mac():
                import subprocess
                script = '''
                tell application "System Events"
                    activate
                    set theFile to choose file with prompt "เลือกรูปภาพใบเสร็จ:" of type {"public.image"}
                    POSIX path of theFile
                end tell
                '''
                try:
                    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        file_path = result.stdout.strip()
                        Clock.schedule_once(lambda dt: self.handle_gallery_selection([file_path]), 0)
                except Exception as e:
                    print(f"[Scan] Mac filechooser error: {e}")
            threading.Thread(target=_open_mac, daemon=True).start()
            return
            
        elif platform.system() == 'Windows':
            def _open_tk():
                try:
                    import tkinter as tk
                    from tkinter import filedialog
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                        
                    file_path = filedialog.askopenfilename(
                        title="เลือกรูปภาพใบเสร็จ",
                        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.webp")]
                    )
                    root.destroy()
                    
                    if file_path:
                        Clock.schedule_once(lambda dt: self.handle_gallery_selection([file_path]), 0)
                except Exception as e:
                    print(f"[Scan] Tkinter error: {e}")
                    
            threading.Thread(target=_open_tk, daemon=True).start()
            return

        # ลอง plyer สำหรับ Mobile (Android/iOS)
        if filechooser is not None:
            try:
                selection = filechooser.open_file(
                    title="เลือกรูปใบเสร็จเพื่อแสกน",
                    filters=[("Images", "*.jpg", "*.jpeg", "*.png")],
                    on_selection=self.handle_gallery_selection
                )
                if selection and isinstance(selection, list):
                    self.handle_gallery_selection(selection)
                return
            except Exception as e:
                print(f"[Scan] plyer filechooser failed: {e}")
                
        from kivymd.toast import toast
        toast("ไม่สามารถเปิดแกลเลอรี่ได้บนอุปกรณ์นี้")
        print("[Scan] No image source available.")

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
            
            # แสดง MDSnackbar แจ้ง user 
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            MDSnackbar(
                MDSnackbarText(
                    text="❌ ไม่สามารถอ่านบิลได้ ลองใหม่อีกครั้ง",
                ),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()

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
