class DeliveryError(Exception):
    """Expected failure of one request: logged in the trace, scenario continues."""
    MOTIF = ""

    def __init__(self, detail: str = ""):
        super().__init__(f"{self.MOTIF}: {detail}" if detail else self.MOTIF)
        self.detail = detail


class UndeterminedEmotionError(DeliveryError):
    MOTIF = "emotion indeterminee"

class EmptyWardrobeError(DeliveryError):
    MOTIF = "armoire vide"

class UnreachableResidentError(DeliveryError):
    MOTIF = "resident inaccessible"
