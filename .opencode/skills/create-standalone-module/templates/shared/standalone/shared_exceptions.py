class NotFoundError(Exception):
    def __init__(self, resource: str = "Resource", identifier: int | str | None = None):
        msg = f"{resource} not found"
        if identifier is not None:
            msg += f": {identifier}"
        super().__init__(msg)


class ConflictError(Exception):
    pass
