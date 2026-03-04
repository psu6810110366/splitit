from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty

# Custom widget for the bill items
class EditableBillItem(MDBoxLayout):
    item_name = StringProperty()
    item_qty = StringProperty("1")
    item_price = StringProperty()

class NewSplitScreen(Screen):
    split_mode = StringProperty('equal')
    
    def on_enter(self, *args):
        # We can trigger initial calculate here just in case
        self.recalculate_total()
        self.set_split_mode('equal')

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
            
        # Add tax if available
        tax = result.get("tax_or_service_charge", 0.0)
        if tax > 0:
            self.ids.tax_input.text = str(tax)
            
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
                        
        tax_text = self.ids.tax_input.text
        tax = 0.0
        if tax_text:
            try:
                tax = float(tax_text)
            except ValueError:
                pass
                
        grand_total = subtotal + tax
        
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
        """Open friend selection modal (to be implemented)"""
        print("Add Friend clicked")

    def on_calculate(self):
        """Advance to Summary Screen along with bill data"""
        print("Moving to Summary Screen...")
        self.manager.current = 'summary_screen'
