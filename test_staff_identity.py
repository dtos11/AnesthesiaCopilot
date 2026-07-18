import unittest

from app.staff_directory_reader import normalize_staff_name


class StaffIdentityNormalizationTests(unittest.TestCase):

    def test_accents_resolve_to_the_same_lookup_key(self):
        equivalent_names = (
            ("José Méndez", "Jose Mendez"),
            ("Martín Garate", "Martin Garate"),
            ("Sánchez Crocci", "Sanchez Crocci"),
        )

        for accented, unaccented in equivalent_names:
            with self.subTest(accented=accented):
                self.assertEqual(
                    normalize_staff_name(accented),
                    normalize_staff_name(unaccented),
                )

    def test_normalization_is_deterministic(self):
        self.assertEqual(
            normalize_staff_name("  JOSÉ   Méndez  "),
            "jose mendez",
        )
        self.assertEqual(normalize_staff_name(123), "123")

    def test_similar_names_remain_different(self):
        different_names = (
            ("Costales", "Costalea"),
            ("Distasio", "Distacio"),
            ("Hwang", "Hwangg"),
        )

        for left, right in different_names:
            with self.subTest(left=left, right=right):
                self.assertNotEqual(
                    normalize_staff_name(left),
                    normalize_staff_name(right),
                )


if __name__ == "__main__":
    unittest.main()
