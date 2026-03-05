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

    def on_enter(self, *args):
        self._load_data()
        self._populate_participants()
        self._generate_and_show_qr()

    def _load_data(self):
        """โหลดข้อมูลจาก DB ถ้ามี bill_id, ถ้าไม่มีใช้ breakdown เดิม"""
        self._participants_data = []
        if self.bill_id > 0:
            from core.storage import get_bill_details
            details = get_bill_details(self.bill_id)
            if details:
                self.bill_title = details.get('title', self.bill_title)
                self.total = details.get('total', self.total)
                self._participants_data = details.get('participants', [])
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

        def on_cancel(inst):
            self.dialog.dismiss()
            # คืนค่ากลับเป็นสถานะเดิม (แอบ unbind ก่อนชั่วคราวเพื่อไม่ให้ยิงลูปซ้ำ)
            checkbox_widget.active = original_paid_state

        def on_confirm(inst):
            self.dialog.dismiss()
            from core.storage import update_participant_paid
            update_participant_paid(participant_id, is_paid)
            print(f"[Result] Participant {participant_id} ({name}) paid status = {is_paid}")
            # รีโหลดข้อมูลใหม่ทั้งหมด
            self.on_enter()

        action_text = "โอนเงินเรียบร้อยแล้ว" if is_paid else "ยังไม่ได้โอนเงิน"
        
        self.dialog = MDDialog(
            title="ยืนยันการตั้งค่า",
            text=f"คุณต้องการเปลี่ยนสถานะของ [b]{name}[/b] เป็น [b]'{action_text}'[/b] ใช่หรือไม่?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.error_color,
                    on_release=on_cancel
                ),
                MDFlatButton(
                    text="CONFIRM",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=on_confirm
                ),
            ],
        )
        self.dialog.open()

    def show_person_qr(self, name, amount):
        """แสดง Dialog พร้อม QR Code สำหรับคนๆ เดียว"""
        print(f"[Result] Show QR for {name} - ฿{amount}")
        
        from kivymd.uix.dialog import MDDialog
        from kivy.storage.jsonstore import JsonStore
        import promptpay.qrcode
        import qrcode
        from kivy.uix.image import Image
        
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
        
        qr_img = Image(source=qr_path, allow_stretch=True, keep_ratio=True, size_hint_y=None, height="240dp")
        
        self.dialog = MDDialog(
            title=f"Scan to pay {name}",
            type="custom",
            content_cls=qr_img,
        )
        self.dialog.open()

    def go_back(self):
        self.manager.current = 'summary_screen'

    def go_home(self):
        self.manager.current = 'dashboard'

    def on_copy_clipboard(self):
        from core.split_engine import format_result_text
        from kivy.core.clipboard import Clipboard
        from kivymd.toast import toast
        
        text = format_result_text(self.bill_title, self.total, self.breakdown)
        Clipboard.copy(text)
        print('[Result] Copied to clipboard')
        toast("คัดลอกสรุปรายการแล้ว นำไปวางในแชทได้เลย!")

