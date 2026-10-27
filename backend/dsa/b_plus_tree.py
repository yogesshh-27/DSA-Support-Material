"""
B+ Tree Implementation for Advanced Warehouse Inventory Indexing.

Academic Purpose (Unit 5 - Advanced Data Structures):
A balanced multi-way search tree where:
1. Internal nodes store only routing/separator keys and child pointers.
2. All actual inventory data records reside exclusively in leaf nodes at the same depth.
3. Leaf nodes are linked in a continuous sequence via `next` pointers, enabling
   O(log_M n + K) range queries and O(n) sequential sorted traversal without
   expensive in-order tree traversals.
4. Auto-rebalancing via node splitting (with separator copy-up for leaves and
   key push-up for internal nodes) maintains O(log_M n) point search and insert times.
"""

from typing import List, Dict, Any, Optional, Tuple
import math


class BPlusNode:
    """Represents a node in the B+ Tree (either an internal node or a leaf node)."""

    _id_counter = 0

    def __init__(self, is_leaf: bool = False):
        BPlusNode._id_counter += 1
        self.node_id: int = BPlusNode._id_counter
        self.is_leaf: bool = is_leaf
        self.keys: List[str] = []
        # For internal nodes: list of child BPlusNode references
        self.children: List["BPlusNode"] = []
        # For leaf nodes: list of inventory record dictionaries
        self.records: List[Dict[str, Any]] = []
        # For leaf nodes: pointer to next and previous leaf node
        self.next: Optional["BPlusNode"] = None
        self.prev: Optional["BPlusNode"] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize node structure for API response and UI visualization."""
        node_info = {
            "node_id": self.node_id,
            "is_leaf": self.is_leaf,
            "keys": list(self.keys),
            "key_count": len(self.keys),
        }
        if self.is_leaf:
            node_info["records"] = [
                {
                    "product_id": r["product_id"],
                    "name": r.get("name", ""),
                    "category": r.get("category", ""),
                    "quantity": r.get("quantity", 0),
                    "location": r.get("location", ""),
                    "priority": r.get("priority", 1),
                    "unit_weight": r.get("unit_weight", 0.0),
                }
                for r in self.records
            ]
            node_info["next_id"] = self.next.node_id if self.next else None
            node_info["prev_id"] = self.prev.node_id if self.prev else None
        else:
            node_info["children_ids"] = [c.node_id for c in self.children]
            node_info["children_keys"] = [c.keys for c in self.children]
        return node_info


class BPlusTree:
    """
    Complete B+ Tree implementation supporting insertion, point search,
    range queries, linked leaf traversals, and dynamic structural visualization.
    """

    def __init__(self, order: int = 4):
        """
        Initialize B+ Tree with configurable tree order M.
        - order M: Maximum number of children an internal node can have.
        - Max keys per node = order - 1.
        - Min keys per node = ceil(order / 2) - 1.
        """
        if order < 3:
            raise ValueError("B+ Tree order must be at least 3.")

        self.order: int = order
        self.max_keys: int = order - 1
        self.min_keys: int = math.ceil(order / 2) - 1

        # Root starts as an empty leaf node
        self.root: BPlusNode = BPlusNode(is_leaf=True)
        self.size: int = 0
        self.last_search_path: List[Dict[str, Any]] = []
        self.last_split_events: List[Dict[str, Any]] = []

    def get_height(self) -> int:
        """Calculate current height of the B+ Tree (1 for root-only)."""
        h = 1
        curr = self.root
        while not curr.is_leaf:
            if curr.children:
                curr = curr.children[0]
                h += 1
            else:
                break
        return h

    def count_nodes(self) -> Tuple[int, int]:
        """Count (internal_node_count, leaf_node_count)."""
        internals = 0
        leaves = 0

        queue = [self.root]
        while queue:
            curr = queue.pop(0)
            if curr.is_leaf:
                leaves += 1
            else:
                internals += 1
                queue.extend(curr.children)

        return internals, leaves

    def search(self, product_id: str) -> Tuple[Optional[Dict[str, Any]], bool, List[Dict[str, Any]], int]:
        """
        Performs point search for a given product_id.
        Returns (record, found, search_path, comparison_count).
        """
        clean_id = str(product_id).strip().upper()
        comparisons = 0
        path: List[Dict[str, Any]] = []

        curr = self.root
        while not curr.is_leaf:
            node_desc = {
                "node_id": curr.node_id,
                "type": "Internal Node",
                "keys": list(curr.keys),
                "decision": "",
            }

            # Find the appropriate child pointer based on separator keys
            idx = 0
            while idx < len(curr.keys):
                comparisons += 1
                if clean_id < curr.keys[idx]:
                    break
                idx += 1

            if idx < len(curr.keys):
                node_desc["decision"] = f"Key '{clean_id}' < Separator '{curr.keys[idx]}' -> Navigate to Child {idx} (Node {curr.children[idx].node_id})"
            else:
                node_desc["decision"] = f"Key '{clean_id}' >= All Separators -> Navigate to Rightmost Child {idx} (Node {curr.children[idx].node_id})"

            path.append(node_desc)
            curr = curr.children[idx]

        # Now in leaf node
        leaf_desc = {
            "node_id": curr.node_id,
            "type": "Leaf Node",
            "keys": list(curr.keys),
            "decision": "",
        }

        # Search within leaf keys
        for idx, key in enumerate(curr.keys):
            comparisons += 1
            if key == clean_id:
                leaf_desc["decision"] = f"MATCH FOUND at index {idx}: Product ID '{clean_id}' in Leaf Node {curr.node_id}."
                path.append(leaf_desc)
                self.last_search_path = path
                return curr.records[idx], True, path, comparisons

        leaf_desc["decision"] = f"Key '{clean_id}' NOT FOUND in destination Leaf Node {curr.node_id}."
        path.append(leaf_desc)
        self.last_search_path = path
        return None, False, path, comparisons

    def insert(self, record: Dict[str, Any]) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Inserts a product record into the B+ Tree.
        Enforces unique Product ID policy.
        Handles leaf splitting, key copying, internal node splitting, and root creation.
        """
        product_id = str(record.get("product_id", "")).strip().upper()
        if not product_id:
            return False, "Product ID cannot be empty.", []

        # Validate duplicate key policy
        existing, found, _, _ = self.search(product_id)
        if found:
            return False, f"Product ID '{product_id}' already exists in B+ Tree index. Duplicate keys are prohibited.", []

        # Prepare normalized record
        clean_record = {
            "product_id": product_id,
            "name": str(record.get("name", "Unknown Product")).strip(),
            "category": str(record.get("category", "General")).strip(),
            "quantity": max(0, int(record.get("quantity", 0))),
            "location": str(record.get("location", "Receiving")).strip(),
            "priority": min(10, max(1, int(record.get("priority", 1)))),
            "unit_weight": max(0.1, round(float(record.get("unit_weight", 1.0)), 2)),
        }

        self.last_split_events = []

        # Insertion recursive or bottom-up
        split_result = self._insert_internal(self.root, clean_record)

        if split_result is not None:
            # Root itself split! Create a new root internal node
            promoted_key, left_child, right_child = split_result
            new_root = BPlusNode(is_leaf=False)
            new_root.keys = [promoted_key]
            new_root.children = [left_child, right_child]
            self.root = new_root

            self.last_split_events.append({
                "type": "Root Split",
                "promoted_separator": promoted_key,
                "new_root_id": new_root.node_id,
                "left_child_id": left_child.node_id,
                "right_child_id": right_child.node_id,
                "new_height": self.get_height(),
                "description": f"Root node overflowed. Created new root (Node {new_root.node_id}) with promoted separator '{promoted_key}'. Tree height increased to {self.get_height()}.",
            })

        self.size += 1
        return True, f"Product '{product_id}' successfully indexed into B+ Tree.", self.last_split_events

    def _insert_internal(
        self, curr: BPlusNode, record: Dict[str, Any]
    ) -> Optional[Tuple[str, BPlusNode, BPlusNode]]:
        """
        Helper method to recursively locate leaf and handle node overflow.
        Returns (promoted_key, left_node, right_node) if curr splits, else None.
        """
        clean_id = record["product_id"]

        if curr.is_leaf:
            # Insert into sorted position in leaf node
            insert_idx = 0
            while insert_idx < len(curr.keys) and clean_id > curr.keys[insert_idx]:
                insert_idx += 1

            curr.keys.insert(insert_idx, clean_id)
            curr.records.insert(insert_idx, record)

            # Check for leaf overflow
            if len(curr.keys) > self.max_keys:
                return self._split_leaf(curr)
            return None

        # Internal node: descend to appropriate child
        child_idx = 0
        while child_idx < len(curr.keys) and clean_id >= curr.keys[child_idx]:
            child_idx += 1

        child_split = self._insert_internal(curr.children[child_idx], record)

        if child_split is not None:
            # Child overflowed and split
            promoted_key, left_child, right_child = child_split

            # Insert promoted separator key and new right child into curr
            curr.keys.insert(child_idx, promoted_key)
            curr.children[child_idx] = left_child
            curr.children.insert(child_idx + 1, right_child)

            # Check if internal node overflows
            if len(curr.keys) > self.max_keys:
                return self._split_internal(curr)

        return None

    def _split_leaf(self, leaf: BPlusNode) -> Tuple[str, BPlusNode, BPlusNode]:
        """
        Splits an overflowing leaf node into two halves.
        Maintains linked leaf node pointers (`next` and `prev`).
        Copies up the first key of the new right leaf as separator to parent.
        """
        mid = len(leaf.keys) // 2

        new_leaf = BPlusNode(is_leaf=True)
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.records = leaf.records[mid:]

        leaf.keys = leaf.keys[:mid]
        leaf.records = leaf.records[:mid]

        # Maintain linked leaf pointers
        new_leaf.next = leaf.next
        new_leaf.prev = leaf
        if leaf.next:
            leaf.next.prev = new_leaf
        leaf.next = new_leaf

        # Separator key copied up to parent is the smallest key in right leaf
        promoted_key = new_leaf.keys[0]

        self.last_split_events.append({
            "type": "Leaf Split",
            "left_node_id": leaf.node_id,
            "right_node_id": new_leaf.node_id,
            "promoted_key": promoted_key,
            "left_keys": list(leaf.keys),
            "right_keys": list(new_leaf.keys),
            "description": f"Leaf Node {leaf.node_id} exceeded capacity {self.max_keys}. Split into Node {leaf.node_id} and Node {new_leaf.node_id}. Copied up separator '{promoted_key}' to parent and updated linked leaf pointer.",
        })

        return promoted_key, leaf, new_leaf

    def _split_internal(self, node: BPlusNode) -> Tuple[str, BPlusNode, BPlusNode]:
        """
        Splits an overflowing internal node.
        Pushes up (extracts) the middle key to parent.
        Distributes remaining keys and child pointers to left and right nodes.
        """
        mid = len(node.keys) // 2
        promoted_key = node.keys[mid]

        new_node = BPlusNode(is_leaf=False)
        new_node.keys = node.keys[mid + 1 :]
        new_node.children = node.children[mid + 1 :]

        node.keys = node.keys[:mid]
        node.children = node.children[: mid + 1]

        self.last_split_events.append({
            "type": "Internal Node Split",
            "left_node_id": node.node_id,
            "right_node_id": new_node.node_id,
            "promoted_key": promoted_key,
            "left_keys": list(node.keys),
            "right_keys": list(new_node.keys),
            "description": f"Internal Node {node.node_id} exceeded capacity {self.max_keys}. Pushed up separator '{promoted_key}' to parent, creating right internal Node {new_node.node_id}.",
        })

        return promoted_key, node, new_node

    def get_all_records_sorted(self) -> List[Dict[str, Any]]:
        """
        Retrieves all inventory records in sorted order by traversing
        linked leaf nodes directly from left to right.
        Time Complexity: O(n) linear scan without tree recursion.
        """
        records: List[Dict[str, Any]] = []

        # Find leftmost leaf
        curr = self.root
        while not curr.is_leaf:
            if curr.children:
                curr = curr.children[0]
            else:
                break

        # Traverse sequential linked list of leaf nodes
        while curr:
            records.extend(curr.records)
            curr = curr.next

        return records

    def range_query(
        self, min_product_id: str, max_product_id: str
    ) -> Dict[str, Any]:
        """
        Executes an efficient range query between min_product_id and max_product_id.
        Steps:
        1. Point search to find start leaf: O(log_M n).
        2. Follow sequential `next` leaf pointers collecting records: O(K).
        Total Complexity: O(log_M n + K) where K is number of records matched.
        """
        clean_min = str(min_product_id).strip().upper()
        clean_max = str(max_product_id).strip().upper()

        if clean_min > clean_max:
            clean_min, clean_max = clean_max, clean_min

        # 1. Point search to find the leaf containing clean_min or where it would start
        curr = self.root
        path_to_start: List[int] = []

        while not curr.is_leaf:
            path_to_start.append(curr.node_id)
            idx = 0
            while idx < len(curr.keys) and clean_min >= curr.keys[idx]:
                idx += 1
            curr = curr.children[idx]

        path_to_start.append(curr.node_id)

        # 2. Sequential scan through linked leaves
        matched_records: List[Dict[str, Any]] = []
        leaves_traversed: List[int] = []

        leaf = curr
        done = False

        while leaf and not done:
            leaves_traversed.append(leaf.node_id)
            for rec in leaf.records:
                pid = rec["product_id"]
                if clean_min <= pid <= clean_max:
                    matched_records.append(rec)
                elif pid > clean_max:
                    done = True
                    break
            leaf = leaf.next

        return {
            "success": True,
            "min_id": clean_min,
            "max_id": clean_max,
            "count": len(matched_records),
            "records": matched_records,
            "start_leaf_id": curr.node_id,
            "leaves_traversed_count": len(leaves_traversed),
            "leaves_traversed_ids": leaves_traversed,
            "search_path_node_ids": path_to_start,
            "algorithm": "B+ Tree Linked Leaf Range Scan",
            "complexity": f"O(log_{self.order} n + K) where K = {len(matched_records)}",
        }

    def to_tree_hierarchy(self) -> Dict[str, Any]:
        """
        Constructs a complete hierarchical dictionary of the entire tree
        for visualization, including levels, node classifications, and leaf links.
        """
        levels: List[List[Dict[str, Any]]] = []

        # Level-order BFS traversal
        curr_level = [self.root]
        level_idx = 0

        while curr_level:
            level_data = []
            next_level = []

            for node in curr_level:
                node_dict = node.to_dict()
                node_dict["tree_level"] = level_idx
                level_data.append(node_dict)

                if not node.is_leaf:
                    next_level.extend(node.children)

            levels.append(level_data)
            curr_level = next_level
            level_idx += 1

        # Collect leaf linked chain
        leaf_chain: List[int] = []
        curr = self.root
        while not curr.is_leaf:
            if curr.children:
                curr = curr.children[0]
            else:
                break
        while curr:
            leaf_chain.append(curr.node_id)
            curr = curr.next

        internals, leaves = self.count_nodes()

        return {
            "order": self.order,
            "max_keys": self.max_keys,
            "min_keys": self.min_keys,
            "height": self.get_height(),
            "total_records": self.size,
            "internal_nodes_count": internals,
            "leaf_nodes_count": leaves,
            "levels": levels,
            "leaf_chain_ids": leaf_chain,
            "root_node_id": self.root.node_id,
        }

    @classmethod
    def from_records(cls, records: List[Dict[str, Any]], order: int = 4) -> "BPlusTree":
        """Instantiate and bulk populate a B+ Tree from a list of records."""
        tree = cls(order=order)
        for rec in records:
            tree.insert(rec)
        return tree
