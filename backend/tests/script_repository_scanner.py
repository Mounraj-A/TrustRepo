from app.services.ingestion.repository_scanner import RepositoryScanner

scanner = RepositoryScanner()

repository_path = "mock_path"

results = scanner.scan_repository(repository_path)

print("\n")

for category, files in results.items():

    print("=" * 60)
    print(category.upper())
    print("=" * 60)

    if not files:
        print("No files found.\n")
        continue

    for file in files:
        print(file)

    print()