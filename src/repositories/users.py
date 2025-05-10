import typing as tp

from fastapi_pagination import Params
from fastapi_pagination.ext.motor import apaginate_aggregate
from fastapi_pagination.types import AsyncItemsTransformer
from motor.motor_asyncio import AsyncIOMotorDatabase

__all__ = ["get_users_with_topic_profiles_paginated_repository"]


def build_get_users_with_topic_profiles_pipeline(
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
                "from": "topic_profiles",
                "localField": "user_id",
                "foreignField": "user_id",
                "as": "topic_profile",
            }
        }
    )

    pipeline.append({"$unwind": "$topic_profile"})

    match_stage: dict[str, tp.Any] = {}
    if keywords:
        match_stage["topic_profile.keywords.name"] = {"$in": keywords}
    if entities:
        match_stage["topic_profile.entities.name"] = {"$in": entities}
    if sentiments:
        match_stage["topic_profile.sentiments.name"] = {"$in": sentiments}

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
                                    "input": "$topic_profile.keywords",
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
                                    "input": "$topic_profile.entities",
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
                                    "input": "$topic_profile.sentiments",
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


async def get_users_with_topic_profiles_paginated_repository(
    *,
    database: AsyncIOMotorDatabase[tp.Any],
    params: Params,
    transformer: AsyncItemsTransformer | None = None,
    **pipeline_kwargs: tp.Any,
) -> tp.Any:
    return await apaginate_aggregate(
        database["users"],
        build_get_users_with_topic_profiles_pipeline(**pipeline_kwargs),
        params,
        transformer=transformer,
    )
