class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def delete(self, node):
        if node is None:
            return
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        self.size -= 1

    def append(self, data):
        new_node = LinkedNode(data)
        self.size += 1
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
    
    def __str__(self):
        current = self.head
        result = []
        while current:
            result.append(str(current.data))
            current = current.next
        return ' <-> '.join(result)
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, LinkedList):
            return False
        if self.size != other.size:
            return False
        l1 = self.head
        l2 = other.head
        while l1 and l2:
            if l1 != l2:
                return False
            l1 = l1.next
            l2 = l2.next
        
        return True
    
    def __hash__(self):
        current = self.head
        hash_value = 0
        while current:
            hash_value ^= hash(current.data)
            current = current.next
        return hash_value


class LinkedNode:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None
    
    def __eq__(self, other):
        if not isinstance(other, LinkedNode):
            return False
        return self.data == other.data
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.data)







