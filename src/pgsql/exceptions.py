class QueryError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ResourceNotFoundError(QueryError):
    def __init__(self, *args):
        super().__init__(*args)

class ResourceConflictError(QueryError):
    def __init__(self, *args):
        super().__init__(*args)