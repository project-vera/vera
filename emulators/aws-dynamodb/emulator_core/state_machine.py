"""
DynamoDB table state machine.

Tracks table lifecycle in memory:
  CREATING -> ACTIVE -> UPDATING -> ACTIVE
                     -> DELETING  (terminal)

On startup, existing tables from DynamoDB Local are imported as ACTIVE.
All data lives in DynamoDB Local; vera only tracks table_status.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger("DynamoDBStateMachine")

# Valid transitions: current_status -> set of allowed next statuses
_TRANSITIONS = {
    "CREATING":  {"ACTIVE", "DELETING"},
    "ACTIVE":    {"UPDATING", "DELETING"},
    "UPDATING":  {"ACTIVE", "DELETING"},
    "DELETING":  set(),  # terminal
}

# Operations blocked per status
_BLOCKED = {
    # table_status -> set of blocked actions
    "CREATING":  {"DeleteTable", "UpdateTable"},
    "DELETING":  {"DeleteTable", "UpdateTable", "CreateTable"},
    "UPDATING":  {"DeleteTable"},
}


class TableStateMachine:
    """In-memory state tracker for DynamoDB tables."""

    def __init__(self):
        # table_name -> status string
        self._tables: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Sync from DynamoDB Local on startup
    # ------------------------------------------------------------------

    def import_existing(self, table_names: list[str]) -> None:
        """Register tables already present in DynamoDB Local as ACTIVE."""
        for name in table_names:
            if name not in self._tables:
                self._tables[name] = "ACTIVE"
                logger.info(f"Imported existing table: {name} -> ACTIVE")

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def get_status(self, table_name: str) -> Optional[str]:
        return self._tables.get(table_name)

    def exists(self, table_name: str) -> bool:
        status = self._tables.get(table_name)
        return status is not None and status != "DELETING"

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def check_action(self, action: str, table_name: str) -> Optional[str]:
        """
        Return an error message string if the action is blocked,
        or None if the action is allowed.
        """
        status = self._tables.get(table_name)

        if action == "CreateTable":
            if status is not None and status != "DELETING":
                return f"Table already exists: {table_name}"
            return None

        if status is None:
            return f"Table not found: {table_name}"

        blocked = _BLOCKED.get(status, set())
        if action in blocked:
            return (
                f"Table {table_name} is in state {status}, "
                f"which does not allow {action}"
            )
        return None

    # ------------------------------------------------------------------
    # Transitions
    # ------------------------------------------------------------------

    def transition(self, table_name: str, new_status: str) -> None:
        current = self._tables.get(table_name)
        allowed = _TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition for {table_name}: {current} -> {new_status}"
            )
        self._tables[table_name] = new_status
        logger.info(f"Table {table_name}: {current} -> {new_status}")

    def register(self, table_name: str, status: str = "CREATING") -> None:
        """Register a brand-new table."""
        self._tables[table_name] = status
        logger.info(f"Registered table {table_name} as {status}")

    def remove(self, table_name: str) -> None:
        """Remove a table from tracking (after DELETING is confirmed)."""
        self._tables.pop(table_name, None)
        logger.info(f"Removed table {table_name} from state machine")
