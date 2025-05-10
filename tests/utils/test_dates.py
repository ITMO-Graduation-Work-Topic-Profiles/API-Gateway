from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.utils.dates import utcnow


class TestUtcnow:
    def test_utcnow_returns_datetime_with_timezone(self) -> None:
        result = utcnow()

        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_utcnow_returns_current_time(self) -> None:
        before = datetime.now(timezone.utc)
        result = utcnow()
        after = datetime.now(timezone.utc)

        assert before <= result <= after

    @patch("src.utils.dates.datetime")
    def test_utcnow_uses_datetime_now(self, mock_datetime: MagicMock) -> None:
        mock_now = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        result = utcnow()

        mock_datetime.now.assert_called_once_with(timezone.utc)
        assert result == mock_now
