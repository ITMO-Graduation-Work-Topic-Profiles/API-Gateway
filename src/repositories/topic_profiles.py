import typing as tp

from motor.motor_asyncio import AsyncIOMotorDatabase

__all__ = [
    "upsert_topic_profile_repository",
]


async def upsert_topic_profile_repository(
    data: dict[str, tp.Any],
    *,
    database: AsyncIOMotorDatabase[tp.Any],
) -> None:
    if "user_id" not in data:
        raise ValueError("Missing user_id in data")

    await database["topic_profiles"].update_one(
        {"user_id": data["user_id"]},
        {"$set": data},
        upsert=True,
    )
