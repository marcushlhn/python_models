from collections.abc import Iterable

class EndOfQueueError(Exception):
    message = "reached end of queue"

    def __init__(self, message = None, *args):
        if message is None:
            message = self.message
        super().__init__(message, *args)

class Node:
    def __init__(self, value, previous_node : Node, next_node : Node):
        assert isinstance(previous_node, Node), "previous_node must be of type Node"
        assert isinstance(next_node, Node), "next_node must be of type Node"
        self.value = value
        self.next = next_node
        self.previous = previous_node

    def get_next(self) -> Node:
        return self.next

    def get_previous(self) -> Node:
        return self.previous

    def put_behind(self, value):
        next_node = Node(value, previous_node = self, next_node = self.next)
        self.next.set_previous(next_node)
        self.next = next_node
        return self

    def put_ahead(self, value):
        prev_node = Node(value, previous_node = self.previous, next_node = self)
        self.previous.set_next(prev_node)
        self.previous = prev_node
        return self

    def set_next(self, next_node : Node):
        self.next = next_node
        return self

    def set_previous(self, previous_node : Node):
        self.previous = previous_node
        return self

    def pop(self):
        self.next.set_previous(self.previous)
        self.previous.set_next(self.next)
        return self.value

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.value == other.value

    def __repr__(self):
        return f"node[{repr(self.value)}]"

    def __bool__(self):
        return True

    def __str__(self):
        return str(self.value)

class NullNode(Node):
    def __init__(self, previous_node : Node = None, next_node : Node = None):
        assert isinstance(previous_node, Node) or previous_node is None, "previous_node must be of type Node"
        assert isinstance(next_node, Node) or next_node is None, "next_node must be of type Node"
        assert previous_node is not None or next_node is not None, "Node must have either a previous or a next node"
        self.value = None
        self.previous = previous_node
        self.next = next_node 

    def __eq__(self, other):
        return False

    def __repr__(self):
        return f"node[]"

    def __bool__(self):
        return False

    def get_next(self) -> Node:
        if self.next is None:
            raise EndOfQueueError()
        return self.next

    def get_previous(self) -> Node:
        if self.previous is None:
            raise EndOfQueueError("reached beginning of queue")
        return self.previous

    def put_behind(self, value):
        if self.next is None:
            raise EndOfQueueError("cannot place value outside the queue")
        return super().put_behind(value)

    def put_ahead(self, value):
        if self.previous is None:
            raise EndOfQueueError("cannot place value outside the queue")
        return super().put_ahead(value)

    def set_next(self, next_node):
        if self.next is None:
            raise EndOfQueueError("cannot place value outside the queue")
        return super().set_next(next_node)

    def set_previous(self, previous_node):
        if self.previous is None:
            raise EndOfQueueError("cannot place value outside the queue")
        return super().set_previous(previous_node)

    def pop(self):
        raise EndOfQueueError("cannot pop null queue element")
    

class FirstNode(NullNode):
    def __init__(self, next_node : Node = None):
        if next_node is None:
            next_node = LastNode(self)
        super().__init__(next_node = next_node)

class LastNode(NullNode):
    def __init__(self, previous_node : Node = None):
        if previous_node is None:
            previous_node = FirstNode(self)
        super().__init__(previous_node = previous_node)

class Queue:
    def __init__(self, elements : Iterable = None):
        self.front = FirstNode()
        self.end = self.front.get_next()
        if isinstance(elements, Iterable):
            for x in elements:
                self.push(x)

    def push(self, value):
        """
        Appends value to the end of the queue
        """
        self.end.put_ahead(value)
        return self

    def pop(self):
        """
        Removes and returns the first value in the queue

        Raises EndOfQueueError on empty queue
        """
        node = self.front.get_next()
        if not node:
            raise EndOfQueueError("Queue is empty")
        return node.pop()

    def remove(self, value):
        """
        Removes the first instance of the value in the queue
        """
        for node in self.nodes():
            if node.value == value:
                return node.pop()
        raise KeyError("No queue node with the given value")


    def first(self):
        node = self.front.get_next()
        return node.value

    def first_node(self):
        node = self.front.get_next()
        if not node:
            return None
        return node

    def last(self):
        node = self.end.get_previous()
        return node.value

    def last_node(self):
        node = self.end.get_previous()
        if not node:
            return None
        return node

    def __getitem__(self, index : int):
        if not isinstance(index, int):
            raise ValueError("index must be int")
        if index < 0:
            raise IndexError(f"queue index {index} out of range")
        node = self.front.get_next()
        i = 0
        while node:
            if i == index:
                return node.value
            i += 1
            node = node.get_next()
        raise IndexError("queue index out of range")

    def __setitem__(self, index : int, value):
        if not isinstance(index, int):
            raise ValueError("index must be int")
        if index < 0:
            raise IndexError(f"queue index {index} out of range")
        node = self.front.get_next()
        i = 0
        while node:
            if i == index:
                node.put_ahead(value)
                return
            i += 1
            node = node.get_next()
        if i == index:
            node.put_ahead(value)
        else:
            raise IndexError("queue index out of range")

    def nodes(self):
        """
        Generator for iterating through each node of the queue
        """
        node = self.front.get_next()
        while node:
            yield node
            node = node.get_next()

    def __iter__(self):
        node = self.front.get_next()
        while node:
            yield node.value
            node = node.get_next()

    def __str__(self):
        return "*[" + ", ".join(map(str, self)) + "]"

    def __repr__(self):
        first = self.front.get_next()
        last = self.end.get_previous()
        return f"Queue[{str(first) if first else ''}{'...' if first or last else ''}{last if last else ''}]"

    def __len__(self):
        node = self.front.get_next()
        n = 0
        while node:
            n += 1
            node = node.get_next()
        return n

    def __sizeof__(self):
        return super().__sizeof__() + sum([n.__sizeof__() for n in self.nodes()])