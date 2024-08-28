class Stack(object):
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        if (self.size() == 0):
            return None
        else:
            return self.items[self.size() - 1]

    def peek_item(self, item_index):
        if (self.size() == 0):
            return None
        else:
            return self.items[(self.size() - (self.size() - item_index) - 1)]

    def size(self):
        return len(self.items)

    def second_peek(self):
        if (self.size() == 0 or self.size() == 1):
            return None
        else:
            return self.items[self.size() - 2]

    def __str__(self):
        string = ''
        for each in self.items:
            string += (str(each.get_file_path()) + '\n')
        return string

    def __repr__(self):
        return str(self)
