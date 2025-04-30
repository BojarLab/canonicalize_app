import streamlit as st
from glycowork.motif.processing import canonicalize_iupac

def main():
  st.title("IUPAC Sequence Canonicalizer")
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

if __name__ == "__main__":
  main()
