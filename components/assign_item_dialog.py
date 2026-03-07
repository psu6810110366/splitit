from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ObjectProperty
from components.person_toggle_row import PersonToggleRow


class AssignItemDialog(MDCard):
    item_name = StringProperty('')
    callback = ObjectProperty(None)

    def setup(self, item_name, all_people, current_assigned):
        """เรียกหลัง add_widget — ตั้งค่ารายชื่อคนและสถานะเลือก"""
        self.item_name = item_name
        self.ids.item_name_label.text = item_name
        self._rows = []
        people_list = self.ids.people_list
        people_list.clear_widgets()
        for name in all_people:
            row = PersonToggleRow()
            row.display_name = name
            row.is_selected = (name in current_assigned)
            people_list.add_widget(row)
            self._rows.append(row)

    def confirm(self):
        selected = [r.display_name for r in self._rows if r.is_selected]
        # ถ้าไม่เลือกใคร ให้ default เป็นทุกคน
        if not selected:
            selected = [r.display_name for r in self._rows]
        if self.callback:
            self.callback(selected)
        self._dismiss()

    def cancel(self):
        self._dismiss()

    def _dismiss(self):
        parent = self.parent
        if parent:
            parent.remove_widget(self)
