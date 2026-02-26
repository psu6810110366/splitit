from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty

class DashboardScreen(Screen):
    total_owed = NumericProperty(15.00) # Dummy start data (You owe)
    total_owe_me = NumericProperty(120.00) # Dummy start data (Owed to you)
    
    def on_enter(self, *args):
        """Callback เมื่อเข้ามาสู่หน้านี้ (Refresh data when entered)"""
        # ในอนาคตดึงข้อมูลจาก core.models
        pass
        
    def go_to_new_split(self):
        """นำทางไปลุ่ม (Navigate to New Split screen)"""
        print("Navigate to Scan or New Split screen...")
        # self.manager.current = 'scan_screen'
