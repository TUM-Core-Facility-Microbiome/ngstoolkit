from __future__ import annotations
from typing import TypeVar, Optional, List

_T = TypeVar('_T')
_G = TypeVar('_G')


class DoublyLinkedListElement(object):
    def __init__(self, value: _T, prev: Optional[DoublyLinkedListElement], next: Optional[DoublyLinkedListElement]):
        self._value = value
        self._prev = prev
        self._next = next

    def get_value(self) -> _T:
        return self._value

    def set_prev(self, new_prev: Optional[DoublyLinkedListElement]):
        self._prev = new_prev

    def get_prev(self) -> Optional[DoublyLinkedListElement]:
        return self._prev

    def set_next(self, new_next: Optional[DoublyLinkedListElement]):
        self._next = new_next

    def get_next(self) -> Optional[DoublyLinkedListElement]:
        return self._next

    def __str__(self):
        return f"DoublyLinkedListElement{{value={repr(str(self._value))}, prev={self._prev is not None}, next={self._next is not None}}}"


class DoublyLinkedList(object):
    def __init__(self):
        self._head_element: Optional[DoublyLinkedListElement] = None
        self._tail_element: Optional[DoublyLinkedListElement] = None

    def push(self, value: _T):
        """Add to front of list."""
        new_element = DoublyLinkedListElement(
            value=value,
            next=self._head_element,
            prev=None
        )

        if self._head_element is not None:
            self._head_element.set_prev(new_element)

        self._head_element = new_element

        if self._tail_element is None:
            self._tail_element = new_element

    def append(self, new_data):
        """Add to end of list."""
        new_node = DoublyLinkedListElement(new_data, self._tail_element, None)

        if self._tail_element is not None:
            self._tail_element.set_next(new_node)

        self._tail_element = new_node

        if self._head_element is None:
            self._head_element = new_node

    def transverse(self):
        current: DoublyLinkedListElement = self.get_head()
        while current is not None:
            yield current
            current = current.get_next()

    def get_head(self) -> Optional[DoublyLinkedListElement]:
        return self._head_element

    def get_tail(self) -> Optional[DoublyLinkedListElement]:
        return self._tail_element

    def __str__(self):
        s = ""
        for element in self.transverse():
            s += str(element) + " "
        return s
