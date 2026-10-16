import streamlit as st
import pdfplumber
import fitz  # PyMuPDF
import io
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

# Set up page configurations
st.set_page_config(page_title="Universal PDF Extractor", page_icon="📄", layout="wide")

st.title("📄 Universal PDF Layout & OCR Extractor")
st.write("Extract text from **both native and scanned/image PDFs** while preserving spatial layout, alignment, and formatting.")
st.divider()

# File Uploader
uploaded_file = st.file_uploader("Choose any PDF file (Native or Scanned)", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    # 1. Automatic Type Detection Pipeline
    st.sidebar.header("🔍 Document Inspector")
    with st.spinner("Inspecting PDF type..."):
        doc_test = fitz.open(stream=file_bytes, filetype="pdf")
        has_text = any(len(page.get_text().strip()) > 0 for page in doc_test)
        pdf_type = "Native (Selectable Text)" if has_text else "Scanned / Image-Only (OCR Required)"
        
    st.sidebar.metric(label="Detected PDF Structure", value=pdf_type)
    
    # Selection modes based on user goals
    extraction_mode = st.sidebar.radio(
        "Choose Priority Mode:",
        ["Preserve Alignment (Text Layout)", "Preserve Formatting & Web View"]
    )
    
    # ----------------------------------------------------
    # ROUTE A: PROCESSING NATIVE TEXT PDFs
    # ----------------------------------------------------
    if has_text:
        if extraction_mode == "Preserve Alignment (Text Layout)":
            st.subheader("🤖 Native Text Alignment View")
            with st.spinner("Extracting multi-column layout..."):
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    full_text = [f"--- PAGE {i+1} ---\n{page.extract_text(layout=True) or ''}" for i, page in enumerate(pdf.pages)]
                final_out = "\n\n".join(full_text)
                st.code(final_out, language="text")
                st.download_button("📥 Download Text Layout File", final_out, "layout.txt", "text/plain")

        elif extraction_mode == "Preserve Formatting & Web View":
            st.subheader("🎨 Native Rich Text View")
            with st.spinner("Parsing typography layers..."):
                html_content = "".join([page.get_text("html") for page in doc_test])
            st.components.v1.html(html_content, height=600, scrolling=True)
            st.download_button("📥 Download Formatted Page (.html)", html_content, "formatting.html", "text/html")

    # ----------------------------------------------------
    # ROUTE B: PROCESSING SCANNED PDFs via OCR
    # ----------------------------------------------------
    else:
        st.warning("⚠️ This document appears to be a scanned image. Activating the OCR Pipeline...")
        
        if extraction_mode == "Preserve Alignment (Text Layout)":
            st.subheader("⚙️ OCR Spatial Layout Extractor")
            st.info("Converting document pages into image maps to calculate text spacing benchmarks...")
            
            with st.spinner("Running high-resolution OCR layout processing..."):
                try:
                    images = convert_from_bytes(file_bytes, dpi=200)
                    ocr_layout_text = []
                    
                    for idx, img in enumerate(images):
                        page_text = pytesseract.image_to_string(img, config='--psm 3')
                        ocr_layout_text.append(f"--- OCR PAGE {idx+1} ---\n{page_text}")
                    
                    final_ocr_out = "\n\n".join(ocr_layout_text)
                    st.code(final_ocr_out, language="text")
                    st.download_button("📥 Download OCR Extracted Layout", final_ocr_out, "ocr_layout.txt", "text/plain")
                except Exception as e:
                    st.error(f"OCR Failed. Verify that your environment has system-level Tesseract and Poppler dependencies configured. Error: {e}")

        elif extraction_mode == "Preserve Formatting & Web View":
            st.subheader("🌐 OCR Rich Text Formatting (hOCR)")
            st.info("Extracting layout text wrapped inside standard web hierarchy styles.")
            
            with st.spinner("Generating hOCR formatting documents..."):
                try:
                    images = convert_from_bytes(file_bytes, dpi=200)
                    hocr_content = ""
                    
                    for img in images:
                        hocr_page = pytesseract.image_to_pdf_or_hocr(img, extension='hocr')
                        hocr_content += hocr_page.decode('utf-8')
                        
                    st.components.v1.html(hocr_content, height=600, scrolling=True)
                    st.download_button("📥 Download hOCR Document (.html)", hocr_content, "ocr_format.html", "text/html")
                except Exception as e:
                    st.error(f"OCR Formatting failed. Error verification: {e}")
else:
    st.info("Upload any document above to trigger the auto-detection workflow.")
