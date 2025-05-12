import typing as tp

from motor.motor_asyncio import AsyncIOMotorDatabase

__all__ = [
    "get_aggregated_topic_attributes_repository",
    "upsert_aggregated_topic_attributes_repository",
]


async def get_aggregated_topic_attributes_repository(
    user_id: str,
    *,
    database: AsyncIOMotorDatabase[tp.Any],
) -> dict[str, tp.Any] | None:
    document = await database["aggregated_topic_attributes"].find_one(
        {"user_id": user_id}
    )

    return document or None


async def upsert_aggregated_topic_attributes_repository(
    data: dict[str, tp.Any],
    *,
    database: AsyncIOMotorDatabase[tp.Any],
) -> None:
    if "user_id" not in data:
        raise ValueError("Missing user_id in data")

    await database["aggregated_topic_attributes"].update_one(
        {"user_id": data["user_id"]},
        {"$set": data},
        upsert=True,
    )
