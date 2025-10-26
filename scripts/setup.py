#!/usr/bin/env python
"""
Setup script for PeruGuide RAG project.

This script automates the initial setup:
1. Verifies Python version
2. Creates necessary directories
3. Validates .env configuration
4. Checks for HuggingFace token
5. Verifies PDFs in data/raw/
6. Provides next steps

Usage:
    python scripts/setup.py
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple


# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.END} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.END} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")


def check_python_version() -> bool:
    """Verify Python version >= 3.10."""
    print_header("Verificando Versión de Python")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version_str} - Versión compatible")
        return True
    else:
        print_error(f"Python {version_str} - Versión NO compatible")
        print_error("Se requiere Python 3.10 o superior")
        print_info("Descarga: https://www.python.org/downloads/")
        return False


def create_directories() -> bool:
    """Create necessary project directories."""
    print_header("Creando Directorios del Proyecto")
    
    directories = [
        "data/raw",
        "data/vector_stores",
        "logs",
        "deleteme"
    ]
    
    all_created = True
    for dir_path in directories:
        path = Path(dir_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Directorio creado/verificado: {dir_path}/")
        except Exception as e:
            print_error(f"Error creando {dir_path}: {e}")
            all_created = False
    
    return all_created


def check_env_file() -> Tuple[bool, List[str]]:
    """Check if .env file exists and has required variables."""
    print_header("Verificando Configuración (.env)")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    issues = []
    
    # Check if .env exists
    if not env_path.exists():
        if env_example_path.exists():
            print_warning("Archivo .env NO encontrado")
            print_info("Copia .env.example a .env:")
            print_info("  cp .env.example .env  (Linux/Mac)")
            print_info("  copy .env.example .env  (Windows)")
            issues.append("Falta archivo .env")
        else:
            print_error("No se encontró .env ni .env.example")
            issues.append("Falta .env.example")
        return False, issues
    
    print_success("Archivo .env encontrado")
    
    # Check for HuggingFace token
    huggingface_token = None
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('HUGGINGFACE_API_TOKEN'):
                huggingface_token = line.split('=')[1].strip()
                break
    
    if not huggingface_token or huggingface_token == 'hf_your_token_here' or huggingface_token == '':
        print_error("Token de HuggingFace NO configurado en .env")
        print_info("Obtén tu token gratis en: https://huggingface.co/settings/tokens")
        print_info("Edita .env y reemplaza: HUGGINGFACE_API_TOKEN=hf_tu_token_aqui")
        issues.append("Falta token de HuggingFace")
    else:
        print_success(f"Token de HuggingFace configurado (hf_...{huggingface_token[-10:]})")
    
    return len(issues) == 0, issues


def check_pdfs() -> Tuple[int, List[str]]:
    """Check for PDFs in data/raw/."""
    print_header("Verificando PDFs en data/raw/")
    
    raw_path = Path("data/raw")
    
    if not raw_path.exists():
        print_error("Directorio data/raw/ no existe")
        return 0, []
    
    pdf_files = list(raw_path.glob("*.pdf"))
    num_pdfs = len(pdf_files)
    
    if num_pdfs == 0:
        print_warning("No se encontraron PDFs en data/raw/")
        print_info("Coloca tus documentos PDF en data/raw/ para procesarlos")
    else:
        print_success(f"Encontrados {num_pdfs} archivos PDF")
        # Show first 5 PDFs
        for pdf in pdf_files[:5]:
            print(f"   • {pdf.name}")
        if num_pdfs > 5:
            print(f"   ... y {num_pdfs - 5} más")
    
    return num_pdfs, [pdf.name for pdf in pdf_files]


def check_vector_store() -> bool:
    """Check if vector store index exists."""
    print_header("Verificando Vector Store")
    
    index_path = Path("data/vector_stores/faiss_peru_guide.index")
    
    if index_path.exists():
        size_mb = index_path.stat().st_size / (1024 * 1024)
        print_success(f"Índice FAISS encontrado ({size_mb:.2f} MB)")
        return True
    else:
        print_warning("Índice FAISS NO encontrado")
        print_info("Ejecuta: python scripts/ingest_pdfs.py")
        return False


def print_next_steps(has_env: bool, num_pdfs: int, has_index: bool):
    """Print next steps based on setup status."""
    print_header("Próximos Pasos")
    
    step = 1
    
    if not has_env:
        print(f"{step}. {Colors.YELLOW}Configura tu .env{Colors.END}")
        print("   Edita .env y agrega tu token de HuggingFace")
        print("   https://huggingface.co/settings/tokens\n")
        step += 1
    
    if num_pdfs == 0:
        print(f"{step}. {Colors.YELLOW}Agrega PDFs{Colors.END}")
        print("   Coloca tus documentos en data/raw/\n")
        step += 1
    
    if not has_index and num_pdfs > 0:
        print(f"{step}. {Colors.YELLOW}Procesa los PDFs{Colors.END}")
        print("   python scripts/ingest_pdfs.py\n")
        step += 1
    
    if has_env and has_index:
        print(f"{step}. {Colors.GREEN}Inicia el servidor API{Colors.END}")
        print("   uvicorn src.api.main:app --reload --host localhost --port 8000\n")
        step += 1
        
        print(f"{step}. {Colors.GREEN}Inicia la interfaz web (en otra terminal){Colors.END}")
        print("   streamlit run app/streamlit_app.py\n")
        step += 1
        
        print(f"{step}. {Colors.GREEN}Abre tu navegador{Colors.END}")
        print("   http://localhost:8501\n")


def main():
    """Main setup function."""
    print(f"{Colors.BOLD}")
    print(r"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       🇵🇪  P E R U G U I D E   A I   S E T U P  🇵🇪       ║
    ║                                                           ║
    ║         Sistema RAG para Turismo en Perú                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(Colors.END)
    
    # Run checks
    python_ok = check_python_version()
    if not python_ok:
        print_error("\n❌ Setup cancelado: Python versión incorrecta\n")
        sys.exit(1)
    
    dirs_ok = create_directories()
    if not dirs_ok:
        print_error("\n❌ Setup cancelado: Error creando directorios\n")
        sys.exit(1)
    
    env_ok, env_issues = check_env_file()
    num_pdfs, pdf_list = check_pdfs()
    index_exists = check_vector_store()
    
    # Print summary
    print_header("Resumen del Setup")
    
    if python_ok:
        print_success("Python: Compatible")
    if dirs_ok:
        print_success("Directorios: Creados")
    
    if env_ok:
        print_success("Configuración: Completa")
    else:
        print_error(f"Configuración: Incompleta ({len(env_issues)} problemas)")
    
    if num_pdfs > 0:
        print_success(f"PDFs: {num_pdfs} encontrados")
    else:
        print_warning("PDFs: No encontrados")
    
    if index_exists:
        print_success("Vector Store: Listo")
    else:
        print_warning("Vector Store: Pendiente")
    
    # Print next steps
    print_next_steps(env_ok, num_pdfs, index_exists)
    
    # Final status
    if env_ok and num_pdfs > 0 and index_exists:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ¡Setup completo! El proyecto está listo para usar.{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Setup incompleto. Sigue los pasos de arriba.{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelado por el usuario{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.END}\n")
        sys.exit(1)
