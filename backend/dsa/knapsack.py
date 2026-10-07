"""
0/1 Knapsack Dynamic Programming for Warehouse Dispatch Optimization.

Academic Purpose:
Selects the optimal subset of inventory items to load into a picking cart
or dispatch vehicle with limited weight capacity (W) to maximize total
cargo priority/value.
Each item is discrete (0/1 decision: either packed or left behind).

Recurrence Relation:
dp[i][w] = dp[i-1][w]                                    if weight[i-1] > w
dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i-1]] + val[i-1]) if weight[i-1] <= w

Time Complexity: O(n * W)
Space Complexity: O(n * W)
"""

from typing import List, Dict, Any, Tuple


def solve_01_knapsack(items: List[Dict[str, Any]], capacity: int) -> Dict[str, Any]:
    """
    Solve the 0/1 Knapsack problem using a 2D Dynamic Programming table.
    Includes item backtracking and full DP table visualization.
    """
    if capacity < 0:
        raise ValueError("Capacity cannot be negative.")

    n = len(items)

    # Edge cases: 0 capacity or 0 items
    if n == 0 or capacity == 0:
        return {
            "max_value": 0,
            "total_weight": 0,
            "capacity": capacity,
            "selected_items": [],
            "dp_table": [[0] * (capacity + 1)],
            "capacities_header": list(range(capacity + 1)),
            "item_labels": ["No Items"],
            "decision_steps": ["Capacity is 0 or no items available."],
            "complexity": f"O(n · W) = O({n} × {capacity}) operations",
        }

    # Validate items
    weights: List[int] = []
    values: List[int] = []
    names: List[str] = []

    for idx, item in enumerate(items):
        wt = int(item.get("weight", 0))
        val = int(item.get("value", 0))
        name = str(item.get("name", f"Item-{idx+1}"))
        if wt <= 0:
            raise ValueError(f"Item '{name}' weight must be a positive integer (got {wt}).")
        if val < 0:
            raise ValueError(f"Item '{name}' value cannot be negative.")
        weights.append(wt)
        values.append(val)
        names.append(name)

    # Construct DP table: (n + 1) rows x (capacity + 1) columns
    # dp[i][w] stores max value using subset of first i items with capacity w
    dp: List[List[int]] = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt_i = weights[i - 1]
        val_i = values[i - 1]
        for w in range(capacity + 1):
            if wt_i <= w:
                include_val = dp[i - 1][w - wt_i] + val_i
                exclude_val = dp[i - 1][w]
                dp[i][w] = max(exclude_val, include_val)
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtracking to identify selected items
    selected_items: List[Dict[str, Any]] = []
    current_w = capacity
    decision_steps: List[str] = []

    for i in range(n, 0, -1):
        # If value is different from row above, item i-1 was included
        if dp[i][current_w] != dp[i - 1][current_w]:
            item_obj = {
                "name": names[i - 1],
                "weight": weights[i - 1],
                "value": values[i - 1],
                "status": "Selected (1)",
            }
            selected_items.append(item_obj)
            decision_steps.append(
                f"Selected '{names[i - 1]}' (Weight: {weights[i - 1]}, Value: {values[i - 1]}) because dp[{i}][{current_w}] ({dp[i][current_w]}) > dp[{i-1}][{current_w}] ({dp[i-1][current_w]})."
            )
            current_w -= weights[i - 1]
        else:
            decision_steps.append(
                f"Skipped '{names[i - 1]}' (Weight: {weights[i - 1]}) because dp[{i}][{current_w}] == dp[{i-1}][{current_w}] ({dp[i][current_w]})."
            )

    selected_items.reverse()
    decision_steps.reverse()

    total_weight = sum(it["weight"] for it in selected_items)
    max_value = dp[n][capacity]

    # Create formatted DP table for UI display
    item_labels = ["0: Base State (No Items)"] + [
        f"{idx+1}: {names[idx]} (w={weights[idx]}, v={values[idx]})"
        for idx in range(n)
    ]

    return {
        "max_value": max_value,
        "total_weight": total_weight,
        "capacity": capacity,
        "selected_items": selected_items,
        "unselected_items_count": n - len(selected_items),
        "dp_table": dp,
        "capacities_header": list(range(capacity + 1)),
        "item_labels": item_labels,
        "decision_steps": decision_steps,
        "complexity": f"O(n · W) = O({n} × {capacity}) operations",
    }
