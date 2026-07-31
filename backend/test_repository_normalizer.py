from app.services.ingestion.repository_scanner import RepositoryScanner
from app.services.ingestion.repository_normalizer import RepositoryNormalizer

scanner = RepositoryScanner()
normalizer = RepositoryNormalizer()

repository_path = input("Repository Path: ")

scan_results = scanner.scan_repository(repository_path)

normalized_results = normalizer.normalize(scan_results)

print()

for category, files in normalized_results.items():

    print("=" * 60)
    print(category.upper())
    print("=" * 60)

    if not files:
        print("No files found.\n")
        continue

    for file in files:
        print(file)

    print()