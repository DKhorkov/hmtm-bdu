from datetime import datetime


class DatetimeParser:

    @staticmethod
    def parse(iso_date_str: str) -> str:
        """
            Преобразует строку даты в формате ISO 8601 (например, '2025-04-04T12:25:53.281303Z')
            в строку формата 'дд.мм.гггг' (например, '04.04.2025').
        """
        try:
            date_obj = datetime.strptime(iso_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            return date_obj.strftime("%d.%m.%Y")
        except Exception:
            return "Ошибка загрузки формата даты"
