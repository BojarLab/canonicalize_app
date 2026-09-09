import streamlit as st
import urllib.parse
from glycowork.motif.processing import canonicalize_iupac, canonicalize_composition
from glycowork.motif.smiles import glycan_to_smiles, GlycanSMILESError
from glycowork.motif.draw import GlycoDraw
from glycorender.render import convert_svg_to_pdf
import base64
from io import BytesIO
import zipfile
import re
import tempfile
import os
import html
import pandas as pd
MAX_SEQUENCES = 500

@st.cache_data(show_spinner = False)
def process_sequence(seq, want_smiles, compact, vertical, show_linkage, shadow, compositions):
  try:
    canonical = canonicalize_composition(seq, as_string = True) if compositions else canonicalize_iupac(seq)
    if not canonical:
      raise ValueError("no monosaccharides recognized")
  except Exception as e:
    return {"input": seq, "canonical": None, "error": f"Canonicalization failed for '{seq}': {e}", "smiles": None, "ambiguous": False, "svg_b64": None, "svg": None}
  if compositions:
    return {"input": seq, "canonical": canonical, "error": None, "smiles": None, "ambiguous": False, "svg_b64": None, "svg": None}
  smiles, ambiguous = None, False
  if want_smiles:
    try:
      smiles = glycan_to_smiles(canonical, strict = True)
    except GlycanSMILESError:
      ambiguous = True
    except Exception as e:
      smiles = f"Error: {e}"
  svg_b64, svg = None, None
  try:
    svg = GlycoDraw(canonical, compact = compact, vertical = vertical, show_linkage = show_linkage, shadow = shadow, suppress = True).as_svg()
    svg_b64 = base64.b64encode(convert_svg_to_pdf(svg, None, return_canvas = True, shadow = shadow).to_svg().encode("utf-8")).decode("utf-8")
  except Exception:
    pass
  return {"input": seq, "canonical": canonical, "error": None, "smiles": smiles, "ambiguous": ambiguous, "svg_b64": svg_b64, "svg": svg}

@st.cache_data(show_spinner = "Rendering PDFs...")
def build_zip(pairs, shadow):
  zip_buffer = BytesIO()
  with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    for i, (sequence, svg_content) in enumerate(pairs):
      safe_filename = re.sub(r'[^\w\-_\.]', '_', sequence)[:50]
      with tempfile.NamedTemporaryFile(mode = 'wb', suffix = '.pdf', delete = False) as temp_file:
        temp_pdf_path = temp_file.name
      try:
        convert_svg_to_pdf(svg_content, temp_pdf_path, shadow = shadow)
        with open(temp_pdf_path, 'rb') as f:
          zip_file.writestr(f"glycan_{i+1:03d}_{safe_filename}.pdf", f.read())
      finally:
        if os.path.exists(temp_pdf_path):
          os.unlink(temp_pdf_path)
  return zip_buffer.getvalue()

def main():
  st.set_page_config(page_title = "Glycan Sequence Canonicalizer", layout = "wide")
  st.title("Glycan Sequence Canonicalizer")
  st.write("Paste your glycan sequences below to canonicalize them (any format should work)")
  input_text = st.text_area("Input Sequences (one per line)", height = 200)
  uploaded = st.file_uploader("...or upload a .txt/.csv file", type = ["txt", "csv"])
  if uploaded is not None:
    input_text = uploaded.getvalue().decode("utf-8", errors = "replace")
  c0, c1 = st.columns(2)
  include_smiles = c0.checkbox("Include SMILES output for each sequence")
  compositions = c1.checkbox("Inputs are compositions (e.g., Hex5HexNAc4Fuc1Neu5Ac2)")
  c2, c3, c4, c5 = st.columns(4)
  compact = c2.checkbox("Compact drawings")
  vertical = c3.checkbox("Vertical drawings")
  show_linkage = c4.checkbox("Show linkages", value = True)
  shadow = c5.checkbox("Drop shadow")
  if st.button("Convert"):
    if not input_text.strip():
      st.error("Please enter at least one sequence.")
    else:
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
      if len(input_sequences) > MAX_SEQUENCES:
        st.warning(f"Input truncated to the first {MAX_SEQUENCES} sequences (received {len(input_sequences)}).")
        input_sequences = input_sequences[:MAX_SEQUENCES]
      progress = st.progress(0.0, text = "Processing sequences...")
      results = []
      for n, seq in enumerate(input_sequences, 1):
        results.append(process_sequence(seq, include_smiles, compact, vertical, show_linkage, shadow, compositions))
        progress.progress(n / len(input_sequences), text = f"Processed {n}/{len(input_sequences)} sequences")
      progress.empty()
      st.session_state.results = results
      st.session_state.smiles_on = include_smiles and not compositions
      st.session_state.pop("zip_bytes", None)
  results = st.session_state.get("results")
  if results:
    st.text_area("Canonicalized Sequences", "\n".join(r["error"] or r["canonical"] for r in results), height = 200)
    st.download_button("Download sequences (.txt)", "\n".join(r["canonical"] for r in results if r["canonical"]), file_name = "canonical_sequences.txt", mime = "text/plain")
    if st.session_state.get("smiles_on"):
      df = pd.DataFrame([{"Input Sequence": r["input"], "Canonical Sequence": r["canonical"] or "", "SMILES": r["smiles"] or ""} for r in results])
      st.markdown("### SMILES Output")
      st.dataframe(df, width = 'stretch', hide_index = True)
      st.download_button("Download SMILES (.csv)", df.to_csv(index = False), file_name = "glycan_smiles.csv", mime = "text/csv")
      ambiguous = [r["input"] for r in results if r["ambiguous"]]
      if ambiguous:
        st.warning("SMILES skipped for sequences with undefined residues, linkage positions, or attachment points: " + ", ".join(ambiguous[:5]) + (" ..." if len(ambiguous) > 5 else ""))
    failures = [r["error"] for r in results if r["error"]]
    if failures:
      st.error("\n".join(failures))
    drawn = [r for r in results if r["svg_b64"]]
    if drawn:
      st.markdown("### Glycan Visualizations using GlycoDraw")
      st.markdown("""<style>
.glycan-container {max-height: 500px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; background-color: white; color: #000;}
.glycan-item {margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee;}
</style>""", unsafe_allow_html = True)
      glycan_html = '<div class="glycan-container">'
      for r in drawn:
        label = html.escape(r["canonical"])
        b64 = r["svg_b64"]
        glycan_html += f'<div class="glycan-item"><p><b>{label}</b></p><img src="data:image/svg+xml;base64,{b64}" alt="{label}" style="max-width:100%;"/></div>'
      glycan_html += '</div>'
      st.markdown(glycan_html, unsafe_allow_html = True)
      if st.button("Prepare PDF download"):
        st.session_state.zip_bytes = build_zip(tuple((r["canonical"], r["svg"]) for r in drawn), shadow)
      if st.session_state.get("zip_bytes"):
        st.download_button("Download All PDFs as ZIP", data = st.session_state.zip_bytes, file_name = "glycan_structures.zip", mime = "application/zip")

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
