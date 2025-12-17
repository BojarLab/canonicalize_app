import streamlit as st
import urllib.parse
from glycowork.motif.processing import canonicalize_iupac, iupac_to_smiles
from glycowork.motif.draw import GlycoDraw
from glycorender.render import convert_svg_to_pdf, convert_svg_to_png, pdf_to_svg_bytes
import base64
from io import BytesIO
import zipfile
import re
import tempfile
import os
import pandas as pd

AMBIGUOUS_MONO_TOKENS = (
  "Hex",
  "HexNAc",
  "dHex",
  "Pen"
)
AMBIGUOUS_MONO_PATTERN = re.compile(
  r"(?<![A-Za-z])(" + "|".join(AMBIGUOUS_MONO_TOKENS) + r")(?![A-Za-z])"
)
def build_smiles_row(input_seq, canonical_seq, smiles_value=""):
  """Return a uniform record for the SMILES results table."""
  return {
    "Input Sequence": input_seq,
    "Canonical Sequence": canonical_seq,
    "SMILES": smiles_value
  }

def svg_to_base64(svg_obj):
  """Convert an SVG object to base64 for embedding in HTML"""
  svg_string = svg_obj.as_svg()
  return base64.b64encode(svg_string.encode("utf-8")).decode("utf-8")

def png_to_base64(svg_string):
  """Convert SVG to PNG bytes and encode as base64"""
  png_bytes = convert_svg_to_png(svg_string, None, output_width=800, output_height=800, scale=2.0, return_bytes=True)
  return base64.b64encode(png_bytes).decode("utf-8")

def has_ambiguous_components(sequence):
  """Return True if SMILES generation should be skipped due to undefined residues/linkages"""
  if "?" in sequence:
    return True
  if any(marker in sequence for marker in ("/", "{", "}")):
    return True
  return bool(AMBIGUOUS_MONO_PATTERN.search(sequence))

def main():
  st.title("Glycan Sequence Canonicalizer")
  st.write("Paste your glycan sequences below to canonicalize them (any format should work)")

  input_text = st.text_area("Input Sequences (one per line)", height=200)
  include_smiles = st.checkbox("Include SMILES output for each sequence")

  if st.button("Convert"):
    if input_text:
      lines = input_text.strip().split("\n")
      input_sequences = []
      i = 0
      while i < len(lines):
        line = lines[i].strip()
        if not line:
          i += 1
          continue
        if line.startswith("RES"):
          glycoct_lines = [line]
          i += 1
          while i < len(lines) and lines[i].strip():
            glycoct_lines.append(lines[i].strip())
            i += 1
          input_sequences.append("\n".join(glycoct_lines))
        else:
          input_sequences.append(line)
          i += 1
      output_sequences = []
      svg_drawings = []
      smiles_results = []
      ambiguous_sequences = []
      smiles_failures = []

      for seq in input_sequences:
        if seq.strip():
          try:
            canonical = canonicalize_iupac(seq)
            output_sequences.append(canonical)
            if include_smiles:
              if has_ambiguous_components(canonical):
                ambiguous_sequences.append(seq)
                smiles_results.append(build_smiles_row(seq, canonical))
              else:
                try:
                  smiles_results.append(
                    build_smiles_row(seq, canonical, iupac_to_smiles([canonical])[0])
                  )
                except Exception as smiles_exc:
                  smiles_failures.append(f"SMILES error for '{seq}': {smiles_exc}")
            try:
              drawing = GlycoDraw(canonical, suppress=True)
              svg_string = drawing.as_svg()
              rendered_svg = pdf_to_svg_bytes(svg_string)
              svg_b64 = base64.b64encode(rendered_svg.encode("utf-8")).decode("utf-8")
              svg_drawings.append((canonical, svg_b64, rendered_svg, svg_string))
            except Exception as e:
              svg_drawings.append((canonical, None, None, None))
          except Exception as e:
            output_sequences.append(f"Error with '{seq}': {str(e)}")
            svg_drawings.append((seq, None, None, None))
            if include_smiles:
              smiles_failures.append(f"Canonicalization failed for '{seq}': {str(e)}")

      if include_smiles:
        if smiles_results:
          st.markdown("### SMILES Output")
          st.dataframe(
            pd.DataFrame(smiles_results),
            width='stretch',
            hide_index=True
          )
        else:
          st.info("No SMILES were generated. Check your input and try again.")
        if ambiguous_sequences:
          sample = ", ".join(ambiguous_sequences[:5])
          st.warning(
            "SMILES skipped for sequences with undefined residues or ambiguous bonds (Hex, '?', '/', '{ }'): "
            + sample + (" ..." if len(ambiguous_sequences) > 5 else "")
          )
        if smiles_failures:
          st.error("\n".join(smiles_failures))
      else:
        st.text_area("Canonicalized Sequences", "\n".join(output_sequences), height=200)
      
      # Display drawings in a scrollable area if any drawings were created
      if any(drawing for _, drawing, _, _ in svg_drawings):
        st.markdown("### Glycan Visualizations using GlycoDraw")

        # Create a scrollable area for the drawings
        st.markdown("""
        <style>
        .glycan-container {
          max-height: 500px;
          overflow-y: auto;
          border: 1px solid #ddd;
          padding: 10px;
          margin-bottom: 20px;
          background-color: white;
        }
        .glycan-item {
          margin-bottom: 15px;
          padding-bottom: 15px;
          border-bottom: 1px solid #eee;
        }
        </style>
        """, unsafe_allow_html=True)

        # Start the container
        glycan_html = '<div class="glycan-container">'
        for sequence, drawing, _, _ in svg_drawings:
          if drawing:
            glycan_html += f'<div class="glycan-item"><p><b>{sequence}</b></p>'
            glycan_html += f'<img src="data:image/svg+xml;base64,{drawing}" alt="{sequence}" style="max-width:100%;"/></div>'
        glycan_html += '</div>'
        st.markdown(glycan_html, unsafe_allow_html=True)
        
        # Create download all button
        valid_pdfs = [(seq, svg_content) for seq, _, _, svg_content in svg_drawings if svg_content]
        if valid_pdfs:
          zip_buffer = BytesIO()
          with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, (sequence, svg_content) in enumerate(valid_pdfs):
              safe_filename = re.sub(r'[^\w\-_\.]', '_', sequence)[:50]
              with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as temp_file:
                temp_pdf_path = temp_file.name
              try:
                convert_svg_to_pdf(svg_content, temp_pdf_path)
                with open(temp_pdf_path, 'rb') as f:
                  pdf_bytes = f.read()
                filename = f"glycan_{i+1:03d}_{safe_filename}.pdf"
                zip_file.writestr(filename, pdf_bytes)
              finally:
                if os.path.exists(temp_pdf_path):
                  os.unlink(temp_pdf_path)
          zip_buffer.seek(0)
          st.download_button(
            label="Download All PDFs as ZIP",
            data=zip_buffer.getvalue(),
            file_name="glycan_structures.zip",
            mime="application/zip"
          )
    else:
      st.error("Please enter at least one sequence.")

  # Feedback section
  st.markdown("---")
  st.header("Report an Issue")
  st.write("If you found a sequence that didn't convert correctly, please report it here:")

  with st.form("issue_report_form"):
    problem_sequence = st.text_input("Problematic Sequence")
    expected_result = st.text_input("Expected Result (optional)")
    issue_description = st.text_area("Description of the Issue", height=100)
    user_email = st.text_input("Your Email (optional, for follow-up)")

    submit_button = st.form_submit_button("Prepare Issue Report")

  if submit_button:
    if problem_sequence and issue_description:
      # Define your GitHub repository information
      repo_owner = "BojarLab"
      repo_name = "canonicalize_app"

      # Format the issue title and body
      issue_title = f"Sequence Conversion Issue: {problem_sequence[:50]}"
      issue_body = f"""
## Sequence Conversion Issue Report

**Problematic Sequence:**
```
{problem_sequence}
```

**Expected Result:**
{expected_result if expected_result else "Not specified"}

**Description of the Issue:**
{issue_description}

**Reporter Email:**
{user_email if user_email else "Not provided"}

---
*This issue was generated from the Glycan Sequence Canonicalizer web app.*
"""

      # Create a GitHub issue URL with prefilled information
      github_url = f"https://github.com/{repo_owner}/{repo_name}/issues/new?title={urllib.parse.quote(issue_title)}&body={urllib.parse.quote(issue_body)}"

      # Display the link to create the GitHub issue
      st.success("Thank you for your report! Click the button below to submit it as a GitHub issue.")
      st.markdown(f"""
      <a href="{github_url}" target="_blank">
        <button style="background-color:#0366d6; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">
          Submit as GitHub Issue
        </button>
      </a>
      """, unsafe_allow_html=True)

      st.info("Note: You'll need a GitHub account to complete the submission. If you don't have one, you can create one for free.")
    else:
      st.error("Please provide both the problematic sequence and a description of the issue.")

if __name__ == "__main__":
  main()
