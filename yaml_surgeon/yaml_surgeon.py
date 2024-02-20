import argparse
from yaml_surgeon.yaml_lexer import scan_text
from yaml_surgeon.yaml_parser import parse_line_tokens
from yaml_surgeon.yaml_operation import NodeSelector, NodeExecutor


def main():
    parser = argparse.ArgumentParser(description='Process and modify a yaml file')

    parser.add_argument('--filePath', type=str, help='Path to the yaml file')
    parser.add_argument('--name', type=str, help='Name of the node to select')
    parser.add_argument('--childOf', type=str, help='Select only children of a node with this name')
    parser.add_argument('--rename', type=str, help='What to rename the selected to')
    parser.add_argument('--delete', action='store_true', help='Delete the selected nodes')

    args = parser.parse_args()
    print(f"Opening {args.filePath}")
    with open(args.filePath, 'r') as file:
        text = file.read()
    lexed_lines = scan_text(text)
    parsed_yaml = parse_line_tokens(lexed_lines)
    selector = NodeSelector(parsed_yaml)
    if args.name:
        selector.named(args.name)
    if args.childOf:
        selector.parent(args.childOf)
    executor = NodeExecutor(selector, lexed_lines)
    if args.rename:
        executor = executor.rename(args.rename)
    elif args.delete:
        executor = executor.delete()
    lines = executor.execute()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
