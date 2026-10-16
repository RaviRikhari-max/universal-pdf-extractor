import streamlit as st
import fitz  # PyMuPDF
import io

# Set up page configurations
st.set_page_config(page_title="Geometric PDF Reader", page_icon="📄", layout="wide")

st.title("📄 Geometric Boundary-Sorted PDF Extractor")
st.write("Extracts actual text values by sorting every visual text block strictly by its physical top-to-bottom and left-to-right coordinates.")
st.divider()

# File Uploader
uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    st.subheader("📝 Extracted Content (Physical Layout Sorting)")
    
    with st.spinner("Extracting and sorting layout blocks..."):
        try:
            # Open PDF from in-memory bytes
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_document_output = []
            
            for page_num, page in enumerate(doc):
                full_document_output.append(f"=== PAGE {page_num + 1} ===")
                
                # Get text structural blocks: returns a list of tuples containing coordinate details
                # Block format: (x0, y0, x1, y1, "text inside the block", block_no, block_type)
                blocks = page.get_text("blocks")
                
                if not blocks:
                    full_document_output.append("[No text detected on this page - it might be an un-OCR'd scanned image]")
                    continue
                
                # Sort blocks: Primary sort by vertical position (y0), Secondary sort by horizontal position (x0)
                # Setting an alignment threshold (rounding) helps group elements that sit on roughly the same horizontal level
                sorted_blocks = sorted(blocks, key=lambda b: (round(b[1], 1), b[0]))
                
                page_text_lines = []
                for b in sorted_blocks:
                    block_text = b[4].strip()  # Index 4 holds the actual string text value
                    if block_text:
                        page_text_lines.append(block_text)
                
                # Join the sorted text lines for the current page
                full_document_output.append("\n\n".join(page_text_lines))
                
            # Compile text across all pages
            final_extracted_text = "\n\n\n".join(full_document_output)
            
            # Display text in a clean monospace code box to hold layout spacing
            st.code(final_extracted_text, language="text")
            
            # Download Button for the cleaned text content
            st.download_button(
                label="📥 Download Sorted Text File",
                data=final_extracted_text,
                file_name="sorted_layout_output.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Failed to process text coordinates: {e}")
else:
    st.info("Upload a PDF file to begin extracting visual blocks.")
