import copy
import typing as tp

from src.dtos import TopicEventBrokerDTO
from src.schemas import (
    EntityTopicEventSchema,
    EntityTopicProfileSchema,
    KeywordTopicEventSchema,
    KeywordTopicProfileSchema,
    SentimentTopicEventSchema,
    SentimentTopicProfileSchema,
    TopicAttributesSchema,
)
from src.utils.dates import utcnow
from src.utils.weights import recalculate_weight

__all__ = [
    "update_topic_attributes_schema_based_on_topic_event_schema",
]


def build_key_from_item_fields(
    key_fields: tp.Sequence[str],
    item: tp.Mapping[str, tp.Any],
) -> tuple[tp.Hashable, ...]:
    return tuple(item[field] for field in key_fields)


def merge_weighted_item_lists(
    existing_item_list: tp.Sequence[tp.Mapping[str, tp.Any]],
    incoming_item_list: tp.Sequence[tp.Mapping[str, tp.Any]],
    *,
    key_fields: tp.Sequence[str],
    weight_field: str,
    timestamp_field: str,
    limit: int,
    alpha: float,
) -> list[dict[str, tp.Any]]:
    existing_item_list = list(copy.deepcopy(existing_item_list))
    incoming_item_list = list(copy.deepcopy(incoming_item_list))

    new_timestamp_value = utcnow()
    merged_item_list: list[dict[str, tp.Any]] = []
    new_keys: set[tuple[tp.Hashable, ...]] = set()
    old_items_by_key = {
        build_key_from_item_fields(key_fields, item): item
        for item in existing_item_list
    }

    # Merge intersecting items or add a new one to `merged_item_list`
    for new_item in incoming_item_list:
        new_key = build_key_from_item_fields(key_fields, new_item)
        new_keys.add(new_key)
        if new_key in old_items_by_key:
            old_item = old_items_by_key[new_key]

            merged_item = dict(old_item)
            merged_item.update(
                {k: v for k, v in new_item.items() if k not in merged_item}
            )
            merged_item[weight_field] = recalculate_weight(
                merged_item[weight_field],
                new_item[weight_field],
                alpha=alpha,
            )
        else:
            merged_item = dict(new_item)
        merged_item[timestamp_field] = new_timestamp_value
        merged_item_list.append(merged_item)

    # Add old non-intersecting items to `merged_item_list`
    for old_key, old_item in old_items_by_key.items():
        if old_key not in new_keys:
            merged_item_list.append(dict(old_item))

    merged_item_list.sort(key=lambda item: item[weight_field], reverse=True)
    merged_item_list = merged_item_list[:limit]

    return merged_item_list


def merge_keywords(
    existing_keywords: tp.Sequence[tp.Mapping[str, tp.Any]],
    incoming_keywords: tp.Sequence[tp.Mapping[str, tp.Any]],
) -> list[dict[str, tp.Any]]:
    return merge_weighted_item_lists(
        existing_keywords,
        incoming_keywords,
        key_fields=("name",),
        weight_field="weight",
        timestamp_field="updated_at",
        limit=50,
        alpha=0.8,
    )


def merge_entities(
    existing_entities: tp.Sequence[tp.Mapping[str, tp.Any]],
    incoming_entities: tp.Sequence[tp.Mapping[str, tp.Any]],
) -> list[dict[str, tp.Any]]:
    return merge_weighted_item_lists(
        existing_entities,
        incoming_entities,
        key_fields=("category", "name"),
        weight_field="weight",
        timestamp_field="updated_at",
        limit=50,
        alpha=0.8,
    )


def merge_sentiment(
    existing_sentiment: tp.Sequence[tp.Mapping[str, tp.Any]],
    incoming_sentiment: tp.Sequence[tp.Mapping[str, tp.Any]],
) -> list[dict[str, tp.Any]]:
    return merge_weighted_item_lists(
        existing_sentiment,
        incoming_sentiment,
        key_fields=("name",),
        weight_field="weight",
        timestamp_field="updated_at",
        limit=50,
        alpha=0.8,
    )


def merge_keywords_schemas(
    existing_keywords: tp.Sequence[KeywordTopicProfileSchema],
    incoming_keywords: tp.Sequence[KeywordTopicEventSchema],
) -> list[KeywordTopicProfileSchema]:
    return list(
        map(
            KeywordTopicProfileSchema.model_validate,
            merge_keywords(
                [kw.model_dump() for kw in existing_keywords],
                [kw.model_dump() for kw in incoming_keywords],
            ),
        )
    )


def merge_entities_schemas(
    existing_entities: tp.Sequence[EntityTopicProfileSchema],
    incoming_entities: tp.Sequence[EntityTopicEventSchema],
) -> list[EntityTopicProfileSchema]:
    return list(
        map(
            EntityTopicProfileSchema.model_validate,
            merge_entities(
                [et.model_dump() for et in existing_entities],
                [et.model_dump() for et in incoming_entities],
            ),
        )
    )


def merge_sentiment_schemas(
    existing_sentiment: tp.Sequence[SentimentTopicProfileSchema],
    incoming_sentiment: tp.Sequence[SentimentTopicEventSchema],
) -> list[SentimentTopicProfileSchema]:
    return list(
        map(
            SentimentTopicProfileSchema.model_validate,
            merge_sentiment(
                [st.model_dump() for st in existing_sentiment],
                [st.model_dump() for st in incoming_sentiment],
            ),
        )
    )


def update_topic_attributes_schema_based_on_topic_event_schema(
    existing_topic_profile: TopicAttributesSchema,
    incoming_topic_event: TopicEventBrokerDTO,
) -> TopicAttributesSchema:
    new_timestamp_value = utcnow()
    new_topic_profile_schema = TopicAttributesSchema.model_validate(
        existing_topic_profile.model_dump()
    )

    new_topic_profile_schema.keywords = merge_keywords_schemas(
        existing_topic_profile.keywords,
        incoming_topic_event.keywords,
    )
    new_topic_profile_schema.entities = merge_entities_schemas(
        existing_topic_profile.entities,
        incoming_topic_event.entities,
    )
    new_topic_profile_schema.sentiments = merge_sentiment_schemas(
        existing_topic_profile.sentiments,
        incoming_topic_event.sentiments,
    )
    new_topic_profile_schema.updated_at = new_timestamp_value

    return new_topic_profile_schema
