import streamlit as st
import urllib.parse
from glycowork.motif.processing import canonicalize_iupac
from glycowork.motif.draw import GlycoDraw
import base64
from io import BytesIO

def svg_to_base64(svg_obj):
  """Convert an SVG object to base64 for embedding in HTML"""
  svg_string = svg_obj.as_svg()
  return base64.b64encode(svg_string.encode("utf-8")).decode("utf-8")

def main():
  st.title("Glycan Sequence Canonicalizer")
  st.write("Paste your glycan sequences below to canonicalize them (any format should work)")

  input_text = st.text_area("Input Sequences (one per line)", height=200)

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

      for seq in input_sequences:
        if seq.strip():
          try:
            canonical = canonicalize_iupac(seq)
            output_sequences.append(canonical)
            try:
              drawing = GlycoDraw(canonical, suppress=True)
              svg_drawings.append((canonical, svg_to_base64(drawing)))
            except Exception as e:
              svg_drawings.append((canonical, None))
          except Exception as e:
            output_sequences.append(f"Error with '{seq}': {str(e)}")
            svg_drawings.append((seq, None))

      st.text_area("Canonicalized Sequences", "\n".join(output_sequences), height=200)
      # Display drawings in a scrollable area if any drawings were created
      if any(drawing for _, drawing in svg_drawings):
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

        for sequence, drawing in svg_drawings:
          if drawing:
            glycan_html += f'<div class="glycan-item"><p><b>{sequence}</b></p>'
            glycan_html += f'<img src="data:image/svg+xml;base64,{drawing}" alt="{sequence}" style="max-width:100%;"/></div>'

        glycan_html += '</div>'
        st.markdown(glycan_html, unsafe_allow_html=True)
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
