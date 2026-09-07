from pathlib import Path


DATA_DIR = Path("data")
DIRS_TO_CLEAN = [
    DATA_DIR / "raw",
    DATA_DIR / "processed",
]


def clean_directory(directory: Path) -> None:
    """Supprime récursivement les fichiers tout en conservant les dossiers."""

    if not directory.exists():
        print(f"Dossier inexistant : {directory}")
        return

    for file in directory.rglob("*"):
        if file.is_file():
            file.unlink()
            print(f"Supprimé : {file}")


def main() -> None:
    for directory in DIRS_TO_CLEAN:
        clean_directory(directory)

    print("Nettoyage terminé.")


if __name__ == "__main__":
    main()