from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ListProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from core.models import Friend
from kivy.uix.scrollview import ScrollView

# Custom widget for the bill items
class EditableBillItem(MDBoxLayout):
    item_name = StringProperty()
    item_qty = StringProperty("1")
    item_price = StringProperty()

class NewSplitScreen(Screen):
    split_mode = StringProperty('equal')
    selected_participants = ListProperty([]) # Store simply names for phase 1
    friend_dialog = None
    
    def on_enter(self, *args):
        # We can trigger initial calculate here just in case
        self.recalculate_total()
        self.set_split_mode('equal')
        
        # Add "Me" as default participant if empty
        if not self.selected_participants:
            self.selected_participants = ["Me"]
            self._render_participants()

    def go_back(self):
        """Navigate back to the scan screen"""
        self.manager.current = 'scan_screen'

    def populate_data_from_ai(self, result):
        """Populate UI with data received from AI"""
        # Set title
        self.ids.bill_title.text = result.get("title", "Scanned Bill")
        
        # Clear old items
        self.ids.items_list.clear_widgets()
        
        # Add generated items
        items = result.get("items", [])
        for item in items:
            self.add_item_row(item.get("name", ""), str(item.get("price", 0.0)))
            
        # Remove tax manipulation here
        self.recalculate_total()

    def add_item_row(self, name="", price="", qty="1"):
        """Add a new item row to the list"""
        row = EditableBillItem()
        row.ids.item_name_input.text = name
        row.ids.item_qty_input.text = str(qty)
        row.ids.item_price_input.text = price
        
        # Bind text change to recalculate total
        row.ids.item_qty_input.bind(text=self._on_input_changed)
        row.ids.item_price_input.bind(text=self._on_input_changed)
        
        self.ids.items_list.add_widget(row)
        self.recalculate_total()

    def _on_input_changed(self, instance, value):
        self.recalculate_total()

    def on_delete_item_widget(self, widget):
        """Delete an item row from the list"""
        self.ids.items_list.remove_widget(widget)
        self.recalculate_total()

    def on_add_item(self):
        """Manually add an empty item row"""
        self.add_item_row("", "0", "1")

    def recalculate_total(self, *args):
        """Calculate subtotal and grand total dynamically"""
        subtotal = 0.0
        
        for child in self.ids.items_list.children:
            if isinstance(child, EditableBillItem):
                price_text = child.ids.item_price_input.text
                qty_text = child.ids.item_qty_input.text
                
                try:
                    price = float(price_text) if price_text else 0.0
                    qty = int(qty_text) if qty_text else 1
                    subtotal += (price * qty)
                except ValueError:
                    pass
        grand_total = subtotal
        
        if 'subtotal_label' in self.ids:
            self.ids.subtotal_label.text = f"${subtotal:,.2f}"
            self.ids.grand_total_label.text = f"${grand_total:,.2f}"

    def set_split_mode(self, mode):
        """Toggle between equal or custom split mode"""
        from kivy.utils import get_color_from_hex
        self.split_mode = mode
        
        if mode == 'equal':
            self.ids.btn_split_equal.md_bg_color = get_color_from_hex("#00C853")
            self.ids.btn_split_equal.text_color = get_color_from_hex("#FFFFFF")
            self.ids.btn_split_custom.md_bg_color = get_color_from_hex("#E0E0E0")
            self.ids.btn_split_custom.text_color = get_color_from_hex("#757575")
        else:
            self.ids.btn_split_custom.md_bg_color = get_color_from_hex("#00C853")
            self.ids.btn_split_custom.text_color = get_color_from_hex("#FFFFFF")
            self.ids.btn_split_equal.md_bg_color = get_color_from_hex("#E0E0E0")
            self.ids.btn_split_equal.text_color = get_color_from_hex("#757575")

    def on_add_friend(self):
        """Open friend selection modal"""
        friends = Friend.select().order_by(Friend.name)
        
        if not friends:
            from kivymd.toast import toast
            toast("No friends available. Add them in the Friends tab!")
            return
            
        # Create dialog content
        scroll = ScrollView()
        list_view = MDList()
        
        for f in friends:
            if f.name not in self.selected_participants:
                item = OneLineListItem(
                    text=f.name,
                    on_release=lambda x, fname=f.name: self._select_friend(fname)
                )
                list_view.add_widget(item)
                
        scroll.add_widget(list_view)
        
        app = MDApp.get_running_app()
        self.friend_dialog = MDDialog(
            title="Select a Friend",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=app.theme_cls.error_color,
                    on_release=lambda x: self.friend_dialog.dismiss()
                )
            ]
        )
        self.friend_dialog.open()

    def _select_friend(self, name):
        self.selected_participants.append(name)
        self.friend_dialog.dismiss()
        self._render_participants()
        
    def on_remove_participant(self, row_widget):
        name = row_widget.friend_name
        if name in self.selected_participants and name != "Me":
            self.selected_participants.remove(name)
            self._render_participants()
            
    def _render_participants(self):
        """Re-render the participant visual list"""
        from kivy.factory import Factory
        self.ids.participants_list.clear_widgets()
        
        for name in self.selected_participants:
            row = Factory.NewSplitParticipantRow()
            row.friend_name = name
            row.avatar_initials = name[:2].upper()
            self.ids.participants_list.add_widget(row)

    def on_calculate(self):
        """Advance to Summary Screen along with bill data"""
        from core.split_engine import split_equally
        
        # 1. Gather Items
        items = []
        subtotal = 0.0
        for child in self.ids.items_list.children:
            if isinstance(child, EditableBillItem):
                price_text = child.ids.item_price_input.text
                qty_text = child.ids.item_qty_input.text
                try:
                    price = float(price_text) if price_text else 0.0
                    qty = int(qty_text) if qty_text else 1
                    items.append({'name': child.ids.item_name_input.text, 'price': price, 'quantity': qty})
                    subtotal += (price * qty)
                except ValueError:
                    pass
                    
        # 2. Gather Participants
        participants = list(self.selected_participants) if self.selected_participants else ["Me"]
        
        # 3. Calculate Split
        if self.split_mode == 'equal':
            split_result = split_equally(subtotal, participants)
        else:
            # Placeholder for custom split (defaults to equal for now to prevent crash)
            split_result = split_equally(subtotal, participants)
            
        bill_data = {
            'title': self.ids.bill_title.text or 'Untitled Bill',
            'total': subtotal,
            'notes': self.ids.notes_input.text
        }
        
        # Pass to summary screen
        summary_screen = self.manager.get_screen('summary_screen')
        summary_screen.receive_data(bill_data, split_result, items)
        
        print("Moving to Summary Screen with calculated data...")
        self.manager.current = 'summary_screen'
