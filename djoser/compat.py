try:
    from functools import lru_cache
except ImportError:
    def lru_cache(*args, **kwargs):
        def decorator(f):
            f.cache_clear = lambda: None
            return f
        return decorator
