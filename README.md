
# ast_scope

This package is an implementation of Python's lexical scoping rules. It's interface is simple, you pass in an AST object to the `annotate` function, and it provides a mapping from each node in the tree that represents a symbol to the containing scope.

## Example Usage

Let's say you have the code

```
code = """
def f():
    x = 3
    lambda z: theta
    return x + y
"""
```

and you want to determine which global variables are referenced by it. All you need to do is run

```
import ast
import ast_scope
tree = ast.parse(code)
scope_info = ast_scope.annotate(tree)
global_variables = sorted(scope_info.global_scope.symbols_in_frame)
```

Once you have executed this code, `global_variables` will be bound to `['f', 'theta', 'y']`.
