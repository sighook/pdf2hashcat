# pdf2hashcat

A Python script to extract password hashes from encrypted PDF files for cracking with [hashcat](https://hashcat.net/hashcat/).

## Features

- Supports PDF versions 1.1 through 1.7 (Acrobat 2 - 11)
- Handles both standard and AES encryption
- Outputs hashes in hashcat-compatible format
- No external dependencies (pure Python 3)

## Installation

```sh
git clone https://github.com/sighook/pdf2hashcat.git
cd pdf2hashcat
```

## Usage

### Basic Usage

```sh
# Extract hash from a PDF file
./pdf2hashcat.py encrypted.pdf

# Save hash to a file
./pdf2hashcat.py encrypted.pdf > encrypted.hash

# Process multiple files
./pdf2hashcat.py file1.pdf file2.pdf file3.pdf
```

### Cracking with hashcat

```sh
# Extract the hash
./pdf2hashcat.py document.pdf | tee document.hash

# Crack using a wordlist (replace $MODE with appropriate mode from table below)
hashcat -m $MODE -a 0 document.hash wordlist.txt

# Crack using brute-force (example:  6-digit numeric PIN)
hashcat -m $MODE -a 3 document.hash ?d?d?d?d?d?d
```

## Hashcat Modes

| Mode  | Description                                |
|-------|--------------------------------------------|
| 10400 | PDF 1.1 - 1.3 (Acrobat 2 - 4)              |
| 10410 | PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #1 |
| 10420 | PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #2 |
| 10500 | PDF 1.4 - 1.6 (Acrobat 5 - 8)              |
| 25400 | PDF 1.4 - 1.6 (Acrobat 5 - 8) AES          |
| 10600 | PDF 1.7 Level 3 (Acrobat 9)                |
| 10700 | PDF 1.7 Level 8 (Acrobat 10 - 11)          |

To view all PDF-related modes supported by your hashcat version:

```sh
hashcat --help | grep -i pdf
```

## Output Format

The script outputs hashes in the following format:

```
$pdf$V*R*Length*P*EncryptMeta*IDLength*ID*ULength*U*OLength*O*[UELength*UE*OELength*OE]
```

| Field        | Description                                      |
|--------------|--------------------------------------------------|
| V            | Version of the encryption algorithm              |
| R            | Revision of the encryption algorithm             |
| Length       | Key length in bits                               |
| P            | Permission flags                                 |
| EncryptMeta  | Whether metadata is encrypted (0 or 1)           |
| ID           | Document ID (hex)                                |
| U, O         | User and Owner password hashes                   |
| UE, OE       | User and Owner encryption keys (PDF 1.7+ only)   |

## Requirements

- Python 3.6+

## Testing

```sh
python -m unittest test_pdf2hashcat.py
```

## Related Projects

- [hashcat](https://github.com/hashcat/hashcat) - Advanced password recovery tool
- [John the Ripper](https://github.com/openwall/john) - Another password cracker with PDF support

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details. 

## Credits

- Original script by Shane Quigley
- Modified for hashcat output by philsmd (2015)
- Maintained by [@sighook](https://github.com/sighook)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
