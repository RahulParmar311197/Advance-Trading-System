class KillSwitch:
    def __init__(self): self._active=False
    def activate(self): self._active=True
    def deactivate(self): self._active=False
    @property
    def active(self): return self._active
    def allow_new_trade(self): return not self._active
