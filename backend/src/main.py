from fastapi import FastAPI, File, UploadFile

app = FastAPI(
    title="Patent API",
    description="API for patent management and processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/patent")
async def upload_patent(file: UploadFile = File(...)):
    """
    Upload a PDF file for patent processing.
    
    Args:
        file: PDF file to upload
        
    Returns:
        Hardcoded response string
    """
    # Validate file type
    if file.content_type != "application/pdf":
        return {"error": "File must be a PDF"}
    
    # Return hardcoded string
    return {"message": "Patent file received successfully", "status": "processed"}