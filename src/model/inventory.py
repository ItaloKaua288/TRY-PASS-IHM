
class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        if item is None:
            return
        self.items.append(item)

    def remove_item(self, item):
        if item is None:
            return
        self.items.remove(item)

    def use_item(self, item_pos):
        self.items[item_pos].is_used = True