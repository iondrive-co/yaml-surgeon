import argparse
from yaml_surgeon.yaml_operation import YamlOperation


def main():
    parser = argparse.ArgumentParser(description='Process and modify a yaml file')

    parser.add_argument('--filePath', type=str, help='Path to the yaml file')
    parser.add_argument('--named', nargs='+', type=str, help='Name of the node to select')
    parser.add_argument('--nameContains', nargs='+', type=str, help='Name of the node to select contains this')
    parser.add_argument('--namedAtLevel', nargs='2', type=str, help='Name of the node to select and its level')
    parser.add_argument('--withParents', nargs='+', type=str, help='Select only children of a node with this name')
    parser.add_argument('--withParentAtLevel', nargs='2', type=str, help='Name of the node to select and its level')
    parser.add_argument('--rename', type=str, help='What to rename the selected to')
    parser.add_argument('--delete', action='store_true', help='Delete the selected nodes')
    parser.add_argument('--duplicateAs', type=str, help='Copies the selected node and its children, giving it this name')
    parser.add_argument('--insertSibling', type=str, help='Inserts a sibling node for the selected with this name')

    args = parser.parse_args()
    print(f"Opening {args.filePath}")
    with open(args.filePath, 'r') as file:
        text = file.read()
    operation = YamlOperation(text)
    if args.named:
        operation.named(args.named)
    if args.nameContains:
        operation.name_contains(args.nameContains)
    if args.namedAtLevel:
        operation.named_at_level(args.namedAtLevel[0], args.namedAtLevel[1])
    if args.withParents:
        operation.with_parents(args.withParents)
    if args.withParentAtLevel:
        operation.with_parent_at_level(args.withParentAtLevel[0], args.withParentAtLevel[1])
    if args.rename:
        operation.rename(args.rename)
    if args.delete:
        operation.delete()
    if args.duplicateAs:
        operation.duplicate_as(args.duplicateAs)
    if args.insertSibling:
        operation.insert_sibling(args.insertSibling)

    lines = operation.execute()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
