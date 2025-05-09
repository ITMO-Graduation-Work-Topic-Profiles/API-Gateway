import typing as tp

from fastapi_pagination import Params
from fastapi_pagination.ext.motor import apaginate_aggregate
from fastapi_pagination.types import AsyncItemsTransformer
from motor.motor_asyncio import AsyncIOMotorDatabase

__all__ = ["get_users_repository"]


def build_get_users_pipeline(
    keywords: list[str] | None = None,
    entities: list[str] | None = None,
    sentiment: str | None = None,
) -> list[dict[str, tp.Any]]:
    keywords = keywords or []
    entities = entities or []

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

    match_filter: dict[str, tp.Any] = {}
    if keywords:
        match_filter["topic_profile.keywords.name"] = {"$in": keywords}
    if entities:
        match_filter["topic_profile.entities.name"] = {"$in": entities}
    if sentiment:
        match_filter[f"topic_profile.sentiment.{sentiment}"] = {"$exists": True}

    if match_filter:
        pipeline.append(
            {
                "$match": match_filter,
            }
        )

    pipeline.append(
        {
            "$addFields": {
                "maxTopicWeight": {
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
                "sentimentScore": (
                    sentiment
                    and f"$topic_profile.sentiment.{sentiment}"
                    or {
                        "$max": [
                            "$topic_profile.sentiment.positive",
                            "$topic_profile.sentiment.neutral",
                            "$topic_profile.sentiment.negative",
                        ]
                    }
                ),
            }
        }
    )

    pipeline.append(
        {
            "$sort": {
                "maxTopicWeight": -1,
                "maxEntityWeight": -1,
                "sentimentScore": -1,
            },
        }
    )

    return pipeline


async def get_users_repository(
    mongo_database: AsyncIOMotorDatabase[tp.Any],
    params: Params,
    transformer: AsyncItemsTransformer | None = None,
    **kwargs: tp.Any,
) -> tp.Any:
    return await apaginate_aggregate(
        mongo_database["topic_profiles"],
        build_get_users_pipeline(**kwargs),
        params,
        transformer=transformer,
    )
