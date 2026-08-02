# IUPAC Glycan Sequence Canonicalizer

A simple web application for canonicalizing IUPAC glycan sequences using the `glycowork` Python package.

## About

This tool provides a convenient interface to convert glycan sequences into their canonicalized IUPAC representation. Simply paste your sequences, click convert, and get standardized results instantly.

## Features

- Easy-to-use web interface, with paste-in or file upload (.txt/.csv) input
- Batch processing of multiple sequences across IUPAC-extended, LinearCode, GlycoCT, WURCS, Oxford, GLYCAM, GlycoWorkBench, CSDB-linear, KCF, GlyConnect, and GlyTouCan formats
- Instant conversion using the `canonicalize_iupac` function from glycowork
- Optional SMILES generation via `IUPAC_to_SMILES`, with automatic skipping of ambiguous sequences
- SNFG structure rendering with `GlycoDraw`, downloadable individually or as a PDF archive
- Downloadable canonicalized sequences (`.txt`) and SMILES tables (`.csv`)
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