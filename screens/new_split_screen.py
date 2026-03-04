from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from components.add_friend_dialog import AddFriendDialog  # noqa: F401
from components.add_item_dialog import AddItemDialog       # noqa: F401
from components.item_row import ItemRow
from components.person_row import PersonRow


class NewSplitScreen(Screen):
    split_mode = StringProperty('equal')

    def on_enter(self, *args):
        """รีเซ็ตฟอร์มทุกครั้งที่เข้าหน้านี้ใหม่"""
        self._items = []   # [{'name': str, 'price': float}]
        self._people = []  # [str]
        self._refresh_items_list()
        self._refresh_people_list()
        self.ids.bill_name_input.text = ''
        self.ids.total_amount_label.text = '0.00'
        self.split_mode = 'equal'
        self.ids.btn_split_equal.md_bg_color = [0.314, 0.784, 0.471, 1]
        self.ids.btn_split_custom.md_bg_color = [0.953, 0.961, 0.973, 1]

    def go_back(self):
        self.manager.current = 'dashboard'

    # ── Items ──────────────────────────────────────────────────────────────

    def on_add_item(self):
        dialog = AddItemDialog()
        dialog.callback = self._on_item_added
        dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        self.add_widget(dialog)

    def _on_item_added(self, name, price):
        self._items.append({'name': name, 'price': price})
        self._refresh_items_list()

    def _on_item_deleted(self, index):
        if 0 <= index < len(self._items):
            del self._items[index]
            self._refresh_items_list()

    def _refresh_items_list(self):
        items_list = self.ids.items_list
        items_list.clear_widgets()
        total = 0.0
        for i, item in enumerate(self._items):
            row = ItemRow()
            row.item_name = item['name']
            row.price = item['price']
            idx = i
            row.delete_cb = lambda idx=idx: self._on_item_deleted(idx)
            items_list.add_widget(row)
            total += item['price']
        self.ids.total_amount_label.text = '{:.2f}'.format(total)
        self.ids.items_count_label.text = '{} Items'.format(len(self._items))

    # ── People ─────────────────────────────────────────────────────────────

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
            del self._people[index]
            self._refresh_people_list()

    def _refresh_people_list(self):
        people_list = self.ids.people_list
        people_list.clear_widgets()
        for i, name in enumerate(self._people):
            row = PersonRow()
            row.display_name = name
            idx = i
            row.remove_cb = lambda idx=idx: self._on_person_removed(idx)
            people_list.add_widget(row)
        count = len(self._people) + 1  # +1 for "Me"
        self.ids.people_count_label.text = '{} people'.format(count)

    # ── Split toggle ───────────────────────────────────────────────────────

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

    # ── Calculate ──────────────────────────────────────────────────────────

    def on_calculate(self):
        from core.split_engine import split_equally
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

        all_people = ['Me'] + list(self._people)
        breakdown = split_equally(total, all_people)

        summary = self.manager.get_screen('summary_screen')
        summary.bill_name = bill_name
        summary.total = total
        summary.breakdown = dict(breakdown)
        summary.bill_items = list(self._items)
        self.manager.current = 'summary_screen'

