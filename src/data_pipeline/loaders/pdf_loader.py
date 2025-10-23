"""
PDF Loader - Domain Agnostic

This loader works with ANY PDF documents, not just tourism guides.
Configure source directory and metadata fields in .env

Examples:
    - Tourism: Peru, Chile, Argentina tourism guides
    - Legal: Regulations, policies, laws
    - Academic: Research papers, textbooks
    - Corporate: Internal reports, manuals

Design Principles:
    - Configuration over hardcoding
    - Dependency injection for custom behavior
    - Minimal assumptions about document structure
    - Extensible for multiple domains

References:
    - LLM Engineer's Handbook (Ch 3): "Build Modular Data Pipelines"
    - Clean Architecture: Dependency Inversion Principle
"""

import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pypdf
from pydantic import BaseModel, Field

# Configure structured logging
logger = logging.getLogger(__name__)


class Document(BaseModel):
    """
    Document model - domain agnostic.
    
    Attributes:
        text: Extracted text content
        metadata: Dictionary of metadata (minimal by default)
        page_content: Alias for text (LangChain compatibility)
    """
    text: str = Field(..., description="Extracted text content from document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Document metadata (filename, path, custom fields)"
    )
    
    @property
    def page_content(self) -> str:
        """Alias for LangChain compatibility."""
        return self.text


class PDFLoader:
    """
    Domain-agnostic PDF loader with configurable behavior.
    
    This loader accepts any PDF structure and allows custom metadata extraction.
    It does NOT hardcode domain-specific logic (e.g., "departamento", "categoria").
    
    Args:
        source_dir: Path to directory containing PDFs (configurable)
        recursive: Whether to search subdirectories recursively
        file_pattern: Pattern to match PDF files (default: "*.pdf")
        metadata_extractor: Optional function to extract custom metadata
        encodings: List of encodings to try (default: ['utf-8', 'latin-1'])
    
    Example:
        >>> # Basic usage (tourism PDFs)
        >>> loader = PDFLoader(source_dir="./Complementarios Peru")
        >>> docs = loader.load_documents()
        
        >>> # Custom domain (legal docs)
        >>> def extract_legal_metadata(path, text):
        >>>     return {"tipo_norma": "ley", "fecha": "2024"}
        >>> loader = PDFLoader(
        >>>     source_dir="./legal_docs",
        >>>     metadata_extractor=extract_legal_metadata
        >>> )
        >>> docs = loader.load_documents()
    """
    
    def __init__(
        self,
        source_dir: str,
        recursive: bool = True,
        file_pattern: str = "*.pdf",
        metadata_extractor: Optional[Callable[[str, str], Dict[str, Any]]] = None,
        encodings: Optional[List[str]] = None,
    ):
        """Initialize PDF loader with configuration."""
        self.source_dir = Path(source_dir)
        self.recursive = recursive
        self.file_pattern = file_pattern
        self.metadata_extractor = metadata_extractor
        self.encodings = encodings or ['utf-8', 'latin-1']
        
        # Validate source directory exists
        if not self.source_dir.exists():
            raise ValueError(f"Source directory does not exist: {self.source_dir}")
        
        if not self.source_dir.is_dir():
            raise ValueError(f"Source path is not a directory: {self.source_dir}")
        
        logger.info(
            f"PDFLoader initialized",
            extra={
                "source_dir": str(self.source_dir),
                "recursive": self.recursive,
                "file_pattern": self.file_pattern,
            }
        )
    
    def find_pdf_files(self) -> List[Path]:
        """
        Find all PDF files matching the pattern.
        
        Returns:
            List of Path objects for found PDFs
        """
        if self.recursive:
            # Search recursively
            pdf_files = list(self.source_dir.rglob(self.file_pattern))
        else:
            # Search only in immediate directory
            pdf_files = list(self.source_dir.glob(self.file_pattern))
        
        logger.info(
            f"Found {len(pdf_files)} PDF files",
            extra={"count": len(pdf_files), "pattern": self.file_pattern}
        )
        
        return pdf_files
    
    def load_single_pdf(self, pdf_path: Path) -> Optional[Document]:
        """
        Load a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Document object or None if loading failed
        """
        try:
            # Extract text from PDF
            text = self._extract_text(pdf_path)
            
            if not text or not text.strip():
                logger.warning(
                    f"Empty text extracted from PDF",
                    extra={"path": str(pdf_path)}
                )
                return None
            
            # Build minimal metadata (always present)
            metadata = self._build_metadata(pdf_path, text)
            
            # Create document
            document = Document(text=text, metadata=metadata)
            
            logger.info(
                f"Successfully loaded PDF",
                extra={
                    "path": str(pdf_path),
                    "text_length": len(text),
                    "metadata_fields": list(metadata.keys())
                }
            )
            
            return document
            
        except Exception as e:
            logger.error(
                f"Failed to load PDF",
                extra={"path": str(pdf_path), "error": str(e)},
                exc_info=True
            )
            return None
    
    def load_documents(self) -> List[Document]:
        """
        Load all PDF documents from source directory.
        
        Returns:
            List of Document objects
        """
        pdf_files = self.find_pdf_files()
        documents = []
        
        for pdf_path in pdf_files:
            doc = self.load_single_pdf(pdf_path)
            if doc is not None:
                documents.append(doc)
        
        logger.info(
            f"Loaded {len(documents)} documents",
            extra={
                "total_files": len(pdf_files),
                "successful": len(documents),
                "failed": len(pdf_files) - len(documents)
            }
        )
        
        return documents
    
    def _extract_text(self, pdf_path: Path) -> str:
        """
        Extract text from PDF with multiple encoding attempts.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text
        
        Raises:
            Exception if all encoding attempts fail
        """
        for encoding in self.encodings:
            try:
                with open(pdf_path, 'rb') as file:
                    reader = pypdf.PdfReader(file)
                    
                    # Extract text from all pages
                    text_parts = []
                    for page_num, page in enumerate(reader.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text_parts.append(page_text)
                        except Exception as e:
                            logger.warning(
                                f"Failed to extract text from page",
                                extra={
                                    "path": str(pdf_path),
                                    "page": page_num,
                                    "error": str(e)
                                }
                            )
                    
                    text = "\n\n".join(text_parts)
                    
                    # Try to decode with current encoding
                    _ = text.encode(encoding)
                    
                    logger.debug(
                        f"Successfully extracted text with encoding {encoding}",
                        extra={"path": str(pdf_path), "encoding": encoding}
                    )
                    
                    return text
                    
            except (UnicodeDecodeError, UnicodeEncodeError) as e:
                logger.debug(
                    f"Encoding {encoding} failed, trying next",
                    extra={"path": str(pdf_path), "encoding": encoding}
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error during text extraction",
                    extra={"path": str(pdf_path), "error": str(e)},
                    exc_info=True
                )
                raise
        
        # All encodings failed
        raise ValueError(
            f"Failed to extract text from {pdf_path} with encodings: {self.encodings}"
        )
    
    def _build_metadata(self, pdf_path: Path, text: str) -> Dict[str, Any]:
        """
        Build metadata dictionary for document.
        
        This method builds minimal metadata by default (filename, path).
        If a custom metadata_extractor is provided, it adds those fields.
        
        Args:
            pdf_path: Path to PDF file
            text: Extracted text
        
        Returns:
            Metadata dictionary
        """
        # Minimal metadata (always present)
        metadata = {
            "filename": pdf_path.name,
            "filepath": str(pdf_path.absolute()),
            "file_size": pdf_path.stat().st_size,
            "source": "PDFLoader",
        }
        
        # Add custom metadata if extractor is provided
        if self.metadata_extractor is not None:
            try:
                custom_metadata = self.metadata_extractor(str(pdf_path), text)
                metadata.update(custom_metadata)
                
                logger.debug(
                    f"Added custom metadata",
                    extra={
                        "path": str(pdf_path),
                        "custom_fields": list(custom_metadata.keys())
                    }
                )
            except Exception as e:
                logger.warning(
                    f"Custom metadata extraction failed",
                    extra={"path": str(pdf_path), "error": str(e)}
                )
        
        return metadata


# Utility function for common use case
def load_pdfs_from_directory(
    directory: str,
    recursive: bool = True,
    metadata_extractor: Optional[Callable] = None
) -> List[Document]:
    """
    Convenience function to load PDFs from a directory.
    
    Args:
        directory: Path to directory containing PDFs
        recursive: Whether to search recursively
        metadata_extractor: Optional custom metadata extractor
    
    Returns:
        List of Document objects
    
    Example:
        >>> docs = load_pdfs_from_directory("./Complementarios Peru")
        >>> print(f"Loaded {len(docs)} documents")
    """
    loader = PDFLoader(
        source_dir=directory,
        recursive=recursive,
        metadata_extractor=metadata_extractor
    )
    return loader.load_documents()
