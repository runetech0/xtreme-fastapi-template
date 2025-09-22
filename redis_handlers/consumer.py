import asyncio
import json
from typing import TypeVar

from redis.asyncio import Redis

from app.logs_config import get_logger

logger = get_logger()

T = TypeVar("T")


class Consumer:
    def __init__(
        self,
        redis: Redis,
        stream_name: str,
        group_name: str,
        output_queue: asyncio.Queue[T],
        worker_number: int = 1,
    ) -> None:
        self.redis = redis
        self.stream_name = stream_name
        self.group_name = group_name
        self.worker_name = f"worker-{worker_number}"
        self.output_queue = output_queue

    async def consume(self) -> None:
        # Create consumer group (ignore error if it already exists)
        try:
            logger.info(
                f"Creating consumer group {self.group_name} for stream {self.stream_name}"
            )
            await self.redis.xgroup_create(
                self.stream_name, self.group_name, id="$", mkstream=True
            )
        except Exception:
            # Group might already exist, that's fine
            pass

        while True:
            messages = await self.redis.xreadgroup(
                self.group_name,
                self.worker_name,
                {self.stream_name: ">"},
                count=1,
            )
            for stream_name, stream_messages in messages:
                for message_id, fields in stream_messages:
                    logger.info(
                        f"Received message {message_id}: {fields} in {stream_name}"
                    )
                    # Acknowledge the message
                    await self.redis.xack(self.stream_name, self.group_name, message_id)

                    payload = json.loads(fields[b"payload"])
                    await self.output_queue.put(payload)
