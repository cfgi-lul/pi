from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Patent API",
    description="API for patent management and processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS to allow requests from Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular default port
        "http://127.0.0.1:4200",  # Alternative localhost format
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    # Flat object with only extracted material specification info (no status, message, patent, abstract, or filename)
    return {
        "application_number": "US20241234567A1",
        "title": "Novel Composite Material for Lightweight Structures",
        "applicant": "Jane Doe",
        "filing_date": "2024-06-12",
        "material_name": "Carbon Fiber Reinforced Polymer",
        "composition_1_component": "Carbon Fiber",
        "composition_1_percentage": 65.0,
        "composition_1_unit": "wt%",
        "composition_2_component": "Epoxy Resin",
        "composition_2_percentage": 35.0,
        "composition_2_unit": "wt%",
        "density_value": 1.6,
        "density_unit": "g/cm^3",
        "tensile_strength_value": 2500,
        "tensile_strength_unit": "MPa",
        "youngs_modulus_value": 150,
        "youngs_modulus_unit": "GPa",
        "manufacturing_method": "Lay-up and autoclave curing"
    }