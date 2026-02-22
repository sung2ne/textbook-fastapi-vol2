import os
import uuid
import shutil
from pathlib import Path
from PIL import Image
from fastapi import UploadFile, HTTPException

from app.config import settings

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_SIZE = settings.MAX_UPLOAD_SIZE  # 5MB


async def save_image(file: UploadFile, folder: str = "products") -> str:
    """이미지 저장"""
    # 확장자 확인
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "지원하지 않는 이미지 형식입니다")

    # 파일 크기 확인
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, f"파일 크기는 {MAX_SIZE // 1024 // 1024}MB 이하여야 합니다")

    # 고유 파일명 생성
    filename = f"{uuid.uuid4().hex}{ext}"

    # 폴더 생성
    folder_path = UPLOAD_DIR / folder
    folder_path.mkdir(exist_ok=True)

    # 파일 저장
    file_path = folder_path / filename
    with open(file_path, "wb") as f:
        f.write(content)

    # 이미지 최적화
    optimize_image(file_path)

    return f"/uploads/{folder}/{filename}"


def optimize_image(file_path: Path, max_width: int = 1200) -> None:
    """이미지 최적화 (리사이즈, 압축)"""
    try:
        with Image.open(file_path) as img:
            # EXIF 방향 정보 적용
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)

            # 너무 크면 리사이즈
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            # RGB로 변환 (PNG 투명 처리)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # 압축 저장
            img.save(file_path, "JPEG", quality=85, optimize=True)
    except Exception as e:
        print(f"이미지 최적화 실패: {e}")


def delete_image(url: str) -> bool:
    """이미지 삭제"""
    if not url.startswith("/uploads/"):
        return False

    file_path = Path(url.replace("/uploads/", str(UPLOAD_DIR) + "/"))
    if file_path.exists():
        file_path.unlink()
        return True
    return False
