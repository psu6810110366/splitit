from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
# from components.add_friend_dialog import AddFriendDialog    # noqa: F401
from components.add_item_dialog import AddItemDialog        # noqa: F401
from components.assign_item_dialog import AssignItemDialog  # noqa: F401
from components.item_row import ItemRow
from components.person_row import PersonRow


class NewSplitScreen(Screen):
    split_mode = StringProperty('equal')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items = []
        self._people = []
        self._custom_amounts = {}

    def on_enter(self, *args):
        """รีเซ็ตฟอร์มทุกครั้งที่เข้าหน้านี้ใหม่ (ยกเว้นกรณีส่งมาจาก AI)"""
        if getattr(self, '_is_ai_handoff', False):
            self._is_ai_handoff = False
            return

        self._items = []   # [{'name': str, 'price': float, 'assigned_to': [str]}]
        self._people = []  # [str] (ไม่รวม "Me")
        self._custom_amounts = {} # {name: str_amount}
        
        self.split_mode = 'equal'
        self.ids.bill_name_input.text = ''
        self.ids.total_amount_label.text = '0.00'
        self.ids.btn_split_equal.md_bg_color = [0.314, 0.784, 0.471, 1]
        self.ids.btn_split_custom.md_bg_color = [0.953, 0.961, 0.973, 1]
        
        self._refresh_items_list()
        self._refresh_people_list()

    def _all_people(self):
        """รายชื่อทุกคน รวม Me เสมอ"""
        return ['Me'] + list(self._people)

    def go_back(self):
        self.manager.current = 'dashboard'

    # ── AI Handoff ────────────────────────────────────────────────────────────

    def populate_data_from_ai(self, result):
        """
        รับข้อมูลจาก AI (scan_screen) แล้วเติมลงฟอร์ม
        result format: {'title': str, 'items': [{'name': str, 'price': float}]}
        """
        # ตั้งค่า flag ป้องกันการล้างข้อมูลใน on_enter
        self._is_ai_handoff = True
        
        # รีเซ็ตก่อนเติมข้อมูล
        self._items = []
        self._people = []

        title = result.get('title', 'Scanned Bill')
        self.ids.bill_name_input.text = str(title)

        for item in result.get('items', []):
            name = item.get('name', '')
            price = float(item.get('price', 0.0))
            if name:
                self._items.append({'name': name, 'price': price, 'assigned_to': []})

        total_amount = result.get('total', 0.0)
        self.ids.total_amount_label.text = f"{total_amount:.2f}"

        self._refresh_items_list()
        self._refresh_people_list()
        print(f"[NewSplit] Populated {len(self._items)} items from AI")

    # ── Items ─────────────────────────────────────────────────────────────────

    def on_add_item(self):
        dialog = AddItemDialog()
        dialog.callback = self._on_item_added
        dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        self.add_widget(dialog)

    def _on_item_added(self, name, price):
        # default: ทุกคนร่วมหาร (assigned_to ว่าง = ทุกคน)
        self._items.append({'name': name, 'price': price, 'assigned_to': []})
        self._refresh_items_list()

    def _on_item_deleted(self, index):
        if 0 <= index < len(self._items):
            del self._items[index]
            self._refresh_items_list()

    def _on_assign_item(self, index):
        """เปิด dialog เลือกว่าใครหารรายการนี้"""
        if index < 0 or index >= len(self._items):
            return
        item = self._items[index]
        current_assigned = item['assigned_to'] or list(self._all_people())

        dialog = AssignItemDialog()
        dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        self.add_widget(dialog)
        dialog.setup(item['name'], self._all_people(), current_assigned)

        def on_confirmed(selected, idx=index):
            self._items[idx]['assigned_to'] = selected
            self._refresh_items_list()

        dialog.callback = on_confirmed

    def _refresh_items_list(self):
        items_list = self.ids.items_list
        items_list.clear_widgets()
        total = 0.0
        for i, item in enumerate(self._items):
            row = ItemRow()
            row.item_name = item['name']
            row.price = item['price']
            assigned = item.get('assigned_to') or []
            row.assigned_to = assigned
            row.delete_cb = (lambda idx=i: self._on_item_deleted(idx))
            row.assign_cb = (lambda idx=i: self._on_assign_item(idx))
            items_list.add_widget(row)
            total += item['price']
        if self._items:
            self.ids.total_amount_label.text = '{:.2f}'.format(total)
        self.ids.items_count_label.text = '{} Items'.format(len(self._items))

    # ── People ────────────────────────────────────────────────────────────────

    def on_add_friend(self):
        from components.select_friend_dialog import SelectFriendDialog
        # ส่งรายชื่อที่เลือกอยู่แล้วไปให้ Dialog ติ๊กถูกไว้ก่อน
        dialog = SelectFriendDialog(pre_selected=list(self._people))
        dialog.callback = self._on_friends_selected
        dialog.open()

    def _on_friends_selected(self, names):
        """รับรายชื่อเพื่อนจากการเลือกใน Dialog (รวมทั้งเพิ่มและลด)"""
        old_people = set(self._people)
        new_people = set(names)
        
        # หาคนที่ถูกลบออก
        removed_people = old_people - new_people
        for name in removed_people:
            for item in self._items:
                if name in item.get('assigned_to', []):
                    item['assigned_to'].remove(name)
        
        self._people = list(names)
        self._refresh_people_list()
        self._refresh_items_list()

    def _on_person_removed(self, index):
        if 0 <= index < len(self._people):
            name = self._people[index]
            del self._people[index]
            # ถอดชื่อออกจาก assigned_to ของทุก item ด้วย
            for item in self._items:
                if name in item.get('assigned_to', []):
                    item['assigned_to'].remove(name)
            self._refresh_people_list()
            self._refresh_items_list()

    def on_total_amount_change(self, text):
        """เมื่อมีการกรอกยอดรวมบิลใหม่ให้รีเฟรชยอดหารรายคน"""
        self._refresh_people_list()
        self._update_remaining_balance()

    def _refresh_people_list(self):
        people_list = self.ids.people_list
        people_list.clear_widgets()
        
        # คำนวณยอดหารต่อคน (กรณีโหมด Equal)
        try:
            total = float(self.ids.total_amount_label.text.replace(',', ''))
        except:
            total = 0.0
            
        all_names = self._all_people()
        count = len(all_names)
        equal_share = total / count if count > 0 else 0.0
        
        for i, name in enumerate(all_names):
            row = PersonRow()
            row.display_name = name
            row.is_custom_mode = (self.split_mode == 'custom')
            
            # ตั้งค่าราคาเริ่มต้น
            if self.split_mode == 'custom':
                row.amount = self._custom_amounts.get(name, '0.00')
            else:
                row.amount = f"{equal_share:.2f}"
            
            # Callback เมื่อมีการพิมพ์ตัวเลข (เฉพาะ Custom mode)
            row.on_amount_change = (lambda val, n=name: self._on_amount_changed(n, val))
            
            # ปุ่มลบ (ห้ามลบ "Me")
            if name == "Me":
                row.ids.close_btn.opacity = 0
                row.ids.close_btn.disabled = True
            else:
                friend_idx = i - 1 # index ใน self._people
                row.remove_cb = (lambda idx=friend_idx: self._on_person_removed(idx))
            
            people_list.add_widget(row)
            
        self.ids.people_count_label.text = '{} people'.format(count)

    def _on_amount_changed(self, name, value):
        """บันทึกยอดเงินที่กรอกเอง"""
        if self.split_mode == 'custom':
            self._custom_amounts[name] = value
            self._update_remaining_balance()

    def _update_remaining_balance(self):
        """คำนวณยอดเงินที่เหลือ (ส่วนต่างระหว่าง Total กับผลรวมที่กรอก)"""
        if self.split_mode != 'custom':
            return
            
        try:
            total = float(self.ids.total_amount_label.text.replace(',', ''))
        except:
            total = 0.0
            
        sum_custom = 0.0
        for val in self._custom_amounts.values():
            try:
                sum_custom += float(val.replace(',', ''))
            except:
                pass
        
        remaining = total - sum_custom
        self.ids.remaining_balance_label.text = f"฿{remaining:,.2f}"
        
        # เปลี่ยนสีถ้าลงตัว
        if abs(remaining) < 0.01:
            self.ids.remaining_balance_label.text_color = [0.196, 0.659, 0.322, 1] # Green
        else:
            self.ids.remaining_balance_label.text_color = [0.937, 0.267, 0.267, 1] # Red

    # ── Split toggle ──────────────────────────────────────────────────────────

    def on_split_mode_toggle(self, mode):
        self.split_mode = mode
        green = [0.314, 0.784, 0.471, 1]
        grey = [0.953, 0.961, 0.973, 1]
        if mode == 'equal':
            self.ids.btn_split_equal.md_bg_color = green
            self.ids.btn_split_custom.md_bg_color = grey
        else:
            self.ids.btn_split_equal.md_bg_color = grey
            self.ids.btn_split_custom.md_bg_color = green
        
        # รีเฟรชรายการเพื่อนเพื่อเปิด/ปิดช่องกรอกเงิน
        self._refresh_people_list()

    # ── Calculate ─────────────────────────────────────────────────────────────

    def on_calculate(self):
        from kivymd.toast import toast

        bill_name = self.ids.bill_name_input.text.strip() or 'Untitled Bill'
        try:
            total = float(self.ids.total_amount_label.text.replace(',', ''))
        except ValueError:
            total = 0.0

        if total <= 0 and self._items:
            total = sum(item['price'] for item in self._items)

        # ── Validation ────────────────────────────────────────────────────────
        if total <= 0:
            if not self._items:
                toast("Please add items or enter a total amount")
            else:
                toast("Bill total must be greater than 0")
            return
        # ──────────────────────────────────────────────────────────────────────

        all_people = self._all_people()
        breakdown = {}

        # 1. ถ้ามีรายการสินค้า (Items) -> คำนวณตามที่ติ๊กเลือกในแต่ละรายการ
        if self._items:
            from core.split_engine import split_by_items
            breakdown = split_by_items(self._items, all_people)
        
        # 2. ถ้าไม่มีสินค้า แต่เลือกโหมด Custom Amount -> ใช้ยอดที่กรอกมือ
        elif self.split_mode == 'custom':
            custom_total = 0.0
            for name in all_people:
                amt_str = self._custom_amounts.get(name, '0.00').replace(',', '')
                try:
                    amt = float(amt_str)
                except:
                    amt = 0.0
                breakdown[name] = amt
                custom_total += amt
            
            # เช็คว่ายอดรวมตรงกันมั้ย (อนุโลมให้ต่างกันได้ไม่เกิน 1 บาท)
            if abs(custom_total - total) > 1.0:
                toast(f"Total doesn't match! Sum is ฿{custom_total:,.2f}")
                return
        
        # 3. ถ้าไม่มีสินค้า และเลือกโหมด Equal -> หารเท่า
        else:
            from core.split_engine import split_equally
            breakdown = split_equally(total, all_people)

        summary = self.manager.get_screen('summary_screen')
        summary.bill_name = bill_name
        summary.total = total
        summary.breakdown = dict(breakdown)
        summary.bill_items = list(self._items)
        self.manager.current = 'summary_screen'
