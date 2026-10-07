"""
AVL Tree Implementation for Warehouse Inventory Management.

Academic Purpose:
Self-balancing Binary Search Tree ensuring O(log n) worst-case time
complexity for SKU insertion, searching, and deletion by maintaining
the AVL balance condition: |height(left) - height(right)| <= 1.
"""

from typing import Optional, Dict, Any, List, Tuple


class AVLNode:
    """Represents a node in the AVL Tree storing an inventory record."""

    def __init__(self, item: Dict[str, Any]):
        self.sku: str = str(item["sku"]).strip().upper()
        self.item: Dict[str, Any] = {
            "sku": self.sku,
            "name": str(item.get("name", "")),
            "category": str(item.get("category", "")),
            "quantity": int(item.get("quantity", 0)),
            "location": str(item.get("location", "")),
            "priority": int(item.get("priority", 1)),
        }
        self.height: int = 1
        self.left: Optional["AVLNode"] = None
        self.right: Optional["AVLNode"] = None

    def balance_factor(self) -> int:
        """Calculate balance factor: height(left) - height(right)."""
        left_h = self.left.height if self.left else 0
        right_h = self.right.height if self.right else 0
        return left_h - right_h

    def update_height(self) -> None:
        """Update node height based on children."""
        left_h = self.left.height if self.left else 0
        right_h = self.right.height if self.right else 0
        self.height = 1 + max(left_h, right_h)


class AVLTree:
    """
    Self-balancing AVL Tree storing inventory keyed by SKU.
    Includes explicit tracking of rotations, comparisons, and traversals.
    """

    def __init__(self):
        self.root: Optional[AVLNode] = None
        self.rotation_stats = {
            "left_rotations": 0,
            "right_rotations": 0,
            "left_right_rotations": 0,
            "right_left_rotations": 0,
        }
        self.size: int = 0

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        return node.balance_factor() if node else 0

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        r"""
        Right Rotation (RR) on node y:
             y                 x
            / \               / \
           x   T3    ==>     T1  y
          / \                   / \
         T1  T2                T2  T3
        """
        x = y.left
        assert x is not None
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.update_height()
        x.update_height()

        self.rotation_stats["right_rotations"] += 1
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        r"""
        Left Rotation (LL) on node x:
           x                     y
          / \                   / \
         T1  y       ==>       x   T3
            / \               / \
           T2  T3            T1  T2
        """
        y = x.right
        assert y is not None
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.update_height()
        y.update_height()

        self.rotation_stats["left_rotations"] += 1
        return y

    def insert(self, item: Dict[str, Any]) -> Tuple[bool, str, int]:
        """
        Insert an inventory item into AVL Tree.
        Returns: (success: bool, message: str, comparisons: int)
        """
        sku = str(item.get("sku", "")).strip().upper()
        if not sku:
            raise ValueError("SKU cannot be empty")
        if int(item.get("quantity", 0)) < 0:
            raise ValueError("Quantity cannot be negative")

        comparisons = [0]
        try:
            self.root = self._insert_node(self.root, item, comparisons)
            self.size += 1
            return True, f"SKU '{sku}' inserted successfully.", comparisons[0]
        except KeyError as e:
            return False, str(e), comparisons[0]

    def _insert_node(
        self, node: Optional[AVLNode], item: Dict[str, Any], comparisons: List[int]
    ) -> AVLNode:
        sku = str(item["sku"]).strip().upper()

        # Standard BST insertion
        if not node:
            return AVLNode(item)

        comparisons[0] += 1
        if sku < node.sku:
            node.left = self._insert_node(node.left, item, comparisons)
        elif sku > node.sku:
            node.right = self._insert_node(node.right, item, comparisons)
        else:
            raise KeyError(f"Duplicate SKU '{sku}': Item already exists in inventory.")

        # Update height
        node.update_height()

        # Check balance factor
        balance = self._get_balance(node)

        # 4 Rebalancing cases:
        # Case 1: Left-Left (Right rotation)
        if balance > 1 and sku < node.left.sku:
            return self._rotate_right(node)

        # Case 2: Right-Right (Left rotation)
        if balance < -1 and sku > node.right.sku:
            return self._rotate_left(node)

        # Case 3: Left-Right (Left rotation on left child, then Right rotation on node)
        if balance > 1 and sku > node.left.sku:
            self.rotation_stats["left_right_rotations"] += 1
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Case 4: Right-Left (Right rotation on right child, then Left rotation on node)
        if balance < -1 and sku < node.right.sku:
            self.rotation_stats["right_left_rotations"] += 1
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, sku: str) -> Tuple[Optional[Dict[str, Any]], int, List[str]]:
        """
        Search for item by SKU in AVL tree.
        Returns: (item: Optional[Dict], comparisons: int, path: List[str])
        """
        sku = sku.strip().upper()
        current = self.root
        comparisons = 0
        path = []

        while current:
            comparisons += 1
            path.append(current.sku)
            if sku == current.sku:
                return current.item.copy(), comparisons, path
            elif sku < current.sku:
                current = current.left
            else:
                current = current.right

        return None, comparisons, path

    def _min_value_node(self, node: AVLNode) -> AVLNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def delete(self, sku: str) -> Tuple[bool, str, int]:
        """
        Delete an item by SKU and rebalance.
        Returns: (success: bool, message: str, comparisons: int)
        """
        sku = sku.strip().upper()
        comparisons = [0]
        found = [False]

        self.root = self._delete_node(self.root, sku, comparisons, found)
        if found[0]:
            self.size -= 1
            return True, f"SKU '{sku}' deleted successfully.", comparisons[0]
        return False, f"SKU '{sku}' not found in inventory.", comparisons[0]

    def _delete_node(
        self,
        node: Optional[AVLNode],
        sku: str,
        comparisons: List[int],
        found: List[bool],
    ) -> Optional[AVLNode]:
        if not node:
            return None

        comparisons[0] += 1
        if sku < node.sku:
            node.left = self._delete_node(node.left, sku, comparisons, found)
        elif sku > node.sku:
            node.right = self._delete_node(node.right, sku, comparisons, found)
        else:
            # Node found
            found[0] = True
            # Case 1 & 2: 0 or 1 child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Case 3: 2 children -> get inorder successor
            successor = self._min_value_node(node.right)
            node.sku = successor.sku
            node.item = successor.item.copy()
            node.right = self._delete_node(
                node.right, successor.sku, comparisons, [False]
            )

        if node is None:
            return None

        # Update height
        node.update_height()
        balance = self._get_balance(node)

        # Rebalance
        # Left Left
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)

        # Left Right
        if balance > 1 and self._get_balance(node.left) < 0:
            self.rotation_stats["left_right_rotations"] += 1
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right Right
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)

        # Right Left
        if balance < -1 and self._get_balance(node.right) > 0:
            self.rotation_stats["right_left_rotations"] += 1
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def inorder_traversal(self) -> List[Dict[str, Any]]:
        """Inorder traversal (Left, Root, Right) -> yields items sorted by SKU."""
        result: List[Dict[str, Any]] = []

        def _inorder(node: Optional[AVLNode]):
            if node:
                _inorder(node.left)
                result.append(node.item.copy())
                _inorder(node.right)

        _inorder(self.root)
        return result

    def preorder_traversal(self) -> List[Dict[str, Any]]:
        """Preorder traversal (Root, Left, Right) -> reveals tree hierarchy."""
        result: List[Dict[str, Any]] = []

        def _preorder(node: Optional[AVLNode]):
            if node:
                result.append(node.item.copy())
                _preorder(node.left)
                _preorder(node.right)

        _preorder(self.root)
        return result

    def to_tree_dict(self) -> Optional[Dict[str, Any]]:
        """Convert tree to nested dictionary representation for frontend visualization."""
        def _build_dict(node: Optional[AVLNode]) -> Optional[Dict[str, Any]]:
            if not node:
                return None
            return {
                "sku": node.sku,
                "name": node.item["name"],
                "category": node.item["category"],
                "quantity": node.item["quantity"],
                "location": node.item["location"],
                "priority": node.item["priority"],
                "height": node.height,
                "balance_factor": node.balance_factor(),
                "left": _build_dict(node.left),
                "right": _build_dict(node.right),
            }

        return _build_dict(self.root)
