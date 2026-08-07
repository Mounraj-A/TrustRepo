from app.models.code.source_file import SourceFile


def main():

    source = SourceFile(
        path="src/app.py",
        language="python",
        content="print('Hello World')",
        extension=".py",
        size=20,
    )

    print("=" * 60)
    print("SOURCE FILE MODEL")
    print("=" * 60)

    print()

    print("Path      :", source.path)
    print("Language  :", source.language)
    print("Extension :", source.extension)
    print("Size      :", source.size)
    print("Content   :", source.content)


if __name__ == "__main__":
    main()