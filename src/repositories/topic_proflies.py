import typing as tp

from motor.motor_asyncio import AsyncIOMotorDatabase

__all__ = [
    "get_topic_profile_repository",
    "upsert_topic_profile_repository",
]


async def get_topic_profile_repository(
    user_id: str,
    *,
    database: AsyncIOMotorDatabase[tp.Any],
) -> dict[str, tp.Any] | None:
    document = await database["topic_profiles"].find_one({"user_id": user_id})

    return document or None


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
