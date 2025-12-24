#!/usr/bin/env python3

"""
Unit tests for pdf2hashcat.py

Run tests: 
    python -m unittest test_pdf2hashcat.py
    python -m pytest test_pdf2hashcat.py
"""

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

    def _assert_parse_succeeds(self, parser, msg="Parse should succeed"):
        """Assert that parser.parse() completes without exception."""
        try:
            parser.parse()
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
