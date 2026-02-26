from kivy.uix.screenmanager import Screen

class NewSplitScreen(Screen):
    def on_add_item(self):
        """Callback: เพิ่มรายการสินค้า manual"""
        print("Add item manually")
        
    def on_delete_item(self, item_id):
        """Callback: ลบรายการ"""
        print(f"Deleting item: {item_id}")
        
    def on_add_friend(self):
        """Callback: เปิด Modal เลือกเพื่อน"""
        print("Show friend picker modal")
        
    def on_split_mode_toggle(self, mode):
        """Callback: สลับระหว่าง หารเท่า (equal) หรือ กำหนดเอง (custom)"""
        print(f"Split mode changed to: {mode}")
        
    def on_calculate(self):
        """Callback: เริ่มคำนวณบิล และนำทางไปหน้า Summary"""
        print("Calculating... advancing to Summary Screen")
        # self.manager.current = 'summary_screen'
