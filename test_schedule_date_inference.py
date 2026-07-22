import unittest
from datetime import date

from app.schedule_date_inference import infer_schedule_date


class ScheduleDateInferenceTests(unittest.TestCase):

    REFERENCE_DATE = date(2026, 7, 22)

    def test_common_filename_variations(self):
        filenames = [
            "Lista del 23 de julio.xlsx",
            "Listas del 23 de julio.xlsx",
            "Lista 23 de julio.xlsx",
            "Listas 23 de julio.xlsx",
            "23 de julio.xlsx",
            "Lista 23 julio.xlsx",
            "Programación 23 de julio.xlsx",
            " Listas   23   de   julio.xlsx ",
        ]

        for filename in filenames:
            with self.subTest(filename=filename):
                self.assertEqual(
                    infer_schedule_date(filename, self.REFERENCE_DATE),
                    date(2026, 7, 23),
                )

    def test_filenames_without_day_and_month_are_rejected(self):
        filenames = [
            "Lista.xlsx",
            "Programación.xlsx",
            "Julio.xlsx",
            "Lista mañana.xlsx",
        ]

        for filename in filenames:
            with self.subTest(filename=filename):
                with self.assertRaises(ValueError):
                    infer_schedule_date(filename, self.REFERENCE_DATE)

    def test_multiple_dates_are_rejected_as_ambiguous(self):
        with self.assertRaises(ValueError):
            infer_schedule_date(
                "Lista 23 julio o 24 julio.xlsx",
                self.REFERENCE_DATE,
            )

    def test_closest_year_behavior_is_preserved(self):
        self.assertEqual(
            infer_schedule_date(
                "Lista 2 enero.xlsx",
                date(2026, 12, 31),
            ),
            date(2027, 1, 2),
        )
        self.assertEqual(
            infer_schedule_date(
                "Lista 31 diciembre.xlsx",
                date(2026, 1, 2),
            ),
            date(2025, 12, 31),
        )


if __name__ == "__main__":
    unittest.main()
