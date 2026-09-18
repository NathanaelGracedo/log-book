# tests/test_narrative_expander.py
import unittest
from scripts.narrative_expander import escape_latex, expand_narrative

class TestNarrativeExpander(unittest.TestCase):
    def test_escape_latex(self):
        self.assertEqual(escape_latex("PT Naraya & Co."), r"PT Naraya \& Co.")
        self.assertEqual(escape_latex("Progress 100%"), r"Progress 100\%")
        self.assertEqual(escape_latex("user_id & item_id"), r"user\_id \& item\_id")
        self.assertEqual(escape_latex("$100 #hashtag {code}"), r"\$100 \#hashtag \{code\}")
        self.assertEqual(escape_latex(r"c:\path\to\file"), r"c:\textbackslash{}path\textbackslash{}to\textbackslash{}file")
        self.assertEqual(escape_latex("~home ^exponent"), r"\textasciitilde{}home \textasciicircum{}exponent")
        self.assertEqual(escape_latex(""), "")
        self.assertEqual(escape_latex(None), "")

    def test_expand_narrative_rules(self):
        # Rule: onboarding
        res1 = expand_narrative("onboarding magang dan setup laptop")
        self.assertIn("onboarding", res1.lower())
        self.assertTrue(res1.endswith("."))
        self.assertTrue(res1[0].isupper())

        # Rule: meeting
        res2 = expand_narrative("meeting mingguan tim dan review tiket sprint")
        self.assertTrue(res2.startswith("Menghadiri rapat koordinasi tim"))
        self.assertTrue(res2.endswith("."))

        # Rule: existing formal sentence preserved
        formal = "Mengembangkan antarmuka pengguna dashboard analitik menggunakan Tailwind CSS."
        self.assertEqual(expand_narrative(formal), formal)

        # Rule: empty string and None
        self.assertEqual(expand_narrative(""), "")
        self.assertEqual(expand_narrative("   "), "")
        self.assertEqual(expand_narrative(None), "")

    def test_expand_narrative_bullet_stripping_and_fallback(self):
        # Bullet stripping
        res = expand_narrative("- testing endpoint autentikasi pengguna")
        self.assertTrue(res.startswith("Melakukan pengujian sistem serta verifikasi fungsionalitas fitur"))
        self.assertTrue(res.endswith("."))

        # Numbered bullet stripping
        res_num = expand_narrative("1. bugfix crash pada login")
        self.assertTrue(res_num.startswith("Melakukan penelusuran masalah dan perbaikan kendala teknis (bug fixing)"))
        self.assertTrue(res_num.endswith("."))

        # Fallback when no keyword matches: prepends Melakukan if lowercase
        res_fb = expand_narrative("sinkronisasi skema database staging")
        self.assertEqual(res_fb, "Melakukan sinkronisasi skema database staging.")

        # Fallback when already capitalized but no period
        res_fb2 = expand_narrative("Sinkronisasi skema database staging")
        self.assertEqual(res_fb2, "Sinkronisasi skema database staging.")

        # Verification that tail is not duplicated
        res_no_dup = expand_narrative("meeting mingguan tim")
        self.assertEqual(
            res_no_dup,
            "Menghadiri rapat koordinasi tim dan sinkronisasi tugas harian mingguan tim."
        )

if __name__ == "__main__":
    unittest.main()
