import tokenize
import subprocess
import tempfile
from pathlib import Path

language_to_filetype = {
    "python": "py",
    "javascript": "js",
    "java": "java",
    "csharp": "cs",
    "cpp": "cpp",
    "rust": "rs",
    "go": "go",
    "ruby": "rb",
    "php": "php",
    "swift": "swift",
    "kotlin": "kt"
}

supported_languages = {
    "python", 
    "rust"
}

def validate_python_file(path: str) -> bool:
    try:
        with tokenize.open(path) as file:
            source = file.read()
        compile(source, str(path), "exec")
        return True
    except (SyntaxError, OSError, UnicodeError) as error:
        print(f"Invalid Python file: {error}")
        return False


def validate_rust_file(path: str) -> bool:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "validation.rmeta"
            result = subprocess.run(
                [
                    "rustc",
                    "--crate-type=lib",
                    "--edition=2021",
                    "--emit=metadata",
                    "-o",
                    str(output_path),
                    str(path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
    except FileNotFoundError:
        print("Cannot validate Rust: rustc was not found. Install Rust first.")
        return False
    except OSError as error:
        print(f"Could not run rustc: {error}")
        return False

    if result.returncode == 0:
        return True

    diagnostic = result.stderr.strip() or result.stdout.strip()
    print(f"Invalid Rust file {path}:\n{diagnostic}")
    return False

def validate_file(path:str):
    ext = Path(path).suffix[1:]
    if ext == "py":
        return validate_python_file(path)
    elif ext == "rs":
        return validate_rust_file(path)
    else:
        print(f"Validation for {ext} files is not supported.")
        return False
