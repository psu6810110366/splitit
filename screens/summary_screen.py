from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, DictProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.core.clipboard import Clipboard


class SummaryScreen(Screen):
    bill_name = StringProperty('Bill')
    total = NumericProperty(0.0)
    breakdown = DictProperty({})   # {name: amount}
    bill_items = ListProperty([])  # [{'name': str, 'price': float}]

    def on_enter(self, *args):
        self._populate_summary()

    def _populate_summary(self):
        self.ids.bill_title_label.text = self.bill_name
        self.ids.bill_total_label.text = 'Total: ' + '{:,.2f}'.format(self.total)
        self.ids.people_count_label.text = '{} People'.format(len(self.breakdown))

        breakdown_list = self.ids.breakdown_list
        breakdown_list.clear_widgets()
        for name, amount in self.breakdown.items():
            row = self._make_breakdown_row(name, amount)
            breakdown_list.add_widget(row)

    def _make_breakdown_row(self, name, amount):
        """สร้าง card แสดงชื่อ + ยอดที่ต้องจ่าย"""
        card = MDCard(
            size_hint_y=None,
            height='60dp',
            radius=[16, 16, 16, 16],
            md_bg_color=get_color_from_hex('#FFFFFF'),
            elevation=0,
            padding=['16dp', '0dp', '16dp', '0dp'],
        )
        box = BoxLayout(orientation='horizontal', spacing='12dp')

        avatar = MDCard(
            size_hint=(None, None),
            size=('36dp', '36dp'),
            radius=[18, 18, 18, 18],
            md_bg_color=get_color_from_hex('#50C878'),
            elevation=0,
        )
        ltr = MDLabel(
            text=name[:1].upper() if name else '?',
            halign='center',
            valign='center',
            bold=True,
            theme_text_color='Custom',
            text_color=get_color_from_hex('#FFFFFF'),
        )
        avatar.add_widget(ltr)
        box.add_widget(avatar)

        name_label = MDLabel(
            text=name,
            font_style='Body1',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#0E1B14'),
        )
        box.add_widget(name_label)

        from kivy.uix.widget import Widget
        box.add_widget(Widget())

        amount_label = MDLabel(
            text='฿' + '{:,.2f}'.format(amount),
            font_style='Subtitle1',
            bold=True,
            halign='right',
            size_hint_x=None,
            width='100dp',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#0E1B14'),
        )
        box.add_widget(amount_label)
        card.add_widget(box)
        return card

    def go_back(self):
        self.manager.current = 'new_split_screen'

    def on_copy_clipboard(self):
        """คัดลอกสรุปยอดไปยัง clipboard เพื่อแชร์ใน LINE/Messenger"""
        from core.split_engine import format_result_text
        text = format_result_text(self.bill_name, self.total, self.breakdown)
        Clipboard.copy(text)
        print('[Summary] Copied to clipboard')

    def on_save_and_finish(self):
        """บันทึกบิลลง SQLite แล้วไปหน้า Result"""
        from core.storage import save_bill
        bill_id = save_bill(self.bill_name, self.total, self.bill_items, self.breakdown)
        print('[Summary] Saved bill id:', bill_id)

        result = self.manager.get_screen('result_screen')
        result.bill_id = bill_id
        result.bill_title = self.bill_name
        result.total = self.total
        result.breakdown = dict(self.breakdown)
        self.manager.current = 'result_screen'

