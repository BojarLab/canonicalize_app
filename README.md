# IUPAC Glycan Sequence Canonicalizer

A simple web application for canonicalizing IUPAC glycan sequences using the `glycowork` Python package.

## About

This tool provides a convenient interface to convert glycan sequences into their canonicalized IUPAC representation. Simply paste your sequences, click convert, and get standardized results instantly.

## Features

- Easy-to-use web interface, with paste-in or file upload (.txt/.csv) input
- Batch processing of multiple sequences across IUPAC-extended, LinearCode, GlycoCT, WURCS, Oxford, GLYCAM, GlycoWorkBench, pGlyco, StrucGP, CSDB-linear, KCF, SMILES, LINUCS, GlyConnect, and GlyTouCan formats
- Instant conversion using the `canonicalize_iupac` function from glycowork
- Compositions (H5N4F1A2, Hex5HexNAc4Fuc1Neu5Ac2, HexNAc(4)Hex(5)Fuc(1)NeuAc(2), {Hex:5; HexNAc:4}, with adducts such as [M+Na]+ stripped) are detected automatically and canonicalized via `canonicalize_composition` into shorthand, Byonic/MSFragger, or GlycReSoft strings; all-digit codes (5421 = Hex/HexNAc/Neu5Ac/dHex) via the composition checkbox
- Optional export to SMILES (offline `glycowork.motif.smiles`, skipping only sequences whose residues, linkage positions, or attachment points are genuinely undefined), GlycoCT, IUPAC-extended, GLYCAM, and Oxford, plus elemental formula and monoisotopic mass
- SNFG rendering of structures and compositions with `GlycoDraw`, with optional drop shadow or sticker style, downloadable as a PDF archive
- Downloadable canonicalized sequences (`.txt`) and conversion tables (`.csv`)
- Error handling for invalid sequences, plus a built-in GitHub issue reporter

## Usage

1. Enter one or more glycan sequences in the input text area (one per line)
2. Click the "Convert" button
3. View and copy the canonicalized sequences from the output area

## Local Development

To run this application locally:

```
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

This application is deployed on Streamlit Cloud and is freely accessible at the [canonicalize app](https://canonicalize.streamlit.app/).

## Dependencies

- streamlit
- glycowork

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or issues related to this application, please open an issue on this repository.
For questions about the glycowork package, visit the [glycowork repository](https://github.com/BojarLab/glycowork).