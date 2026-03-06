from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, DictProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


class ResultScreen(Screen):
    bill_id = NumericProperty(-1)
    bill_title = StringProperty('Bill')
    total = NumericProperty(0.0)
    breakdown = DictProperty({})  # fallback for no-DB
    _participants_data = ListProperty([]) # List of dicts
    _items_data = ListProperty([]) # List of items

    def on_enter(self, *args):
        self._load_data()
        self._populate_items()
        self._populate_participants()
        self._generate_and_show_qr()

    def _load_data(self):
        """โหลดข้อมูลจาก DB ถ้ามี bill_id, ถ้าไม่มีใช้ breakdown เดิม"""
        self._participants_data = []
        self._items_data = getattr(self, 'bill_items', []) # Fallback for items from NewSplit
        
        if self.bill_id > 0:
            from core.storage import get_bill_details
            details = get_bill_details(self.bill_id)
            if details:
                self.bill_title = details.get('title', self.bill_title)
                self.total = details.get('total', self.total)
                self._participants_data = details.get('participants', [])
                self._items_data = details.get('items', self._items_data)
        else:
            # Fallback
            for name, amount in self.breakdown.items():
                self._participants_data.append({
                    "id": -1,
                    "name": name,
                    "amount": amount,
                    "is_paid": False
                })

    def _generate_and_show_qr(self):
        from kivy.storage.jsonstore import JsonStore
        import promptpay.qrcode
        import qrcode
        import os
        from kivy.clock import Clock

        store = JsonStore('settings.json')
        promptpay_number = store.get('user').get('promptpay', '') if store.exists('user') else ''
        
        # Clean the number
        promptpay_number = promptpay_number.replace('-', '').replace(' ', '')
        
        qr_image = self.ids.qr_image
        qr_container = self.ids.qr_container
        
        if not promptpay_number:
            qr_container.opacity = 0
            qr_container.height = 0
            return
            
        try:
            # Generate PromptPay Payload
            payload = promptpay.qrcode.generate_payload(promptpay_number, self.total)
            
            # Generate QR Code Image
            img = qrcode.make(payload)
            qr_path = "temp_promptpay_qr.png"
            img.save(qr_path)
            
            # Update UI
            qr_image.source = qr_path
            qr_image.reload()
            qr_container.opacity = 1
            qr_container.height = "240dp"
            
            # Provide info text
            self.ids.qr_info_label.text = f"Scan to pay ฿{self.total:,.2f}"
            
        except Exception as e:
            print(f"[ResultScreen] QR Generation failed: {e}")
            qr_container.opacity = 0
            qr_container.height = 0

    def _populate_items(self):
        container = self.ids.get('items_list_container')
        heading = self.ids.get('items_heading_label')
        if not container or getattr(heading, 'opacity', None) is None:
            return
            
        container.clear_widgets()
        if not self._items_data:
            # ซ่อนส่วนนี้ทิ้งถ้าบิลเก่าๆ ไม่มีข้อมูล items
            container.opacity = 0
            container.height = "0dp"
            heading.opacity = 0
            heading.height = "0dp"
            return
            
        # เปิดคืนกรณีเคยถูกซ่อน
        container.opacity = 1
        heading.opacity = 1
        heading.height = "32dp"
        
        from kivymd.uix.label import MDLabel
        from kivy.uix.boxlayout import BoxLayout
        
        for item in self._items_data:
            name = item.get('name', 'Item')
            price = item.get('price', 0.0)
            qty = item.get('quantity', 1)
            
            card = MDCard(
                size_hint_y=None,
                height='48dp',
                radius=[12, 12, 12, 12],
                md_bg_color=get_color_from_hex('#F8FAFC'),
                elevation=0,
                padding=['16dp', '0dp', '16dp', '0dp']
            )
            
            box = BoxLayout(orientation='horizontal')
            
            name_lbl = MDLabel(
                text=f"{name} (x{qty})", 
                font_style='Subtitle2', 
                theme_text_color='Custom', 
                text_color=get_color_from_hex('#334155'),
                valign='center'
            )
            price_lbl = MDLabel(
                text=f"฿{price:,.2f}", 
                halign='right', 
                valign='center',
                font_style='Subtitle2',
                bold=True, 
                theme_text_color='Custom', 
                text_color=get_color_from_hex('#065F46')
            )
            
            box.add_widget(name_lbl)
            box.add_widget(price_lbl)
            card.add_widget(box)
            container.add_widget(card)

    def _populate_participants(self):
        participants_list = self.ids.participants_list
        participants_list.clear_widgets()
        for p in self._participants_data:
            row = self._make_participant_row(p)
            participants_list.add_widget(row)

    def _make_participant_row(self, p_data):
        from kivymd.uix.selectioncontrol import MDCheckbox
        
        p_id = p_data.get('id', -1)
        name = p_data.get('name', 'Unknown')
        amount = p_data.get('amount', 0.0)
        is_paid = p_data.get('is_paid', False)
        
        card = MDCard(
            size_hint_y=None,
            height='72dp',
            radius=[20, 20, 20, 20],
            md_bg_color=get_color_from_hex('#FFFFFF'),
            elevation=0,
            padding=['16dp', '12dp', '16dp', '12dp'],
            ripple_behavior=True
        )
        card.bind(on_release=lambda x, n=name, a=amount: self.show_person_qr(n, a))

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

        # Checkbox for paid status
        chk_box = BoxLayout(orientation='vertical', size_hint_x=None, width='48dp', padding='0dp')
        checkbox = MDCheckbox(
            size_hint=(None, None),
            size=('48dp', '48dp'),
            active=is_paid,
            pos_hint={'center_x': .5, 'center_y': .5}
        )
        
        # เราจะไม่ bind on_active เพราะจะยิงรัวๆ ตอนโหลด ให้ใช้ on_release หรือวิธีเก็บสถานะแทน
        # แต่เพื่อความง่าย เราจะ bind active ปกติ แล้วเช็คว่าต่างจากข้อมูลเดิมไหมในฟังก์ชัน
        checkbox.bind(active=lambda instance, value, pid=p_id, c=checkbox, n=name, op=is_paid: 
                      self._on_participant_paid_toggle(pid, value, c, n, op))
        chk_box.add_widget(checkbox)
        
        amount_card = MDCard(
            size_hint=(None, None),
            size=('80dp', '36dp'),
            radius=[18, 18, 18, 18],
            md_bg_color=get_color_from_hex('#D1FAE5'),
            elevation=0,
            pos_hint={'center_y': .5}
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
        box.add_widget(chk_box)

        card.add_widget(box)
        return card

    def _on_participant_paid_toggle(self, participant_id, is_paid, checkbox_widget, name, original_paid_state):
        """อัปเดตสถานะการจ่ายเงินของเพื่อนลง DB พร้อม Dialog ยืนยัน"""
        # ถ้าค่าใหม่ตรงกับค่าดั้งเดิมในฐานข้อมูล (เช่นตอนระบบเพิ่งโหลดข้อมูลและเซ็ต active) => ข้าม
        if is_paid == original_paid_state:
            return
            
        if participant_id < 0:
            # รายการ fallback (ไม่มี DB) => ปล่อยผ่าน
            return

        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.app import MDApp
        from kivy.clock import Clock
        
        # ป้องกันเปิดหลาย popup ซ้อนกัน
        if hasattr(self, 'dialog') and getattr(self, 'dialog', None):
            self.dialog.dismiss()
            self.dialog = None

        def _close_dialog(*args):
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.dismiss()
                self.dialog = None

        def on_cancel(*args):
            _close_dialog()
            # คืนค่ากลับเป็นสถานะเดิมแบบเงียบๆ ป้องกัน event ซ้ำ
            checkbox_widget.active = original_paid_state

        def on_confirm(*args):
            _close_dialog()
            from core.storage import update_participant_paid
            update_participant_paid(participant_id, is_paid)
            print(f"[Result] Participant {participant_id} ({name}) paid status = {is_paid}")
            # รีโหลดข้อมูลใหม่ทั้งหมดโดยหน่วงเวลาเล็กน้อยเพื่อให้ Dialog ปิดสนิทก่อน
            Clock.schedule_once(lambda dt: self.on_enter(), 0.15)

        action_text = "โอนเงินเรียบร้อยแล้ว" if is_paid else "ยังไม่ได้โอนเงิน"
        theme_cls = MDApp.get_running_app().theme_cls

        btn_cancel = MDFlatButton(
            text="CANCEL",
            theme_text_color="Custom",
            text_color=theme_cls.error_color,
            on_release=on_cancel
        )

        btn_confirm = MDFlatButton(
            text="CONFIRM",
            theme_text_color="Custom",
            text_color=theme_cls.primary_color,
            on_release=on_confirm
        )

        self.dialog = MDDialog(
            title="ยืนยันการตั้งค่า",
            text=f"คุณต้องการเปลี่ยนสถานะของ [b]{name}[/b] เป็น [b]'{action_text}'[/b] ใช่หรือไม่?",
            buttons=[btn_cancel, btn_confirm],
            auto_dismiss=False  # บังคับให้กดปุ่มเท่านั้น
        )
        self.dialog.open()

    def show_person_qr(self, name, amount):
        """แสดง Dialog พร้อม QR Code และจำนวนเงิน สำหรับคนๆ เดียว"""
        print(f"[Result] Show QR for {name} - ฿{amount}")
        
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.app import MDApp
        from kivy.storage.jsonstore import JsonStore
        from kivy.uix.image import Image
        import promptpay.qrcode
        import qrcode
        import os
        
        # ป้องกันเปิดหลาย popup ซ้อนกัน
        if hasattr(self, 'qr_dialog') and getattr(self, 'qr_dialog', None):
            self.qr_dialog.dismiss()
            self.qr_dialog = None
        
        store = JsonStore('settings.json')
        promptpay_number = store.get('user').get('promptpay', '') if store.exists('user') else ''
        
        if not promptpay_number:
            from kivymd.toast import toast
            toast("กรุณาตั้งค่า PromptPay ใน Settings ก่อนใช้งาน QR")
            return
            
        promptpay_number = promptpay_number.replace('-', '').replace(' ', '')
        payload = promptpay.qrcode.generate_payload(promptpay_number, float(amount))
        img = qrcode.make(payload)
        qr_path = f"temp_qr_{name}.png"
        img.save(qr_path)
        
        # สร้าง Layout เก็บรูป QR และข้อความจำนวนเงิน
        content = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None)
        
        qr_image = Image(source=qr_path, size_hint=(1, None), height="200dp", allow_stretch=True)
        content.add_widget(qr_image)
        content.add_widget(MDLabel(
            text=f"ยอดโอน: ฿{amount:,.2f}",
            halign="center",
            theme_text_color="Primary",
            font_style="H6"
        ))
        
        # ใช้ height ของ Content ให้พอดี
        content.height = "250dp"

        def _close_qr_dialog(*args):
            if hasattr(self, 'qr_dialog') and self.qr_dialog:
                self.qr_dialog.dismiss()
                self.qr_dialog = None
            if os.path.exists(qr_path):
                os.remove(qr_path)

        theme_cls = MDApp.get_running_app().theme_cls

        self.qr_dialog = MDDialog(
            title=f"QR Code ของ {name}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    theme_text_color="Custom",
                    text_color=theme_cls.primary_color,
                    on_release=_close_qr_dialog
                ),
            ],
        )
        self.qr_dialog.open()

    def go_back(self):
        self.manager.current = 'summary_screen'

    def go_home(self):
        self.manager.current = 'dashboard'

    def on_copy_clipboard(self):
        from core.split_engine import format_result_text
        from kivy.core.clipboard import Clipboard
        from kivymd.toast import toast
        
        text = format_result_text(self.bill_title, self.total, self._participants_data, self._items_data)
        Clipboard.copy(text)
        print('[Result] Copied to clipboard')
        toast("คัดลอกสรุปรายการแล้ว นำไปวางในแชทได้เลย!")

