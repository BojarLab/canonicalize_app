# IUPAC Glycan Sequence Canonicalizer

A simple web application for canonicalizing IUPAC glycan sequences using the `glycowork` Python package.

## About

This tool provides a convenient interface to convert glycan sequences into their canonicalized IUPAC representation. Simply paste your sequences, click convert, and get standardized results instantly.

## Features

- Easy-to-use web interface
- Batch processing of multiple sequences
- Instant conversion using the `canonicalize_iupac` function from glycowork
- Error handling for invalid sequences

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

## Optional SMILES Output

Enable the **Include SMILES output** checkbox in the app to convert each canonicalized sequence into SMILES using glycowork’s chem utilities. Structures that still contain undefined elements (for example `Hex`, `HexNAc`, or `?` linkages) are skipped automatically and flagged with a short note in the results table.

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
