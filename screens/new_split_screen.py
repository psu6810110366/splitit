from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty

# Custom widget for the bill items
class EditableBillItem(MDBoxLayout):
    item_name = StringProperty()
    item_price = StringProperty()

class NewSplitScreen(Screen):
    def on_enter(self, *args):
        # We can trigger initial calculate here just in case
        self.recalculate_total()

    def populate_data_from_ai(self, result):
        """รับข้อมูลจาก AI (scan_screen.py) มาเติมลง UI"""
        # ตั้งชื่อบิล
        self.ids.bill_title.text = result.get("title", "บิลใหม่ (สแกน)")
        
        # ล้างรายการเก่าเพื่อใส่ของใหม่
        self.ids.items_list.clear_widgets()
        
        # ใส่รายการสินค้า
        items = result.get("items", [])
        for item in items:
            self.add_item_row(item.get("name", ""), str(item.get("price", 0.0)))
            
        # ใส่ค่า Service Charge หรือภาษี (ถ้ามี)
        tax = result.get("tax_or_service_charge", 0.0)
        if tax > 0:
            self.ids.tax_input.text = str(tax)
            
        self.recalculate_total()

    def add_item_row(self, name="", price=""):
        """เพิ่ม UI แถวใหม่ของรายการสินค้า"""
        row = EditableBillItem()
        row.ids.item_name_input.text = name
        row.ids.item_price_input.text = price
        
        # ผูกเหตุการณ์ตอนพิมพ์เปลี่ยนเพื่อคำนวณยอด
        row.ids.item_price_input.bind(text=self._on_price_changed)
        
        self.ids.items_list.add_widget(row)
        self.recalculate_total()

    def _on_price_changed(self, instance, value):
        self.recalculate_total()

    def on_delete_item_widget(self, widget):
        """ลบแถวสินค้านั้นๆ ลบทิ้งจากหน้าจอ"""
        self.ids.items_list.remove_widget(widget)
        self.recalculate_total()

    def on_add_item(self):
        """Callback: เพิ่มรายการสินค้า manual"""
        self.add_item_row("", "0")

    def recalculate_total(self, *args):
        """คำนวณ Subtotal และ Grand Total แบบ Realtime"""
        subtotal = 0.0
        
        # หาของทั้งหมดในลิสต์แล้วบวกราคา
        for child in self.ids.items_list.children:
            if isinstance(child, EditableBillItem):
                price_text = child.ids.item_price_input.text
                if price_text:
                    try:
                        subtotal += float(price_text)
                    except ValueError:
                        pass
                        
        # อ่านค่า ภาษี / Service Charge
        tax_text = self.ids.tax_input.text
        tax = 0.0
        if tax_text:
            try:
                tax = float(tax_text)
            except ValueError:
                pass
                
        grand_total = subtotal + tax
        
        # อัปเดต UI 
        if 'subtotal_label' in self.ids:
            self.ids.subtotal_label.text = f"฿{subtotal:,.2f}"
            self.ids.grand_total_label.text = f"฿{grand_total:,.2f}"

    def on_calculate(self):
        """Callback: เริ่มคำนวณบิล และนำทางไปหน้า Summary (ยังไม่ได้ทำหน้านี้ในตัวอย่างนี้)"""
        print("Saving bill and proceeding...")
        # เก็บข้อมูลงฐานข้อมูลที่นี่...
