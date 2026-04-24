"""Utility functions for the backend."""
from bson import ObjectId
from typing import Optional


def object_id_to_str(obj_id) -> str:
    """Convert ObjectId to string for JSON serialization.
    
    Args:
        obj_id: ObjectId or string
        
    Returns:
        String representation of the ID
    """
    if isinstance(obj_id, ObjectId):
        return str(obj_id)
    return obj_id


def str_to_object_id(id_str: str) -> Optional[ObjectId]:
    """Convert string to ObjectId if valid, otherwise return None.
    
    Args:
        id_str: String ID
        
    Returns:
        ObjectId if valid, None otherwise
    """
    try:
        return ObjectId(id_str)
    except Exception:
        return None

