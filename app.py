import streamlit as st
import urllib.parse
from glycowork.motif.processing import canonicalize_iupac

def main():
  st.title("IUPAC Glycan Sequence Canonicalizer")
  st.write("Paste your glycan sequences below to canonicalize them")
  
  input_text = st.text_area("Input Sequences (one per line)", height=200)
  
  if st.button("Convert"):
    if input_text:
      input_sequences = input_text.strip().split("\n")
      output_sequences = []
      
      for seq in input_sequences:
        if seq.strip():
          try:
            canonical = canonicalize_iupac(seq)
            output_sequences.append(canonical)
          except Exception as e:
            output_sequences.append(f"Error with '{seq}': {str(e)}")
      
      st.text_area("Canonicalized Sequences", "\n".join(output_sequences), height=200)
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
      repo_owner = "BojarLab"  # Replace with your organization name
      repo_name = "canonicalize_app"  # Replace with your repository name
      
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
*This issue was generated from the IUPAC Glycan Sequence Canonicalizer web app.*
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
