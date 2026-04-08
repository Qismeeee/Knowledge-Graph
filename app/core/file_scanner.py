import hashlib
from dataclasses import dataclass, field
from pathlib import Path

SKIP_DIRS = frozenset({
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", "vendor", ".next", ".nuxt", "target",
    "bin", "obj", ".tox", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "coverage", ".terraform",
})

SKIP_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".bmp", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".zip", ".tar", ".gz", ".bz2", ".rar", ".7z",
    ".exe", ".dll", ".so", ".dylib", ".pyc", ".pyo", ".class", ".o", ".a",
    ".db", ".sqlite", ".sqlite3",
    ".lock",
})

LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".go": "go",
    ".java": "java",
    ".cs": "csharp",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".xml": "xml",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".less": "less",
    ".md": "markdown",
    ".rst": "rst",
    ".sql": "sql",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".proto": "protobuf",
    ".graphql": "graphql",
    ".gql": "graphql",
    ".tf": "terraform",
    ".hcl": "hcl",
    ".vue": "vue",
    ".svelte": "svelte",
}

FILENAME_MAP: dict[str, str] = {
    "Dockerfile": "dockerfile",
    "Makefile": "makefile",
    "Jenkinsfile": "groovy",
    "Vagrantfile": "ruby",
    ".gitignore": "gitignore",
    ".dockerignore": "dockerignore",
    ".editorconfig": "editorconfig",
}

MAX_FILE_SIZE = 1_048_576  # 1MB


@dataclass
class ScannedFile:
    path: str
    language: str
    sha256: str
    loc: int


@dataclass
class ScanResult:
    files: list[ScannedFile] = field(default_factory=list)
    skipped: int = 0


class FileScanner:
    def scan(self, repo_path: Path) -> ScanResult:
        result = ScanResult()
        for file_path in self._walk(repo_path):
            relative = file_path.relative_to(repo_path).as_posix()
            scanned = self._process_file(file_path, relative)
            if scanned:
                result.files.append(scanned)
            else:
                result.skipped += 1
        return result

    def _walk(self, root: Path) -> list[Path]:
        files: list[Path] = []
        for entry in sorted(root.iterdir()):
            if entry.is_dir():
                if entry.name not in SKIP_DIRS:
                    files.extend(self._walk(entry))
            elif entry.is_file():
                files.append(entry)
        return files

    def _process_file(self, file_path: Path, relative: str) -> ScannedFile | None:
        if file_path.suffix.lower() in SKIP_EXTENSIONS:
            return None
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return None

        language = self._detect_language(file_path)
        try:
            content = file_path.read_bytes()
        except OSError:
            return None

        sha256 = hashlib.sha256(content).hexdigest()
        try:
            text = content.decode("utf-8", errors="strict")
            loc = sum(1 for line in text.splitlines() if line.strip())
        except UnicodeDecodeError:
            return None

        return ScannedFile(path=relative, language=language, sha256=sha256, loc=loc)

    def _detect_language(self, file_path: Path) -> str:
        if file_path.name in FILENAME_MAP:
            return FILENAME_MAP[file_path.name]
        return LANGUAGE_MAP.get(file_path.suffix.lower(), "unknown")
