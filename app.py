import streamlit as st
import fitz  # PyMuPDF
import io

# Set up page configurations
st.set_page_config(page_title="Universal Layout OCR Reader", page_icon="📄", layout="wide")

st.title("📄 Universal Layout & OCR Geometric Extractor")
st.write("Extracts actual text values from **both selectable and scanned image PDFs** by sorting text zones strictly by spatial coordinates.")
st.divider()

# File Uploader
uploaded_file = st.file_uploader("Upload your PDF file (Native or Scanned)", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    st.subheader("📝 Extracted Text (Sorted Geometric Layout)")
    
    with st.spinner("Analyzing document layers and running OCR if needed..."):
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_document_output = []
            
            for page_num, page in enumerate(doc):
                full_document_output.append(f"=== PAGE {page_num + 1} ===")
                
                # Check if the page has native text. If not, trigger OCR via Tesseract automatically
                text_check = page.get_text().strip()
                
                if not text_check:
                    # Page is a scanned image. Use PyMuPDF's built-in Tesseract OCR engine mapping
                    # "tp" extracts text positions via layout analysis
                    try:
                        pix = page.get_pixmap(dpi=150)
                        ocr_doc = fitz.open("pdf", pix.pdfocr_tobytes())
                        page = ocr_doc[0]
                    except Exception as ocr_err:
                        full_document_output.append(f"[OCR Engine Error: Ensure packages.txt includes tesseract-ocr. Details: {ocr_err}]")
                        continue

                # Get spatial text blocks: (x0, y0, x1, y1, "text string", block_no, block_type)
                blocks = page.get_text("blocks")
                
                if not blocks:
                    full_document_output.append("[Empty block configuration detected on this page]")
                    continue
                
                # Group text blocks strictly by their physical top-to-bottom (y0) and left-to-right (x0) layout
                # Rounding coordinate integers prevents minor micro-misalignments from breaking sentence sequences
                sorted_blocks = sorted(blocks, key=lambda b: (round(b[1], 1), b[0]))
                
                page_text_lines = []
                for b in sorted_blocks:
                    block_text = b[4].strip() # Index 4 contains the extracted string value
                    if block_text:
                        page_text_lines.append(block_text)
                        
                full_document_output.append("\n\n".join(page_text_lines))
                
            # Compile text across all pages
            final_extracted_text = "\n\n\n".join(full_document_output)
            
            # Display text inside a code container to respect structural alignment and lines
            st.code(final_extracted_text, language="text")
            
            # Download Button
            st.download_button(
                label="📥 Download Extracted Layout & OCR Text",
                data=final_extracted_text,
                file_name="universal_ocr_layout_output.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Processing structural layout pipeline failed: {e}")
else:
    st.info("Upload any document to process structural character recognition.")
