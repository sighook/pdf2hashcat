# pdf2hashcat

The goal of this script is to make it very easy to convert
Password-protected PDF Files to so-called "hashes" which
hashcat can crack.

hashcat mode
------------

| MODE  | DESCRIPTION                                |
| ----- | ------------------------------------------ |
| 10400 | PDF 1.1 - 1.3 (Acrobat 2 - 4)              |
| 10410 | PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #1 |
| 10420 | PDF 1.1 - 1.3 (Acrobat 2 - 4), collider #2 |
| 10500 | PDF 1.4 - 1.6 (Acrobat 5 - 8)              |
| 25400 | PDF 1.4 - 1.6 (Acrobat 5 - 8)              |
| 10600 | PDF 1.7 Level 3 (Acrobat 9)                |
| 10700 | PDF 1.7 Level 8 (Acrobat 10 - 11)          |

Use the following command to view supported modes:

```sh
hashcat --help | grep -i pdf
```

usage
-----

```sh
pdf2hashcat dummy.pdf | tee dummy.pdf.hashcat
hashcat -m $MODE -a 0 dummy.pdf.hashcat wordlist.txt
```
