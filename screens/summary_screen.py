from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.clipboard import Clipboard
from kivymd.toast import toast
from core.storage import save_bill
from core.split_engine import format_result_text

class SummaryParticipantRow(MDBoxLayout):
    name = StringProperty()
    amount = StringProperty()
    status = StringProperty("Pending")

class SummaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bill_data = {}
        self.split_result = {}
        self.items_data = []

    def go_back(self):
        self.manager.current = 'new_split_screen'

    def receive_data(self, bill_data, split_result, items_data):
        """Receive calculated data from NewSplitScreen"""
        self.bill_data = bill_data
        self.split_result = split_result
        self.items_data = items_data
        
        # Populate UI
        self.ids.summary_title.text = bill_data.get('title', 'Untitled Bill')
        self.ids.summary_total.text = f"${bill_data.get('total', 0.0):,.2f}"
        
        # Populate breakdown list
        self.ids.breakdown_list.clear_widgets()
        for name, amount in split_result.items():
            row = SummaryParticipantRow()
            row.name = name
            row.amount = f"${amount:,.2f}"
            self.ids.breakdown_list.add_widget(row)

    def on_copy_clipboard(self):
        text = format_result_text(
            self.bill_data.get('title', 'Food'),
            self.bill_data.get('total', 0.0),
            self.split_result
        )
        Clipboard.copy(text)
        toast("Copied to clipboard!")

    def on_save_and_finish(self):
        """Callback: บันทึกข้อมูลบิลลงระบบ (SQLite) และจบงาน"""
        print("Saving bill to database...")
        
        # Prepare participants data
        participants_data = []
        for name, amount in self.split_result.items():
            participants_data.append({
                'name': name,
                'amount': amount,
                'is_paid': True if name == "Me" else False # I paid my own
            })
            
        success = save_bill(self.bill_data, participants_data, self.items_data)
        if success:
            toast("Bill saved successfully!")
            self.manager.current = 'dashboard'
        else:
            toast("Failed to save bill")

