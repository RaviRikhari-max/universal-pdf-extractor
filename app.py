import streamlit as st
import pdfplumber
import io

# Set up page configurations
st.set_page_config(page_title="Visual PDF Extractor", page_icon="📄", layout="wide")

st.title("📄 Visual PDF Snapshot Extractor")
st.write("Extracts text exactly how it visually looks on the PDF page, ignoring the PDF's internal reading order boundaries.")
st.divider()

# File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    st.subheader("🤖 Visual Match Output Preview")
    st.info("Text below is grouped and printed strictly by its vertical and horizontal coordinates on the page.")
    
    with st.spinner("Mapping visual layout coordinates..."):
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                full_text_blocks = []
                
                for page_num, page in enumerate(pdf.pages):
                    full_text_blocks.append(f"--- VISUAL PAGE {page_num + 1} ---")
                    
                    # Extract words with their exact spatial coordinates (x0, y0, text)
                    words = page.extract_words()
                    
                    if not words:
                        continue
                        
                    # Group words into lines that share roughly the same vertical alignment (y-coordinate)
                    # We round the top coordinate to group words on the exact same text line
                    lines = {}
                    for w in words:
                        # Rounding to 0 decimals forces words on the same line to stay together
                        y_coordinate = round(w['top'], 0) 
                        
                        if y_coordinate not in lines:
                            lines[y_coordinate] = []
                        lines[y_coordinate].append(w)
                    
                    # Sort lines from the top of the page down to the bottom
                    sorted_y = sorted(lines.keys())
                    
                    page_output = []
                    for y in sorted_y:
                        # For each line, sort the words strictly from left to right
                        line_words = sorted(lines[y], key=lambda w: w['x0'])
                        
                        # Reconstruct the line text exactly as it visually sits from left to right
                        line_text = " ".join([w['text'] for w in line_words])
                        page_output.append(line_text)
                        
                    full_text_blocks.append("\n".join(page_output))
                
                final_visual_text = "\n\n".join(full_text_blocks)
            
            # Display text in a code frame to respect line breaks and raw horizontal alignment
            st.code(final_visual_text, language="text")
            
            # Download button for the visual matched output
            st.download_button(
                label="📥 Download Visual Layout Text File",
                data=final_visual_text,
                file_name="visual_snapshot_layout.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Error parsing layout coordinates: {e}")
else:
    st.info("Upload your PDF to isolate the visual layout alignment.")
