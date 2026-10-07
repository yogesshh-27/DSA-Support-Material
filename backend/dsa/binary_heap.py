"""
Max-Heap / Priority Queue Implementation for Warehouse Alerts.

Academic Purpose:
A complete binary tree stored as an array where every parent's priority
is greater than or equal to its children's priorities:
A[parent(i)] >= A[i].
Ensures O(1) peek for highest priority warehouse alerts (e.g. critical stockout)
and O(log n) insert and extract-max.
"""

from typing import List, Dict, Any, Optional


class Alert:
    """Represents a warehouse alert with priority."""

    def __init__(self, sku: str, alert_type: str, priority: int, quantity: int, location: str):
        self.sku = str(sku).strip().upper()
        self.alert_type = str(alert_type).strip()
        self.priority = int(priority)
        self.quantity = int(quantity)
        self.location = str(location).strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku": self.sku,
            "alert_type": self.alert_type,
            "priority": self.priority,
            "quantity": self.quantity,
            "location": self.location,
        }

    def __repr__(self) -> str:
        return f"Alert({self.sku}, {self.alert_type}, P={self.priority})"


class MaxHeap:
    """
    Max Heap implementation using 0-indexed dynamic list.
    Parent of i: (i - 1) // 2
    Left child of i: 2 * i + 1
    Right child of i: 2 * i + 2
    """

    def __init__(self):
        self.heap: List[Alert] = []

    def size(self) -> int:
        return len(self.heap)

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def parent(self, i: int) -> int:
        return (i - 1) // 2

    def left_child(self, i: int) -> int:
        return 2 * i + 1

    def right_child(self, i: int) -> int:
        return 2 * i + 2

    def insert(self, alert_data: Dict[str, Any]) -> Alert:
        """
        Insert alert into Max Heap.
        Time Complexity: O(log n)
        """
        alert = Alert(
            sku=alert_data.get("sku", "UNKNOWN"),
            alert_type=alert_data.get("alert_type", "General Alert"),
            priority=int(alert_data.get("priority", 1)),
            quantity=int(alert_data.get("quantity", 0)),
            location=alert_data.get("location", "Unknown Location"),
        )
        self.heap.append(alert)
        self._heapify_up(len(self.heap) - 1)
        return alert

    def _heapify_up(self, index: int) -> None:
        """Move element up until max heap property holds."""
        while index > 0 and self.heap[index].priority > self.heap[self.parent(index)].priority:
            parent_idx = self.parent(index)
            # Swap
            self.heap[index], self.heap[parent_idx] = self.heap[parent_idx], self.heap[index]
            index = parent_idx

    def peek(self) -> Optional[Dict[str, Any]]:
        """
        View highest priority alert without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.heap[0].to_dict()

    def extract_max(self) -> Optional[Dict[str, Any]]:
        """
        Remove and return highest priority alert.
        Time Complexity: O(log n)
        """
        if self.is_empty():
            return None

        root_alert = self.heap[0]
        last_alert = self.heap.pop()

        if not self.is_empty():
            self.heap[0] = last_alert
            self._heapify_down(0)

        return root_alert.to_dict()

    def _heapify_down(self, index: int) -> None:
        """Move element down until max heap property holds."""
        max_idx = index
        left = self.left_child(index)
        right = self.right_child(index)

        if left < len(self.heap) and self.heap[left].priority > self.heap[max_idx].priority:
            max_idx = left

        if right < len(self.heap) and self.heap[right].priority > self.heap[max_idx].priority:
            max_idx = right

        if max_idx != index:
            self.heap[index], self.heap[max_idx] = self.heap[max_idx], self.heap[index]
            self._heapify_down(max_idx)

    def display_heap(self) -> List[Dict[str, Any]]:
        """Return list of all alerts in current array heap order."""
        return [alert.to_dict() for alert in self.heap]
