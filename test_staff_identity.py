import unittest
from types import SimpleNamespace

from app.staff_directory_reader import normalize_staff_name
from app.staff_identity_service import StaffIdentityService


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


class StaffIdentitySuggestionTests(unittest.TestCase):

    def setUp(self):
        staff = [
            SimpleNamespace(his_full_name="Grimblatt Matias"),
            SimpleNamespace(his_full_name="Betular Haas Juan Ignacio"),
            SimpleNamespace(his_full_name="Mega Diaz Federico Andres"),
        ]
        aliases = [
            SimpleNamespace(
                alias="Grimblatt",
                his_full_name="Grimblatt Matias",
            ),
            SimpleNamespace(
                alias="Betular",
                his_full_name="Betular Haas Juan Ignacio",
            ),
            SimpleNamespace(
                alias="Mega Diaz",
                his_full_name="Mega Diaz Federico Andres",
            ),
        ]
        directory_reader = SimpleNamespace(
            read=lambda: (staff, aliases),
        )
        self.service = StaffIdentityService(directory_reader)

    def test_obvious_typo_returns_one_high_confidence_suggestion(self):
        suggestions = self.service.suggest("GRIMBALTT")

        self.assertEqual(len(suggestions), 1)
        self.assertEqual(
            suggestions[0].canonical_name,
            "Grimblatt Matias",
        )
        self.assertGreaterEqual(
            suggestions[0].similarity_score,
            self.service.SUGGESTION_SCORE_CUTOFF,
        )

    def test_already_resolved_name_has_no_suggestions(self):
        self.assertEqual(self.service.suggest("BETULAR"), [])

    def test_alias_based_suggestion_returns_canonical_name(self):
        suggestions = self.service.suggest("MEGA DIAZZ")

        self.assertEqual(len(suggestions), 1)
        self.assertEqual(
            suggestions[0].canonical_name,
            "Mega Diaz Federico Andres",
        )

    def test_composite_value_has_no_suggestions(self):
        self.assertEqual(
            self.service.suggest("BASSO/MONTANARO"),
            [],
        )

    def test_unrelated_value_has_no_suggestions(self):
        self.assertEqual(
            self.service.suggest("ALERGIA AL LATEX"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
