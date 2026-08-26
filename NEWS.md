# NEWS

## pdf2hashcat 1.0.0 — 2026-08-26

This is the first tagged release of pdf2hashcat from this repository.

It collects the project history since the initial import in December 2022,
including parser fixes, broader PDF compatibility, diagnostics, regression
tests, documentation improvements, and the recent rework of PDF literal-string
parsing.

### Project lineage

pdf2hashcat is derived from the PDF password hash extraction code originally
written by Shane Quigley in 2013 and modified by philsmd in 2015 to emit hashes
for hashcat.

The project was imported into this repository in December 2022 and has since
been maintained and extended as a standalone Python 3 hashcat extractor.

### PDF support

* Extract password hashes from encrypted PDF documents for use with hashcat.
* Support PDF 1.1 through 1.7 encryption revisions handled by hashcat.
* Support standard and AES-encrypted PDF password protection.
* Handle user and owner password data and the `UE`/`OE` fields used by newer
  PDF encryption revisions.
* Produce hashcat-compatible `$pdf$...` output without external Python
  dependencies.

### Parser correctness

* Fix PDF document ID extraction, including empty IDs and IDs represented with
  either hexadecimal strings or parenthesized strings.
* Correctly strip delimiters from parenthesized document IDs.
* Recognize indirect PDF objects separated by valid PDF whitespace rather than
  assuming object headers begin on a new line.
* Handle compact object layouts such as `endobj 19 0 obj`.
* Enforce object token boundaries so an object number cannot be matched as a
  suffix of another object number or from arbitrary stream contents.
* Replace regex-based password-string boundary recovery with a byte-level PDF
  string-object scanner.
* Handle escaped and balanced parentheses in PDF literal strings.
* Decode the PDF-defined literal-string escapes.
* Apply PDF semantics to unknown escape sequences by ignoring the escape
  backslash.
* Support octal escapes and escaped line continuations in literal strings.
* Parse hexadecimal string objects through the same value path, including PDF
  whitespace and odd hexadecimal digit counts.
* Keep PDF names such as `/U` and `/UE` distinct while locating encryption
  dictionary values.

### Diagnostics

* Detect FileOpen `/FOPN_foweb` DRM and report it explicitly as unsupported
  rather than failing later with an unrelated parser error.

  FileOpen is license-based DRM rather than PDF password hashing, so there is
  no password hash for pdf2hashcat to extract for hashcat.

### Testing

* Introduce a unit-test suite for PDF ID extraction and parser behavior.
* Add regression coverage for empty and parenthesized document IDs.
* Add FileOpen DRM coverage.
* Add direct coverage of compact PDF object layouts and object token
  boundaries.
* Capture parser output so tests can validate the public hash-generation
  contract instead of only parser internals.
* Add regression coverage for PDF literal-string escapes, octal escapes,
  unknown escapes, line continuations, escaped parentheses, balanced
  parentheses, hexadecimal strings, and adjacent PDF names.
* Add an end-to-end test asserting the complete hashcat output produced from a
  PDF containing the literal-string cases reported in PRs #7 and #8.

### Documentation

* Expand the README with installation, usage, supported hashcat modes, output
  format, requirements, testing instructions, and project credits.
* Correct command examples and hashcat invocation documentation.
* Use hashcat's extended `-hh` help output when listing all supported PDF hash
  modes.

### Contributors

Thanks to everyone who has contributed code, reports, testing, review, or
historical work to pdf2hashcat:

* Shane Quigley — original PDF password hash extraction implementation.
* philsmd — original adaptation for hashcat output.
* V (`@deviant`, V@anomalous) — Python 3 invalid escape-sequence warning
  cleanup.
* Fedor Golishevskii (`@aurabirb`) — PDF document ID extraction fixes.
* `@synner88` — compact PDF object-layout parsing and regression coverage.
* Velizar Dimitrov — PDF object-boundary tightening and regression coverage.
* Kartik Soneji (`@KartikSoneji`) — reports for the literal-string escape and
  escaped-parenthesis regressions, plus validation of the replacement parser
  against the original affected PDFs.
* Omer (`@omerav`) — correction to the hashcat mode-discovery documentation.
* Alexandr Savca (`@sighook`) — repository maintenance, parser work, tests,
  documentation, and release integration.

Thank you also to everyone who tested the parser against real-world PDF files
and helped turn isolated failures into regression coverage.
