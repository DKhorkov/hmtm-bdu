import pytest

from contextlib import nullcontext as does_not_raise

from src.core.common.parsers import DatetimeParser


class TestDatetimeParser:

    @pytest.mark.parametrize(
        "iso_date_str, expected_result, expectation",
        [
            ("2025-04-04T12:25:53.281303Z", "04.04.2025", does_not_raise()),
            ("2024-03-04T12:25:53.281303Z", "04.03.2024", does_not_raise()),
            ("155325.346gr.::35325", "Ошибка загрузки формата даты", does_not_raise()),
        ]
    )
    def test_datetime_parser(
            self,
            iso_date_str: str,
            expected_result: str,
            expectation
    ) -> None:
        with expectation:
            assert DatetimeParser.parse_iso_format(iso_date_str) == expected_result
