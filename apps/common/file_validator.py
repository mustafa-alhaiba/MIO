import zipfile
from django.conf import settings
from django.core.exceptions import ValidationError


PDF_MAGIC = b"%PDF"
ZIP_MAGIC = b"PK\x03\x04" 

MAX_UPLOAD_BYTES = getattr(settings, "CONTRACT_DOCUMENT_MAX_BYTES", 10 * 1024 * 1024)  

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _read_header(file_obj: object, n: int = 8) -> bytes:
    header = file_obj.read(n)
    file_obj.seek(0)
    return header


def _is_pdf(header: bytes) -> bool:
    return header[:4] == PDF_MAGIC


def _is_docx_zip(header: bytes) -> bool:
    return header[:4] == ZIP_MAGIC


def _docx_structure_valid(file_obj) -> bool:
    try:
        with zipfile.ZipFile(file_obj) as zf:
            valid = "[Content_Types].xml" in zf.namelist()
    except zipfile.BadZipFile:
        valid = False
    finally:
        file_obj.seek(0)
    return valid

def validate_contract_document(file_obj) -> None:
    file_obj.seek(0, 2)          
    size = file_obj.tell()
    file_obj.seek(0)

    if size > MAX_UPLOAD_BYTES:
        mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        raise ValidationError(
            f"Document exceeds the {mb} MB size limit "
            f"(received {size / (1024 * 1024):.1f} MB)."
        )

    if size == 0:
        raise ValidationError("Uploaded file is empty.")

    header = _read_header(file_obj)

    if _is_pdf(header):
        return  

    if _is_docx_zip(header):
        if not _docx_structure_valid(file_obj):
            raise ValidationError(
                "File has a ZIP signature but is not a valid DOCX document. "
                "Upload a proper .docx file."
            )
        return

    raise ValidationError(
        "Only PDF and DOCX files are accepted. "
        "The uploaded file does not match either format's binary signature."
    )