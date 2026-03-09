from typing import Dict, Optional, List, Union, Any

cdef class Key_cython:
    cdef public str value

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Key_cython) and self.value == other.value

    def __repr__(self):
        return f"Key_cython({self.value})"

    def __hash__(self):
        """
        Creates a "fingerprint" number for this Key so Python can use it efficiently.
        
        **Why is this needed?**
        Python needs to be able to quickly compare keys and store them in dictionaries.
        This method converts your key value into a number (hash) for fast lookups.
        
        **Special handling:**
        - Lists get converted to tuples (because lists can change, tuples can't)
        - This ensures your key works even if you use complex data structures
        """
        # Ensure value is hashable or convert to a hashable type
        if isinstance(self.value, (list, dict)):
            # Example: convert list to tuple for hashing
            return hash(tuple(self.value))
        return hash(self.value)

    def __str_key__(self):
        return self.value

    def __str__(self):
        return self.value

