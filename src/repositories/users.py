import typing as tp

from fastapi_pagination import Params
from fastapi_pagination.ext.motor import apaginate_aggregate
from fastapi_pagination.types import AsyncItemsTransformer
from motor.motor_asyncio import AsyncIOMotorDatabase

__all__ = ["get_users_repository"]


def build_get_users_pipeline(
    topics: list[str] | None = None,
    entities: list[str] | None = None,
    sentiment: str | None = None,
) -> list[dict[str, tp.Any]]:
    match_stage = {"$match": {}}  # type: ignore[var-annotated]
    if topics:
        match_stage["$match"]["topics"] = {"$in": topics}
    if entities:
        match_stage["$match"]["entities"] = {"$in": entities}
    if sentiment:
        match_stage["$match"][f"sentiment.{sentiment}"] = {"$exists": True}

    add_fields_stage = {
        "$addFields": {
            "maxTopicWeight": {
                "$max": {
                    "$map": {
                        "input": {
                            "$filter": {
                                "input": "$topics",
                                "as": "t",
                                "cond": {"$in": ["$$t.name", topics or []]},
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
                                "input": "$entities",
                                "as": "e",
                                "cond": {"$in": ["$$e.name", entities or []]},
                            }
                        },
                        "as": "e",
                        "in": "$$e.weight",
                    }
                }
            },
            "maxSentimentWeight": (
                {
                    "$ifNull": [
                        f"$sentiment.{sentiment}",
                        {
                            "$max": [
                                "$sentiment.positive",
                                "$sentiment.neutral",
                                "$sentiment.negative",
                            ]
                        },
                    ]
                }
            ),
        }
    }

    sort_stage = {
        "$sort": {"maxTopicWeight": -1, "maxEntityWeight": -1, "maxSentimentWeight": -1}
    }

    pipeline = [
        match_stage,
        add_fields_stage,
        sort_stage,
    ]

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
