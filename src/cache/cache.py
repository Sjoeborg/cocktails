import redis

r = redis.Redis(host='localhost', port=7777)


def start_redis_client(host: str = 'localhost', port: int = 6379) -> redis.Redis:
    return redis.Redis(host=host, port=port)


def get(key: str, client: redis.Redis) -> str | None:
    if client.exists(key):
        return client.get(key)
    else:
        return None


def set(key: str, value: str, client: redis.Redis) -> None:
    client.set(key, value)
