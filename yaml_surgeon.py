import argparse
from yaml_surgeon.yaml_operation import YamlOperation


def main():
    parser = argparse.ArgumentParser(description='Process and modify a yaml file')

    parser.add_argument('--filePath', type=str, help='Path to the yaml file')
    parser.add_argument('--name', type=str, help='Name of the node to select')
    parser.add_argument('--childOf', type=str, help='Select only children of a node with this name')
    parser.add_argument('--duplicate', type=str, help='Copies the selected node and its children, giving it this name')
    parser.add_argument('--rename', type=str, help='What to rename the selected to')
    parser.add_argument('--delete', action='store_true', help='Delete the selected nodes')

    args = parser.parse_args()
    print(f"Opening {args.filePath}")
    with open(args.filePath, 'r') as file:
        text = file.read()
    operation = YamlOperation(text)
    if args.name:
        operation.named(args.name)
    if args.childOf:
        operation.with_parents(args.childOf)
    if args.duplicate:
        operation.duplicate_as(args.duplicate)
    if args.rename:
        operation.rename(args.rename)
    elif args.delete:
        operation.delete()
    lines = operation.execute()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
