from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


class ResultScreen(Screen):
    bill_title = StringProperty('Bill')
    total = NumericProperty(0.0)
    breakdown = DictProperty({})  # {name: amount}

    def on_enter(self, *args):
        self._populate_participants()

    def _populate_participants(self):
        participants_list = self.ids.participants_list
        participants_list.clear_widgets()
        for name, amount in self.breakdown.items():
            row = self._make_participant_row(name, amount)
            participants_list.add_widget(row)

    def _make_participant_row(self, name, amount):
        card = MDCard(
            size_hint_y=None,
            height='72dp',
            radius=[20, 20, 20, 20],
            md_bg_color=get_color_from_hex('#FFFFFF'),
            elevation=0,
            padding=['16dp', '12dp', '16dp', '12dp'],
        )
        box = BoxLayout(orientation='horizontal', spacing='12dp')

        avatar = MDCard(
            size_hint=(None, None),
            size=('44dp', '44dp'),
            radius=[22, 22, 22, 22],
            md_bg_color=get_color_from_hex('#FFF0EB'),
            elevation=0,
        )
        ltr = MDLabel(
            text=name[:1].upper() if name else '?',
            halign='center',
            valign='center',
            bold=True,
            theme_text_color='Custom',
            text_color=get_color_from_hex('#F45925'),
        )
        avatar.add_widget(ltr)
        box.add_widget(avatar)

        vbox = BoxLayout(orientation='vertical', spacing='2dp')
        name_lbl = MDLabel(
            text=name,
            font_style='Subtitle1',
            bold=True,
            theme_text_color='Custom',
            text_color=get_color_from_hex('#0E1B14'),
            adaptive_height=True,
        )
        amount_lbl = MDLabel(
            text='Owes ' + '฿' + '{:,.2f}'.format(amount),
            font_style='Caption',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#6B7280'),
            adaptive_height=True,
        )
        vbox.add_widget(name_lbl)
        vbox.add_widget(amount_lbl)
        box.add_widget(vbox)
        box.add_widget(Widget())

        amount_card = MDCard(
            size_hint=(None, None),
            size=('100dp', '36dp'),
            radius=[18, 18, 18, 18],
            md_bg_color=get_color_from_hex('#D1FAE5'),
            elevation=0,
        )
        amount_card_lbl = MDLabel(
            text='฿' + '{:,.2f}'.format(amount),
            halign='center',
            valign='center',
            bold=True,
            font_style='Subtitle2',
            theme_text_color='Custom',
            text_color=get_color_from_hex('#065F46'),
        )
        amount_card.add_widget(amount_card_lbl)
        box.add_widget(amount_card)

        card.add_widget(box)
        return card

    def go_back(self):
        self.manager.current = 'summary_screen'

    def go_home(self):
        self.manager.current = 'dashboard'

    def on_copy_clipboard(self):
        from core.split_engine import format_result_text
        from kivy.core.clipboard import Clipboard
        text = format_result_text(self.bill_title, self.total, self.breakdown)
        Clipboard.copy(text)
        print('[Result] Copied to clipboard')

