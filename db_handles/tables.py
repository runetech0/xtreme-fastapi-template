from sqlalchemy import Column, ForeignKey, Integer, Table

from .base import Base

user_follow_targets = Table(
    "user_follow_targets",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column(
        "follow_target_id", Integer, ForeignKey("follow_targets.id"), primary_key=True
    ),
)


user_tweet_targets = Table(
    "user_tweet_targets",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column(
        "tweet_target_id", Integer, ForeignKey("tweet_targets.id"), primary_key=True
    ),
)
