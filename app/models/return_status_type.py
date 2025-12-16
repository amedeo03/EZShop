from enum import Enum

class ReturnStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    REIMBURSED = "Reimbursed"