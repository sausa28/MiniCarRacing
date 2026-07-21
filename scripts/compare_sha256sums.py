from pathlib import Path
import hashlib

def main():
    paths = ["data", "AsphaltDuell/data"]
    hashfiles: dict[str, list[str]] = {}

    for path in paths:
        add_hashes_from_path(Path(path), hashfiles)

    print("These files are equivalent:")
    for files in sorted(hashfiles.values()):
        if len(files) > 1:
            print(files)


def add_hashes_from_path(path: Path, hashfiles: dict[str, list[str]]):
    for file in path.glob("*.dat"):
        with file.open("rb") as f:
            data = f.read()
        hash = hashlib.sha256(data).hexdigest()
        if hashfiles.get(hash) is None:
            hashfiles[hash] = [str(file)]
        else:
            hashfiles[hash].append(str(file))
            hashfiles[hash].sort()
    

if __name__ == "__main__":
    main()
