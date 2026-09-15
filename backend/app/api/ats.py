from io import BytesIO

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from pypdf import PdfReader

from app.ats.schemas import ATSAnalyzeResponse
from app.ats.service import analyze_resume
from app.core.security import get_current_user


router = APIRouter(
    prefix="/api/v1/ats",
    tags=["ATS Analysis"],
)


def _get_user_id(current_user) -> int:
    """
    Extract the authenticated user's ID.

    Supports both SQLAlchemy user objects and dictionary-like
    user representations.
    """

    if hasattr(current_user, "id"):
        return int(current_user.id)

    if isinstance(current_user, dict):
        if "id" in current_user:
            return int(current_user["id"])

        if "user_id" in current_user:
            return int(current_user["user_id"])

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to determine authenticated user.",
    )


@router.post(
    "/analyze",
    response_model=ATSAnalyzeResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_resume_endpoint(
    file: UploadFile = File(...),
    job_description: str | None = Form(default=None),
    current_user=Depends(get_current_user),
):
    """
    Analyze a resume against an optional job description.

    Authentication is required.

    The authenticated user's ID is passed to the ATS service so
    the latest ATS result can be persisted and later used by
    the placement-readiness system.
    """

    user_id = _get_user_id(current_user)

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resumes are supported.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Validate PDF.
    try:
        reader = PdfReader(BytesIO(file_bytes))
        page_count = len(reader.pages)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unreadable PDF file.",
        ) from exc

    try:
        result = analyze_resume(
            file_bytes=file_bytes,
            filename=file.filename,
            page_count=page_count,
            job_description=job_description,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return result