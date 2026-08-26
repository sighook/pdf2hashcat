#!/usr/bin/env python3

"""
Unit tests for pdf2hashcat.py

Run tests: 
    python -m unittest test_pdf2hashcat.py
    python -m pytest test_pdf2hashcat.py
"""

import io
import unittest
from unittest.mock import patch, mock_open
from pdf2hashcat import PdfParser


class TestPdfParser(unittest.TestCase):
    """Test cases for PdfParser class."""

    # =========================================================================
    # Test fixtures and helpers
    # =========================================================================

    # Standard PDF header
    PDF_HEADER = b"%PDF-1.4\n"

    # Standard encryption dictionary (valid for most tests)
    STANDARD_ENC_DICT = b"/Filter /Standard /V 2 /R 3 /Length 128 /P -3904"

    def _create_parser_with_mocks(self, mock_get_dict, mock_get_obj_id,
                                   mock_get_trailer, trailer, enc_dict=None):
        """
        Helper to set up mocks and create a PdfParser instance.

        Args:
            mock_get_dict: Mock for get_encryption_dictionary()
            mock_get_obj_id:  Mock for get_object_id()
            mock_get_trailer: Mock for get_trailer()
            trailer: Bytes for the trailer (e.g., b"/ID [<abcd> <efgh>]")
            enc_dict:  Bytes for encryption dictionary (defaults to STANDARD_ENC_DICT)

        Returns: 
            PdfParser instance ready for testing
        """
        mock_get_trailer.return_value = trailer
        mock_get_obj_id.return_value = b"12 0"
        mock_get_dict.return_value = enc_dict or self.STANDARD_ENC_DICT
        return PdfParser("dummy.pdf")

    def _parse_output(self, parser):
        """Run the parser and return the emitted hash without its newline."""
        output = io.StringIO()
        with patch("sys.stdout", output):
            parser.parse()
        return output.getvalue().rstrip("\n")

    def _assert_parse_succeeds(self, parser, msg="Parse should succeed"):
        """Assert that parser.parse() completes without exception."""
        try:
            return self._parse_output(parser)
        except Exception as exc:
            self.fail(f"{msg}: {exc}")

    def _assert_parse_fails_with(self, parser, expected_message):
        """Assert that parser.parse() raises RuntimeError with expected message."""
        with self.assertRaises(RuntimeError) as context:
            parser.parse()
        self.assertIn(expected_message, str(context.exception))

    # =========================================================================
    # Valid ID tests
    # =========================================================================

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_valid_id_with_brackets(self, mock_get_dict, mock_get_obj_id,
                                    mock_get_trailer, mock_file):
        """Valid /ID with <hex> brackets should parse successfully."""
        parser = self._create_parser_with_mocks(
            mock_get_dict, mock_get_obj_id, mock_get_trailer,
            trailer=b"/ID [<abcd> <efgh>]"
        )
        self._assert_parse_succeeds(parser)

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_valid_id_with_parentheses(self, mock_get_dict, mock_get_obj_id,
                                       mock_get_trailer, mock_file):
        """Valid /ID with (literal) parentheses should parse successfully."""
        parser = self._create_parser_with_mocks(
            mock_get_dict, mock_get_obj_id, mock_get_trailer,
            trailer=b"/ID [(abcd) (efgh)]"
        )
        self._assert_parse_succeeds(parser)

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_valid_id_without_filter(self, mock_get_dict, mock_get_obj_id,
                                     mock_get_trailer, mock_file):
        """PDF without explicit /Filter should still work (backward compat)."""
        parser = self._create_parser_with_mocks(
            mock_get_dict, mock_get_obj_id, mock_get_trailer,
            trailer=b"/ID [<abcd> <efgh>]",
            enc_dict=b"/V 2 /R 3 /Length 128 /P -3904"  # No /Filter
        )
        self._assert_parse_succeeds(parser)

    # =========================================================================
    # Empty ID tests (PR #3 fix)
    # =========================================================================

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_empty_id_with_brackets(self, mock_get_dict, mock_get_obj_id,
                                    mock_get_trailer, mock_file):
        """Empty /ID with <> brackets should parse successfully."""
        parser = self._create_parser_with_mocks(
            mock_get_dict, mock_get_obj_id, mock_get_trailer,
            trailer=b"/ID [<> <>]"
        )
        self._assert_parse_succeeds(parser)

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_empty_id_with_parentheses(self, mock_get_dict, mock_get_obj_id,
                                       mock_get_trailer, mock_file):
        """Empty /ID with () parentheses should parse successfully."""
        parser = self._create_parser_with_mocks(
            mock_get_dict, mock_get_obj_id, mock_get_trailer,
            trailer=b"/ID [() ()]"
        )
        self._assert_parse_succeeds(parser)

    # =========================================================================
    # Partial/malformed ID tests
    # =========================================================================

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_partial_id_with_brackets_and_space(self, mock_get_dict, mock_get_obj_id,
                                                mock_get_trailer, mock_file):
        """Malformed /ID with space inside brackets < > should fail."""
        parser = self._create_parser_with_mocks(
            mock_get_dict, mock_get_obj_id, mock_get_trailer,
            trailer=b"/ID [<abcd> < >]"
        )
        self._assert_parse_fails_with(parser, "Could not find /ID tag")

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_partial_id_with_parentheses(self, mock_get_dict, mock_get_obj_id,
                                         mock_get_trailer, mock_file):
        """Partial /ID with one full and one empty () should still work."""
        parser = self._create_parser_with_mocks(
            mock_get_dict, mock_get_obj_id, mock_get_trailer,
            trailer=b"/ID [(abcd) ()]"
        )
        self._assert_parse_succeeds(parser)

    # =========================================================================
    # Unsupported encryption filter tests (Issue #2)
    # =========================================================================

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_unsupported_filter_fopn_foweb(self, mock_get_dict, mock_get_obj_id,
                                           mock_get_trailer, mock_file):
        """FileOpen DRM (FOPN_foweb) should fail with clear error message."""
        parser = self._create_parser_with_mocks(
            mock_get_dict, mock_get_obj_id, mock_get_trailer,
            trailer=b"/ID [<abcd> <efgh>]",
            enc_dict=b"/Filter/FOPN_foweb/V 2/Length 128"
        )
        self._assert_parse_fails_with(parser, "FOPN_foweb")

    # =========================================================================
    # Encryption dictionary string tests
    # =========================================================================

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    def test_literal_string_named_escapes(self, mock_file):
        """PDF-defined literal escapes must become their byte values."""
        parser = PdfParser("dummy.pdf")
        values = parser.get_passwords_for_JtR(
            b"/U (A\\nB\\rC\\tD\\bE\\fF\\\\G) /O (owner)"
        )
        self.assertEqual(
            values,
            "13*410a420d43094408450c465c47*5*6f776e6572",
        )

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    def test_literal_string_unknown_escapes_drop_backslash(self, mock_file):
        """Unknown PDF escapes preserve the byte and discard the backslash."""
        parser = PdfParser("dummy.pdf")
        values = parser.get_passwords_for_JtR(
            b"/U (\\s\\e\\v\\a) /O (owner)"
        )
        self.assertEqual(values, "4*73657661*5*6f776e6572")

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    def test_literal_string_octal_and_line_rules(self, mock_file):
        """Octal escapes and PDF line handling must decode before hashing."""
        parser = PdfParser("dummy.pdf")
        values = parser.get_passwords_for_JtR(
            b"/U (A\\101\\12B\\\r\nC\rD\nE) /O (owner)"
        )
        self.assertEqual(values, "9*41410a42430a440a45*5*6f776e6572")

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    def test_literal_string_escaped_closing_parenthesis(self, mock_file):
        """An escaped right parenthesis is data, not the string terminator."""
        parser = PdfParser("dummy.pdf")
        values = parser.get_passwords_for_JtR(
            b"/U (left\\)right) /O (owner)"
        )
        self.assertEqual(
            values,
            "10*6c656674297269676874*5*6f776e6572",
        )

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    def test_literal_string_balanced_parentheses(self, mock_file):
        """Balanced unescaped parentheses may occur inside a PDF string."""
        parser = PdfParser("dummy.pdf")
        values = parser.get_passwords_for_JtR(
            b"/U (a(b)c) /O (owner)"
        )
        self.assertEqual(values, "5*6128622963*5*6f776e6572")

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    def test_empty_literal_string_value(self, mock_file):
        """Empty literal strings are valid PDF string objects."""
        parser = PdfParser("dummy.pdf")
        values = parser.get_passwords_for_JtR(b"/U () /O (owner)")
        self.assertEqual(values, "0**5*6f776e6572")

    @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    def test_hex_string_whitespace_and_odd_nibble(self, mock_file):
        """Hex strings ignore PDF whitespace and pad a final odd nibble."""
        parser = PdfParser("dummy.pdf")
        values = parser.get_passwords_for_JtR(
            b"/U <61 62\n6> /O <6f776e6572>"
        )
        self.assertEqual(values, "3*616260*5*6f776e6572")

    # =========================================================================
    # Compact object layout tests (no newline before "<id> obj")
    # =========================================================================

    def _make_pdf_bytes(self, objects, trailer_id=b"<abcd> <efgh>",
                        encrypt_ref=b"5 0"):
        """Assemble minimal PDF bytes from a list of (object_id, body) tuples."""
        body = b"%PDF-1.7\n"
        for obj_id, obj_body in objects:
            body += obj_id + b" obj\n" + obj_body + b"\nendobj "
        body += b"\ntrailer<</Size " + str(len(objects)).encode() + \
                b" /Root 1 0 R /ID [" + trailer_id + \
                b"] /Encrypt " + encrypt_ref + b" R>>\n%%EOF"
        return body

    def test_parse_emits_decoded_literal_string_hash(self):
        """Literal string syntax must be reflected in the emitted hash."""
        enc_dict = b"<</V 2 /R 3 /Length 128 /P -3904 " \
                   b"/Filter /Standard " \
                   b"/U (left\\)right) /O (\\101\\e)>>"
        pdf_bytes = self._make_pdf_bytes(
            [(b"1 0", b"<</Type /Catalog>>"),
             (b"5 0", enc_dict)],
        )
        with patch("builtins.open", mock_open(read_data=pdf_bytes)):
            parser = PdfParser("dummy.pdf")

        self.assertEqual(
            self._parse_output(parser),
            "$pdf$2*3*128*-3904*1*2*abcd*"
            "10*6c656674297269676874*2*4165",
        )

    def test_compact_layout_encrypt_object(self):
        """Encrypt object preceded by space (not \\r\\n) must still parse.

        Regression for PDFs that pack 'endobj <next-id> obj' on one line.
        """
        enc_dict = b"<</V 2 /R 3 /Length 128 /P -3904 " \
                   b"/Filter /Standard " \
                   b"/U (" + b"x" * 32 + b") " \
                   b"/O (" + b"y" * 32 + b")>>"
        pdf_bytes = self._make_pdf_bytes(
            [(b"1 0", b"<</Type /Catalog>>"),
             (b"5 0", enc_dict)],
        )
        with patch("builtins.open", mock_open(read_data=pdf_bytes)):
            parser = PdfParser("dummy.pdf")
        self._assert_parse_succeeds(parser)

    def test_get_pdf_object_does_not_match_digit_prefix(self):
        """Looking up '9 0 obj' must not match '19 0 obj' or '129 0 obj'."""
        pdf_bytes = b"%PDF-1.4\n" \
                    b"19 0 obj\n<</Bogus true>>\nendobj\n" \
                    b"9 0 obj\n<</Real true>>\nendobj\n"
        with patch("builtins.open", mock_open(read_data=pdf_bytes)):
            parser = PdfParser("dummy.pdf")
        obj = parser.get_pdf_object(b"9 0")
        self.assertIn(b"/Real true", obj)
        self.assertNotIn(b"/Bogus", obj)

    def test_get_pdf_object_does_not_match_non_whitespace_prefix(self):
        """Looking up '9 0 obj' must not match 'foo9 0 obj' inside a stream.

        Enforces the PDF token-boundary semantic: object headers are only
        recognized when preceded by PDF whitespace (or start of input),
        not just by any non-digit byte.
        """
        pdf_bytes = b"%PDF-1.4\n" \
                    b"1 0 obj\n<</Length 12>>stream\nfoo9 0 obj\nendstream\nendobj\n" \
                    b"9 0 obj\n<</Real true>>\nendobj\n"
        with patch("builtins.open", mock_open(read_data=pdf_bytes)):
            parser = PdfParser("dummy.pdf")
        obj = parser.get_pdf_object(b"9 0")
        self.assertIn(b"/Real true", obj)
        self.assertNotIn(b"stream", obj)

    # =========================================================================
    # Add new test cases below
    # =========================================================================
    #
    # Template: 
    #
    # @patch("builtins.open", new_callable=mock_open, read_data=PDF_HEADER)
    # @patch.object(PdfParser, "get_trailer")
    # @patch.object(PdfParser, "get_object_id")
    # @patch.object(PdfParser, "get_encryption_dictionary")
    # def test_your_case(self, mock_get_dict, mock_get_obj_id,
    #                    mock_get_trailer, mock_file):
    #     """Description."""
    #     parser = self._create_parser_with_mocks(
    #         mock_get_dict, mock_get_obj_id, mock_get_trailer,
    #         trailer=b"/ID [<abcd> <efgh>]",
    #         enc_dict=b"/Filter /Standard /V 2 /R 3 /Length 128 /P -3904"
    #     )
    #     self._assert_parse_succeeds(parser)
    #     # or:  self._assert_parse_fails_with(parser, "error message")
    #


if __name__ == "__main__":
    unittest.main()
