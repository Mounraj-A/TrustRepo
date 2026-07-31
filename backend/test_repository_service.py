from app.services.ingestion.repository_service import RepositoryService

service = RepositoryService()

print("=" * 60)
print("Repository Service Loaded From")
print("=" * 60)
print(service.__class__.__module__)
print("=" * 60)

github_url = input("Enter GitHub Repository URL: ")

print("\n")

clone_result = service.clone_repository(github_url)

print("=" * 60)
print("Clone Result")
print("=" * 60)

for key, value in clone_result.items():
    print(f"{key}: {value}")

print("\n")

metadata = service.get_repository_metadata(
    clone_result["repository_name"]
)

print("=" * 60)
print("Metadata Object")
print("=" * 60)
print(metadata)
print(type(metadata))

if metadata is not None:
    print("\nRepository Metadata")
    print("=" * 60)

    for key, value in metadata.items():
        print(f"{key}: {value}")