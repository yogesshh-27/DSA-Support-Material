"""
Pydantic Schemas for Request Validation and Response Typing.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class InventoryItemSchema(BaseModel):
    sku: str = Field(..., description="Unique Stock Keeping Unit, e.g. SKU001")
    name: str = Field(..., description="Item Name")
    category: str = Field(..., description="Product Category")
    quantity: int = Field(..., ge=0, description="In-stock Quantity")
    location: str = Field(..., description="Storage rack/zone location")
    priority: int = Field(..., ge=1, le=10, description="Handling priority (1 to 10)")


class AlertSchema(BaseModel):
    sku: str = Field(..., description="Item SKU associated with alert")
    alert_type: str = Field(..., description="Alert category: Critical Stock, Low Stock, etc.")
    priority: int = Field(..., ge=1, le=10, description="Alert Priority (1-10)")
    quantity: int = Field(..., ge=0, description="Current quantity")
    location: str = Field(..., description="Warehouse location")


class DijkstraRequest(BaseModel):
    source_id: int = Field(..., ge=0, description="Source vertex ID")
    dest_id: int = Field(..., ge=0, description="Destination vertex ID")


class PrimRequest(BaseModel):
    start_node_id: int = Field(0, ge=0, description="Root vertex ID to start Prim's algorithm")


class FloydWarshallQueryRequest(BaseModel):
    source_id: int = Field(..., ge=0, description="Source vertex ID")
    dest_id: int = Field(..., ge=0, description="Destination vertex ID")


class KnapsackItemSchema(BaseModel):
    name: str = Field(..., description="Item description")
    weight: int = Field(..., gt=0, description="Positive weight in kilograms/units")
    value: int = Field(..., ge=0, description="Priority or monetary value")


class KnapsackRequest(BaseModel):
    items: List[KnapsackItemSchema]
    capacity: int = Field(..., ge=0, description="Maximum weight limit of cart/dispatch bay")


class GraphEdgeSchema(BaseModel):
    u: int = Field(..., ge=0, description="Source node ID")
    v: int = Field(..., ge=0, description="Destination node ID")
    weight: float = Field(..., ge=0.0, description="Movement cost or distance")


class GraphVertexSchema(BaseModel):
    id: int = Field(..., ge=0, description="Unique node ID")
    name: str = Field(..., description="Location name")
    x: Optional[int] = Field(0, description="Visualization X coordinate")
    y: Optional[int] = Field(0, description="Visualization Y coordinate")
