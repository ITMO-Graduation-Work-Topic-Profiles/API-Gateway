import typing as tp

from fastapi_pagination import Params
from fastapi_pagination.ext.motor import apaginate_aggregate
from fastapi_pagination.types import AsyncItemsTransformer
from motor.motor_asyncio import AsyncIOMotorDatabase

__all__ = [
    "get_users_with_topic_info_paginated_repository",
    "get_user_with_topic_info_repository",
    "get_user_repository",
    "insert_user_repository",
]


def build_get_users_with_topic_info_pipeline(
    keywords: tp.Sequence[str] = (),
    entities: tp.Sequence[str] = (),
    sentiments: tp.Sequence[str] = (),
) -> list[dict[str, tp.Any]]:
    keywords = list(keywords)
    entities = list(entities)
    sentiments = list(sentiments)

    pipeline: list[dict[str, tp.Any]] = []

    pipeline.append(
        {
            "$lookup": {
                "from": "aggregated_topic_attributes",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "aggregated_topic_attributes",
            }
        }
    )
    pipeline.append(
        {
            "$lookup": {
                "from": "topic_profiles",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "topic_profile",
            }
        }
    )

    pipeline.append(
        {
            "$unwind": {
                "path": "$aggregated_topic_attributes",
                "preserveNullAndEmptyArrays": True,
            },
        },
    )

    pipeline.append(
        {
            "$unwind": {
                "path": "$topic_profile",
                "preserveNullAndEmptyArrays": True,
            },
        },
    )

    match_stage: dict[str, tp.Any] = {}
    if keywords:
        match_stage["aggregated_topic_attributes.keywords.name"] = {"$in": keywords}
    if entities:
        match_stage["aggregated_topic_attributes.entities.name"] = {"$in": entities}
    if sentiments:
        match_stage["aggregated_topic_attributes.sentiments.name"] = {"$in": sentiments}

    if match_stage:
        pipeline.append(
            {
                "$match": match_stage,
            }
        )

    pipeline.append(
        {
            "$addFields": {
                "maxKeywordWeight": {
                    "$max": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$aggregated_topic_attributes.keywords",
                                    "as": "t",
                                    "cond": {"$in": ["$$t.name", keywords]},
                                }
                            },
                            "as": "t",
                            "in": "$$t.weight",
                        }
                    }
                },
                "maxEntityWeight": {
                    "$max": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$aggregated_topic_attributes.entities",
                                    "as": "e",
                                    "cond": {"$in": ["$$e.name", entities]},
                                }
                            },
                            "as": "e",
                            "in": "$$e.weight",
                        }
                    }
                },
                "maxSentimentWeight": {
                    "$max": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$aggregated_topic_attributes.sentiments",
                                    "as": "s",
                                    "cond": {"$in": ["$$s.name", sentiments]},
                                }
                            },
                            "as": "s",
                            "in": "$$s.weight",
                        }
                    },
                },
            },
        }
    )

    pipeline.append(
        {
            "$sort": {
                "maxKeywordWeight": -1,
                "maxEntityWeight": -1,
                "maxSentimentWeight": -1,
            },
        }
    )

    return pipeline


async def get_users_with_topic_info_paginated_repository(
    *,
    database: AsyncIOMotorDatabase[tp.Any],
    params: Params,
    transformer: AsyncItemsTransformer | None = None,
    **pipeline_kwargs: tp.Any,
) -> tp.Any:
    return await apaginate_aggregate(
        database["users"],
        build_get_users_with_topic_info_pipeline(**pipeline_kwargs),
        params,
        transformer=transformer,
    )


def build_get_user_with_topic_info_pipeline(
    user_id: str,
) -> list[dict[str, tp.Any]]:
    pipeline: list[dict[str, tp.Any]] = []

    pipeline.append(
        {"$match": {"user_id": user_id}},
    )
    pipeline.append(
        {
            "$lookup": {
                "from": "aggregated_topic_attributes",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "aggregated_topic_attributes",
            }
        },
    )
    pipeline.append(
        {
            "$unwind": {
                "path": "$aggregated_topic_attributes",
                "preserveNullAndEmptyArrays": True,
            },
        },
    )

    return pipeline


async def get_user_with_topic_info_repository(
    *,
    database: AsyncIOMotorDatabase[tp.Any],
    **pipeline_kwargs: tp.Any,
) -> dict[str, tp.Any] | None:
    pipeline = build_get_user_with_topic_info_pipeline(**pipeline_kwargs)
    result = await database["users"].aggregate(pipeline).to_list(1)
    return result[0] if result else None


async def get_user_repository(
    user_id: str,
    *,
    database: AsyncIOMotorDatabase[tp.Any],
) -> dict[str, tp.Any] | None:
    result = await database["users"].find_one({"user_id": user_id})
    return result


async def insert_user_repository(
    data: tp.Mapping[str, tp.Any],
    *,
    database: AsyncIOMotorDatabase[tp.Any],
) -> None:
    await database["users"].insert_one(data)
