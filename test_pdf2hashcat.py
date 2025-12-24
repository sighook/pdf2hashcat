import unittest
from unittest.mock import patch, mock_open
from pdf2hashcat import PdfParser

class TestPdfParser(unittest.TestCase):
    def setUp(self):
        # Valid PDF header and base content
        self.valid_pdf_header = b"%PDF-1.4\n"


    ## 1 #####################################################################

    @patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4\n")
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")

    def test_valid_id_with_brackets(self, mock_get_dict, mock_get_obj_id,
                                    mock_get_trailer, mock_file):
        # Valid `/ID` with `< >` brackets
        mock_get_trailer.return_value = b"/ID [<abcd> <efgh>]"
        mock_get_obj_id.return_value = b"12 0"
        mock_get_dict.return_value = b"/V 2 /R 3 /Length 128 /P -3904"

        # Create a new instance with the mocked file
        parser = PdfParser("dummy.pdf")

        # Run
        try:
            parser.parse()
        except Exception as exc:
            self.fail(f"Valid ID with brackets failed with error: {exc}")

    ## 2 #####################################################################

    @patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4\n")
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_id_with_parentheses(self, mock_get_dict, mock_get_obj_id,
                                 mock_get_trailer, mock_file):
        # Valid `/ID` with `()` parentheses
        mock_get_trailer.return_value = b"/ID [(abcd) (efgh)]"
        mock_get_obj_id.return_value = b"12 0"
        mock_get_dict.return_value = b"/V 2 /R 3 /Length 128 /P -3904"

        # Create a new instance with the mocked file
        parser = PdfParser("dummy.pdf")

        # Run
        try:
            parser.parse()
        except Exception as exc:
            self.fail(f"Valid ID with parentheses failed with error: {exc}")

    ## 3 #####################################################################

    @patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4\n")
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_empty_id_with_brackets(self, mock_get_dict, mock_get_obj_id,
                                    mock_get_trailer, mock_file):
        # Empty `/ID` with `< >` brackets
        mock_get_trailer.return_value = b"/ID [<> <>]"
        mock_get_obj_id.return_value = b"12 0"
        mock_get_dict.return_value = b"/V 2 /R 3 /Length 128 /P -3904"

        # Create a new instance with the mocked file
        parser = PdfParser("dummy.pdf")

        # Parse
        #with self.assertRaises(RuntimeError) as context:
        #    parser.parse()
        # Ensure correct error message
        #self.assertIn("Could not find /ID tag", str(context.exception))

        # Run
        try:
            parser.parse()
        except Exception as exc:
            self.fail(f"Valid ID with brackets failed with error: {exc}")


    ## 4 #####################################################################

    @patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4\n")
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_empty_id_with_parentheses(self, mock_get_dict, mock_get_obj_id,
                                       mock_get_trailer, mock_file):
        # Empty `/ID` with `()` parentheses
        mock_get_trailer.return_value = b"/ID [() ()]"
        mock_get_obj_id.return_value = b"12 0"
        mock_get_dict.return_value = b"/V 2 /R 3 /Length 128 /P -3904"

        # Create a new instance with the mocked file
        parser = PdfParser("dummy.pdf")

        # Parse
        #with self.assertRaises(RuntimeError) as context:
        #    parser.parse()

        # Ensure correct error message
        #self.assertIn("Could not find /ID tag", str(context.exception))

        # Run
        try:
            parser.parse()
        except Exception as exc:
            self.fail(f"Valid ID with brackets failed with error: {exc}")

    ## 5 #####################################################################

    @patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4\n")
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_partial_id_with_brackets(self, mock_get_dict, mock_get_obj_id,
                                      mock_get_trailer, mock_file):
        # Partial `/ID` with `<abcd>` and `< >`
        mock_get_trailer.return_value = b"/ID [<abcd> < >]"
        mock_get_obj_id.return_value = b"12 0"
        mock_get_dict.return_value = b"/V 2 /R 3 /Length 128 /P -3904"

        # Create a new instance with the mocked file
        parser = PdfParser("dummy.pdf")

        # Parse
        with self.assertRaises(RuntimeError) as context:
            parser.parse()

        # Ensure correct error message
        self.assertIn("Could not find /ID tag", str(context.exception))

    ## 6 #####################################################################

    @patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4\n")
    @patch.object(PdfParser, "get_trailer")
    @patch.object(PdfParser, "get_object_id")
    @patch.object(PdfParser, "get_encryption_dictionary")
    def test_partial_id_with_parentheses(self, mock_get_dict, mock_get_obj_id,
                                         mock_get_trailer, mock_file):
        # Partial `/ID` with `(abcd)` and `()`
        mock_get_trailer.return_value = b"/ID [(abcd) ()]"
        mock_get_obj_id.return_value = b"12 0"
        mock_get_dict.return_value = b"/V 2 /R 3 /Length 128 /P -3904"

        # Create a new instance with the mocked file
        parser = PdfParser("dummy.pdf")

        # Parse
        #with self.assertRaises(RuntimeError) as context:
        #    parser.parse()

        # Ensure correct error message
        #self.assertIn("Could not find /ID tag", str(context.exception))

        # Run
        try:
            parser.parse()
        except Exception as exc:
            self.fail(f"Valid ID with brackets failed with error: {exc}")

    ###########################################################################

if __name__ == "__main__":
    unittest.main()
