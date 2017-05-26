try:
    from functools import lru_cache
except ImportError:
    def lru_cache(*args, **kwargs):
        def decorator(f):
            return f
        return decorator
