import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pytesseract
from app.services.ai_factory import AIServiceFactory


class DocumentService:
    """Service for document analysis and processing"""

    def __init__(self):
        self.supported_formats = {
            'pdf': self._extract_pdf,
            'docx': self._extract_docx,
            'doc': self._extract_docx,
            'txt': self._extract_txt,
            'png': self._extract_image,
            'jpg': self._extract_image,
            'jpeg': self._extract_image,
        }

    async def extract_text(self, file_path: str) -> str:
        """
        Extract text from various document formats

        Args:
            file_path: Path to document file

        Returns:
            Extracted text

        Raises:
            ValueError: If file format is not supported
        """
        file_extension = file_path.split('.')[-1].lower()

        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")

        extractor = self.supported_formats[file_extension]
        return await extractor(file_path)

    async def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        reader = PdfReader(file_path)

        for page in reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()

    async def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()

    async def _extract_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    async def _extract_image(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='tur+eng')
            return text.strip()
        except Exception as e:
            return f"Error extracting text from image: {str(e)}"

    async def analyze_document(
        self,
        file_path: str,
        custom_prompt: Optional[str] = None,
        ai_provider: Optional[str] = None,
    ) -> dict:
        """
        Extract and analyze document using AI

        Args:
            file_path: Path to document
            custom_prompt: Custom analysis prompt
            ai_provider: AI provider to use

        Returns:
            Dictionary with extracted_text, summary, and analysis
        """
        # Extract text
        extracted_text = await self.extract_text(file_path)

        if not extracted_text or len(extracted_text) < 10:
            return {
                "extracted_text": extracted_text,
                "summary": "Document appears to be empty or text extraction failed.",
                "analysis": "Unable to analyze document.",
            }

        # Get AI service
        ai_service = AIServiceFactory.get_service(ai_provider)

        # Generate summary
        summary = await ai_service.summarize(extracted_text)

        # Generate analysis
        analysis = await ai_service.analyze_document(extracted_text, custom_prompt)

        return {
            "extracted_text": extracted_text,
            "summary": summary,
            "analysis": analysis,
        }

    def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        stat = os.stat(file_path)
        extension = file_path.split('.')[-1].lower()

        return {
            "filename": os.path.basename(file_path),
            "file_type": extension,
            "file_size": stat.st_size,
            "is_supported": extension in self.supported_formats,
        }
