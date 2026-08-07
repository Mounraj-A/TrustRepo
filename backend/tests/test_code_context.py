from app.models.code.code_context import CodeContext


def main():

    context = CodeContext()

    print("=" * 60)
    print("CODE CONTEXT")
    print("=" * 60)

    print()

    print("Source Files        :", len(context.source_files))
    print("Parsed Files        :", len(context.parsed_files))
    print("AST Nodes           :", len(context.ast_nodes))
    print("Symbols             :", len(context.symbols))
    print("Relationships       :", len(context.relationships))
    print("Intermediate IR     :", context.intermediate_representation)
    print("Metadata            :", context.metadata)


if __name__ == "__main__":
    main()