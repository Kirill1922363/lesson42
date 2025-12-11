from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime

app = FastAPI()

UPLOAD_FOLDER = 'uploads'
MAX_SIZE = 5 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

photos = []

@app.post('/photos/upload')
async def upload_photo(file: UploadFile = File(...)):
    if not file.filename.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(400, 'Тільки JPEG та PNG')
    
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, 'Максимум 5MB')
    
    ext = file.filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, new_filename)
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    photo = {
        'filename': new_filename,
        'url': f'/photos/{new_filename}',
        'date': datetime.now().isoformat()
    }
    photos.append(photo)
    
    return photo

@app.get('/photos/list')
def list_photos():
    sorted_photos = sorted(photos, key=lambda p: p['date'], reverse=True)
    return sorted_photos

@app.get('/photos/{filename}')
def get_photo(filename: str):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(404, 'Не знайдено')
    
    return FileResponse(filepath)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)