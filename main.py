from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil

app = FastAPI()

# 📁 Create upload folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 🧪 In-memory test applications and uploads
test_applications = {
    "1234567890": "ABCD1234EF",  #1 id: reference
    "1122334455": "ABCDEFG123" , #2 id: reference 
    "1472583690": "SALLOT1234" , #3 id: reference
}

# Track uploads: { "id": [list of car sides uploaded] }
upload_tracking = {}

# ✅ Validate ID and reference
@app.get("/api/policies/confirmation/{id}/{reference}")
def confirm(id: str, reference: str):
    if id not in test_applications or test_applications[id] != reference:
        raise HTTPException(status_code=404, detail="Application not found")

    count = len(upload_tracking.get(id, []))
    return {
        "status": True,
        "can_upload": count < 6,
        "uploaded_count": count
    }

# 📤 Upload endpoint
@app.post("/api/policies/uploading/{id}/{reference}/{car_side}")
async def upload_image(id: str, reference: str, car_side: str, file: UploadFile = File(...)):
    if id not in test_applications or test_applications[id] != reference:
        raise HTTPException(status_code=404, detail="Application not found")

    # Prevent >6 uploads
    current_uploads = upload_tracking.get(id, [])
    if len(current_uploads) >= 6:
        raise HTTPException(status_code=403, detail="Upload limit reached")

    # Save file
    filename = f"{id}_{car_side}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update tracking
    current_uploads.append(car_side)
    upload_tracking[id] = current_uploads

    return {
        "status": True,
        "message": "Upload successful",
        "file_path": f"/uploads/{filename}"
    }
