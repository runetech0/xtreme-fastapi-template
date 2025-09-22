import datetime
import enum
import json
from typing import Any, Mapping

from redis.asyncio import Redis
from redis.typing import EncodableT, FieldT


class Dispatcher:
    @staticmethod
    def to_redis_fields(
        payload: Mapping[str, Any],
    ) -> dict[FieldT, EncodableT]:
        """
        Convert a dict-like payload into Redis-safe fields for XADD/HSET/etc.
        - str, int, float, bytes → kept as-is
        - bool → "1"/"0"
        - Enum → its value (if str/int) else its name
        - datetime/date → ISO 8601 string
        - dict/list/other → JSON string
        """
        out: dict[FieldT, EncodableT] = {}

        for k, v in payload.items():
            if v is None:
                continue  # skip None fields (or store as "")
            elif isinstance(v, (str, int, float, bytes)):
                out[k] = v
            elif isinstance(v, bool):
                out[k] = "1" if v else "0"
            elif isinstance(v, enum.Enum):
                out[k] = v.value if isinstance(v.value, (str, int, float)) else v.name
            elif isinstance(v, (datetime.date, datetime.datetime)):
                out[k] = v.isoformat()
            else:
                out[k] = json.dumps(v, separators=(",", ":"), ensure_ascii=True)

        return out

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def dispatch(self, stream_name: str, payload: str) -> None:
        await self.redis.xadd(stream_name, {"payload": payload})
