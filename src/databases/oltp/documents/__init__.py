from .user import UserDocument
from .user_topic_profile import UserTopicProfileDocument

__all__ = [
    "UserTopicProfileDocument",
    "UserDocument",
]
__all__ += ["__documents__"]

# For easy-to-access `document_models` parameter in `init_beanie` function
__documents__ = [
    UserTopicProfileDocument,
]
