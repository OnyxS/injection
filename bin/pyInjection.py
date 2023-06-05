import sys
import ast
import json
import argparse


class IllegalLine:
    def __init__(self, message, node, filename):
        self.message = message
        self.lineno = node.lineno
        self.filename = filename

    def to_dict(self):
        return {
            'message': self.message,
            'lineno': self.lineno,
            'filename': self.filename
        }


class Checker(ast.NodeVisitor):
    def __init__(self, filename):
        self.errors = []
        self.fixed_queries = []
        self.filename = filename

    def check_execute(self, node):
        if 'execute' in node.s.lower():
            return IllegalLine('Potentially unsafe SQL query', node, self.filename)
        return None

    def check_join(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'join':
                return IllegalLine('str.join called on SQL query', node, self.filename)
        return None

    def check(self, node, context=None):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
            error = self.check_execute(node.value)
            if error:
                self.errors.append(error)
                self.write_error_to_file(node.lineno, node.value.s)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Str):
            error = self.check_execute(node.value)
            if error:
                if isinstance(node.targets[0], ast.Name):
                    assignment_node = find_assignment_in_context(node.targets[0].id, context)
                    if assignment_node:
                        self.fixed_queries.append((assignment_node.value, node.value))
                self.errors.append(error)
                self.write_error_to_file(node.lineno, node.value.s)

    def write_error_to_file(self, lineno, line):
        with open('error_log.txt', 'a') as f:
            f.write(f'Error in line {lineno}: {line}\n')

    def visit_Module(self, node):
        for stmt in node.body:
            self.check(stmt, context=node)

    def visit_FunctionDef(self, node):
        for stmt in node.body:
            self.check(stmt, context=node)

    def visit_Lambda(self, node):
        for stmt in node.body:
            self.check(stmt, context=node)

    def visit_With(self, node):
        for stmt in node.body:
            self.check(stmt, context=node)

    def visit_ClassDef(self, node):
        for stmt in node.body:
            self.check(stmt, context=node)

    def generic_visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
            elif isinstance(value, ast.AST):
                self.visit(value)

    def visit_Call(self, node):
        self.generic_visit(node)


def check(filename):
    with open(filename, 'r') as f:
        content = f.read()
    parsed = ast.parse(content, filename=filename)
    c = Checker(filename)
    c.visit(parsed)
    return c.errors, c.fixed_queries


def find_assignment_in_context(target, context):
    if not context:
        return None
    if isinstance(context, ast.Assign) and isinstance(context.targets[0], ast.Name) and context.targets[0].id == target:
        return context
    return find_assignment_in_context(target, getattr(context, 'context', None))


def main(args):
    if args.stdin:
        content = sys.stdin.read()
        parsed = ast.parse(content)
        files = [('<stdin>', *check(parsed))]
    elif args.input:
        with open(args.input, 'r') as f:
            files = [(line.strip(), *check(line.strip())) for line in f.readlines()]
    else:
        files = [(filename, *check(filename)) for filename in args.files]

    json_output = args.json
    fix = args.fix
    output_file = args.output

    total_errors = 0
    total_fixed_queries = 0

    for fname, file_errors, file_fixed_queries in files:
        total_errors += len(file_errors)
        if not json_output:
            if len(file_errors) > 0:
                print('Errors in file: %s' % fname)
                for error in file_errors:
                    print('Line %d: %s' % (error.lineno, error.message))
                print()

        if fix and len(file_fixed_queries) > 0:
            total_fixed_queries += len(file_fixed_queries)
            if not json_output:
                print('Fixed queries:')
                for old_query, new_query in file_fixed_queries:
                    print('Before: %s' % old_query.s)
                    print('After: %s' % new_query.s)

    if json_output:
        output_data = {
            'total_errors': total_errors,
            'total_fixed_queries': total_fixed_queries,
            'files': [
                {
                    'filename': fname,
                    'errors': [error.to_dict() for error in file_errors],
                    'fixed_queries': [
                        {
                            'old_query': old_query.s,
                            'new_query': new_query.s
                        }
                        for old_query, new_query in file_fixed_queries
                    ]
                }
                for fname, file_errors, file_fixed_queries in files
            ]
        }
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(output_data, f)
        else:
            print(json.dumps(output_data, indent=4))

    return total_errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pyInjection.py', description='Detect SQL injection in Python code.')
    parser.add_argument('files', nargs='*', help='files or directories to check')
    parser.add_argument('-i', '--input', metavar='file', help='input file with list of files to check')
    parser.add_argument('-j', '--json', action='store_true', help='output results in JSON format')
    parser.add_argument('-s', '--stdin', action='store_true', help='read from standard input')
    parser.add_argument('-f', '--fix', action='store_true', help='output fixed queries')
    parser.add_argument('-o', '--output', metavar='file', help='output file to save the results')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    sys.exit(main(args))
