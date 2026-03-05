from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from components.add_friend_dialog import AddFriendDialog    # noqa: F401
from components.add_item_dialog import AddItemDialog        # noqa: F401
from components.assign_item_dialog import AssignItemDialog  # noqa: F401
from components.item_row import ItemRow
from components.person_row import PersonRow


class NewSplitScreen(Screen):
    split_mode = StringProperty('equal')

    def on_enter(self, *args):
        """รีเซ็ตฟอร์มทุกครั้งที่เข้าหน้านี้ใหม่"""
        self._items = []   # [{'name': str, 'price': float, 'assigned_to': [str]}]
        self._people = []  # [str] (ไม่รวม "Me" — จะเพิ่มในการคำนวณ)
        self._refresh_items_list()
        self._refresh_people_list()
        self.ids.bill_name_input.text = ''
        self.ids.total_amount_label.text = '0.00'
        self.split_mode = 'equal'
        self.ids.btn_split_equal.md_bg_color = [0.314, 0.784, 0.471, 1]
        self.ids.btn_split_custom.md_bg_color = [0.953, 0.961, 0.973, 1]

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
        # รีเซ็ตก่อนเติมข้อมูล
        self._items = []

        title = result.get('title', 'Scanned Bill')
        self.ids.bill_name_input.text = title

        for item in result.get('items', []):
            name = item.get('name', '')
            price = float(item.get('price', 0.0))
            if name:
                self._items.append({'name': name, 'price': price, 'assigned_to': []})

        self._refresh_items_list()
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
        dialog = AddFriendDialog()
        dialog.callback = self._on_friend_added
        dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        self.add_widget(dialog)

    def _on_friend_added(self, name):
        if name and name not in self._people:
            self._people.append(name)
            self._refresh_people_list()

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

    def _refresh_people_list(self):
        people_list = self.ids.people_list
        people_list.clear_widgets()
        for i, name in enumerate(self._people):
            row = PersonRow()
            row.display_name = name
            row.remove_cb = (lambda idx=i: self._on_person_removed(idx))
            people_list.add_widget(row)
        count = len(self._people) + 1  # +1 for "Me"
        self.ids.people_count_label.text = '{} people'.format(count)

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

    # ── Calculate ─────────────────────────────────────────────────────────────

    def on_calculate(self):
        bill_name = self.ids.bill_name_input.text.strip() or 'Untitled Bill'
        try:
            total = float(self.ids.total_amount_label.text.replace(',', ''))
        except ValueError:
            total = 0.0

        if total <= 0 and self._items:
            total = sum(item['price'] for item in self._items)

        if total <= 0:
            print('[NewSplit] Cannot calculate: total is 0')
            return

        all_people = self._all_people()

        # ถ้ามีรายการย่อย ให้คำนวณตาม assignment ของแต่ละรายการ
        if self._items:
            from core.split_engine import split_by_items
            breakdown = split_by_items(self._items, all_people)
        else:
            from core.split_engine import split_equally
            breakdown = split_equally(total, all_people)

        summary = self.manager.get_screen('summary_screen')
        summary.bill_name = bill_name
        summary.total = total
        summary.breakdown = dict(breakdown)
        summary.bill_items = list(self._items)
        self.manager.current = 'summary_screen'
