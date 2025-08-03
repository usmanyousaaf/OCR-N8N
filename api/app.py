from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import pytesseract
from pdf2image import convert_from_bytes
import io
import os
from tempfile import NamedTemporaryFile

app = FastAPI()

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/ocr")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    try:
        # Verify file is PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Read the PDF file
        pdf_bytes = await file.read()
        
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes)
        
        # Extract text from each page
        extracted_text = []
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            extracted_text.append({
                "page": i + 1,
                "text": text.strip()
            })
        
        return JSONResponse(content={
            "filename": file.filename,
            "pages": extracted_text,
            "status": "success"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)