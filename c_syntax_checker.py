"""
=============================================================================
C Syntax Checker
=============================================================================
Module 1 – Main Function Validation
    Check 1 : Program must have int main() or void main()
    Check 2 : main() must be followed by opening '{'
    Check 2.5: return statement must exist inside main() body
    Check 3 : Stack-based curly-bracket balancing

Module 2 – Statement Analyser (line-by-line inside main body)
    Step A : Tokenise each line
    Step B : Identify statement type
               DECLARATION  – int / float / char / double / long / short
               IF           – if(...)
               FOR          – for(...)
               WHILE        – while(...)
               PRINTF       – printf(...)
               SCANF        – scanf(...)
               ASSIGNMENT   – identifier = expression
               ARITHMETIC   – expression without assignment
               RETURN       – return ...
    Step C : Per-type validation
               • Variable name valid (starts with letter/_, no spaces mid-name)
               • '=' must not appear before the variable name
               • Invalid operator combinations: *+  *-  /+  /-  +*  -*
               • Invalid post-increment usage: i++b  i++*5
               • Missing semicolon at end of statement
               • Unmatched parentheses  ( )
=============================================================================
"""

import re
import sys


class CSyntaxChecker:

    # ── Data tables ────────────────────────────────────────────────────────
    TYPE_KEYWORDS = {'int', 'float', 'double', 'char', 'long', 'short',
                     'unsigned', 'signed', 'void'}

    # Operator combinations that are never valid
    INVALID_OP_COMBOS = [
        (r'\*\+',          '*+'),
        (r'\*-(?![=>])',   '*-'),
        (r'/\+',           '/+'),
        (r'/-(?![=>])',    '/-'),
        (r'\+\*(?!=)',     '+*'),
        (r'-\*(?![=>])',   '-*'),
    ]

    # Post-increment/decrement immediately followed by identifier (e.g. i++b, a--c)
    INVALID_POSTFIX = [
        (r'\+\+\s*[a-zA-Z_]',  'i++<identifier>  (e.g. i++b)'),
        (r'--\s*[a-zA-Z_]',    'i--<identifier>  (e.g. a--b)'),
    ]

    def __init__(self):
        self.errors = []

    # ==================================================================== #
    #  Entry Points
    # ==================================================================== #
    def check_file(self, filename):
        try:
            with open(filename, 'r') as f:
                content = f.read()
            self.check_content(content)
            return self.errors
        except FileNotFoundError:
            return [f"Error: File '{filename}' not found"]

    def check_content(self, content):
        self.errors = []
        self.check_main(content)        # Module 1
        self.check_statements(content)  # Module 2

    # ==================================================================== #
    #  MODULE 1 – Main Function Validation
    # ==================================================================== #
    def check_main(self, content):
        code = self._strip_comments(content)
        lines = code.split('\n')

        # ── Check 1: signature ─────────────────────────────────────────
        main_match = re.search(r'\b(int|void)\s+main\s*\(', code)

        if not main_match:
            self.errors.append(
                "Error: Program must have a valid main function — "
                "'int main()' or 'void main()'"
            )
            self._bracket_stack(lines, main_line=None)
            return

        return_type  = main_match.group(1)
        main_line_no = self._line_of(code, main_match.start())

        if return_type == 'void':
            self.errors.append(
                f"Warning (Line {main_line_no}): 'void main()' found — "
                f"prefer 'int main()' for standard C"
            )

        # ── Check 2: opening '{' ───────────────────────────────────────
        open_pos = code.find('{', main_match.end())
        if open_pos == -1:
            self.errors.append(
                f"Error (Line {main_line_no}): "
                f"main() must be followed by an opening '{{'"
            )
            return

        # ── Check 2.5: 'return' inside body ───────────────────────────
        depth = 0
        body_end = None
        for i in range(open_pos, len(code)):
            if code[i] == '{':
                depth += 1
            elif code[i] == '}':
                depth -= 1
                if depth == 0:
                    body_end = i
                    break

        if body_end is None:
            self.errors.append(
                f"Error (Line {main_line_no}): "
                f"Unclosed '{{' — main() body is never closed"
            )
        else:
            body = code[open_pos + 1: body_end]
            if not re.search(r'\breturn\b', body):
                if return_type == 'int':
                    self.errors.append(
                        f"Error (Line {main_line_no}): "
                        f"'int main()' is missing a 'return' statement"
                    )
                else:
                    self.errors.append(
                        f"Warning (Line {main_line_no}): "
                        f"'void main()' has no 'return' — optional but recommended"
                    )

        # ── Check 3: bracket stack ─────────────────────────────────────
        self._bracket_stack(lines, main_line=main_line_no)

    def _bracket_stack(self, lines, main_line):
        stack = []
        main_brace_found = False
        for line_no, line in enumerate(lines, start=1):
            for col, ch in enumerate(line, start=1):
                if ch == '{':
                    stack.append(line_no)
                    if main_line and line_no >= main_line and not main_brace_found:
                        main_brace_found = True
                elif ch == '}':
                    if not stack:
                        self.errors.append(
                            f"Error (Line {line_no}, Col {col}): "
                            f"Unmatched '}}' — no matching opening '{{'"
                        )
                    else:
                        stack.pop()
        for open_line in stack:
            self.errors.append(
                f"Error (Line {open_line}): Unclosed '{{' — missing closing '}}'"
            )
        if main_line and not main_brace_found:
            self.errors.append(
                f"Error (Line {main_line}): main() must be followed by opening '{{'"
            )

    def check_statements(self, content):
        """
        For every non-blank, non-comment line:
          A. Tokenise → identify statement type
          B. Run per-type checks
          C. Run universal checks (operators, semicolons, parens)
        """
        code  = self._strip_comments(content)
        lines = code.split('\n')

        for line_no, raw in enumerate(lines, start=1):
            line = raw.strip()

            # Skip blanks, preprocessor, pure braces, main signature
            if (not line
                    or line.startswith('#')
                    or line in ('{', '}', '};')
                    or re.match(r'\b(int|void)\s+main\s*\(', line)):
                continue

            stmt_type = self._identify_statement(line)
            self._validate_statement(line_no, line, stmt_type)

    # ------------------------------------------------------------------ #
    #  Step A+B : Tokenise & Identify
    # ------------------------------------------------------------------ #
    def _tokenise(self, line):
        """
        Split line into tokens:
          - identifiers / keywords   [a-zA-Z_]\w*
          - numbers                  \d+(\.\d+)?
          - compound operators       +=  -=  *=  /=  %=  ==  !=  <=  >=  ++  --
          - single char operators    + - * / % = < > ! & | ^ ~ ? :
          - punctuation              ( ) [ ] { } ; ,
        """
        pattern = r'[a-zA-Z_]\w*|\d+(?:\.\d+)?|[+\-*/%&|^~]=|[<>!]=|[+][+]|--|&&|\|\||[+\-*/%=<>!&|^~?:()\[\]{};,"]'
        return re.findall(pattern, line)

    def _identify_statement(self, line):
        """Return statement type string based on the first meaningful token."""
        tokens = self._tokenise(line)
        if not tokens:
            return 'EMPTY'

        first = tokens[0]

        if first in self.TYPE_KEYWORDS:
            return 'DECLARATION'
        if first == 'if':
            return 'IF'
        if first == 'else':
            return 'ELSE'
        if first == 'for':
            return 'FOR'
        if first == 'while':
            return 'WHILE'
        if first == 'printf':
            return 'PRINTF'
        if first == 'scanf':
            return 'SCANF'
        if first == 'return':
            return 'RETURN'
        if first in ('break', 'continue'):
            return 'CONTROL_FLOW'
        # Assignment: identifier followed by = (but not == != <= >=)
        if (re.match(r'^[a-zA-Z_]\w*', line)
                and re.search(r'(?<![=!<>])=(?!=)', line)):
            return 'ASSIGNMENT'
        return 'ARITHMETIC'

    # ------------------------------------------------------------------ #
    #  Step C : Validate per statement type
    # ------------------------------------------------------------------ #
    def _validate_statement(self, line_no, line, stmt_type):
        """Dispatch to the right validator, then run universal checks."""

        if stmt_type == 'DECLARATION':
            self._check_declaration(line_no, line)

        elif stmt_type == 'IF':
            self._check_control_keyword(line_no, line, 'if')

        elif stmt_type == 'FOR':
            self._check_for(line_no, line)

        elif stmt_type == 'WHILE':
            self._check_control_keyword(line_no, line, 'while')

        elif stmt_type in ('PRINTF', 'SCANF'):
            self._check_io_function(line_no, line, stmt_type.lower())

        elif stmt_type == 'ASSIGNMENT':
            self._check_assignment(line_no, line)

        elif stmt_type == 'ARITHMETIC':
            self._check_arithmetic(line_no, line)

        # Universal checks on every statement
        self._check_invalid_operators(line_no, line)
        self._check_invalid_postfix(line_no, line)
        self._check_semicolon(line_no, line, stmt_type)
        self._check_paren_balance(line_no, line)

    # ── DECLARATION  (e.g. int a = 5;  char name[10];) ────────────────
    def _check_declaration(self, line_no, line):
        tokens = self._tokenise(line)
        if len(tokens) < 2:
            self.errors.append(
                f"Error (Line {line_no}): Declaration missing variable name"
            )
            return

        var_name = tokens[1]

        # Variable name must start with letter or _
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
            self.errors.append(
                f"Error (Line {line_no}): Invalid variable name '{var_name}' — "
                f"must start with a letter or '_'"
            )

        # '=' must NOT appear before the variable name on the line
        before_var = line[:line.find(var_name)]
        if '=' in before_var:
            self.errors.append(
                f"Error (Line {line_no}): '=' appears before variable name '{var_name}'"
            )

    # ── IF / WHILE  (e.g. if(x > 0)  while(i < 10)) ───────────────────
    def _check_control_keyword(self, line_no, line, keyword):
        # Must have '(' right after keyword
        if not re.search(rf'\b{keyword}\s*\(', line):
            self.errors.append(
                f"Error (Line {line_no}): '{keyword}' must be followed by '('"
            )
            return

        # Condition inside () must not be empty
        match = re.search(rf'\b{keyword}\s*\(([^)]*)\)', line)
        if match and not match.group(1).strip():
            self.errors.append(
                f"Error (Line {line_no}): '{keyword}' has empty condition '()'"
            )

    # ── FOR  (e.g. for(i=0; i<10; i++)) ───────────────────────────────
    def _check_for(self, line_no, line):
        if not re.search(r'\bfor\s*\(', line):
            self.errors.append(
                f"Error (Line {line_no}): 'for' must be followed by '('"
            )
            return

        match = re.search(r'\bfor\s*\(([^)]*)\)', line)
        if not match:
            self.errors.append(
                f"Error (Line {line_no}): 'for' loop has unmatched parentheses"
            )
            return

        body = match.group(1)
        parts = body.split(';')
        if len(parts) != 3:
            self.errors.append(
                f"Error (Line {line_no}): 'for' loop needs exactly 2 semicolons "
                f"inside () — got {len(parts)-1}  →  for(init; condition; update)"
            )

    # ── PRINTF / SCANF ─────────────────────────────────────────────────
    def _check_io_function(self, line_no, line, fname):
        if not re.search(rf'\b{fname}\s*\(', line):
            self.errors.append(
                f"Error (Line {line_no}): '{fname}' must be followed by '('"
            )
            return

        # Must have at least one argument (a string literal for printf/scanf)
        match = re.search(rf'\b{fname}\s*\(([^)]*)\)', line)
        if match:
            args = match.group(1).strip()
            if not args:
                self.errors.append(
                    f"Error (Line {line_no}): '{fname}' called with no arguments"
                )
            elif not args.startswith('"'):
                self.errors.append(
                    f"Error (Line {line_no}): '{fname}' first argument should be "
                    f"a string literal starting with '\"'"
                )

    # ── ASSIGNMENT  (e.g. a = b + 5;  x += 3;) ────────────────────────
    def _check_assignment(self, line_no, line):
        tokens = self._tokenise(line)
        if not tokens:
            return

        lhs = tokens[0]

        # Left-hand side must be a valid identifier
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', lhs):
            self.errors.append(
                f"Error (Line {line_no}): Invalid identifier '{lhs}' "
                f"on left-hand side of assignment"
            )

        # '=' must not be the very first token (i.e., = a = 5  is wrong)
        if line.lstrip().startswith('='):
            self.errors.append(
                f"Error (Line {line_no}): Statement begins with '=' — "
                f"'=' cannot appear before the variable name"
            )

        # Compound operators: +=  -=  *=  /=  %=  are all valid
        # But the RHS must not be empty
        assign_match = re.search(r'(?<![=!<>])=(?!=)\s*$', line.rstrip(';').rstrip())
        if assign_match:
            self.errors.append(
                f"Error (Line {line_no}): Assignment has no right-hand side value"
            )

    # ── ARITHMETIC  (e.g. a + b * c) ───────────────────────────────────
    def _check_arithmetic(self, line_no, line):
        # Expression must not start with a binary operator (not unary - or !)
        if re.match(r'^\s*[+*/%]', line):
            self.errors.append(
                f"Error (Line {line_no}): Expression starts with invalid operator"
            )

    # ── Universal: invalid operator combinations ────────────────────────
    def _check_invalid_operators(self, line_no, line):
        # Remove string literals first to avoid false positives
        cleaned = re.sub(r'"[^"]*"', '""', line)
        for pattern, label in self.INVALID_OP_COMBOS:
            if re.search(pattern, cleaned):
                self.errors.append(
                    f"Error (Line {line_no}): Invalid operator combination '{label}'"
                )

    # ── Universal: invalid post-increment/decrement ─────────────────────
    def _check_invalid_postfix(self, line_no, line):
        cleaned = re.sub(r'"[^"]*"', '""', line)
        # Check for i++b, a--c (identifier directly after ++/--)
        for pattern, label in self.INVALID_POSTFIX:
            if re.search(pattern, cleaned):
                self.errors.append(
                    f"Error (Line {line_no}): Invalid post-increment/decrement usage "
                    f"'{label}'"
                )
        # Check for incrementing constants: 5++, 10--
        if re.search(r'\b\d+\s*(\+\+|--)\b', cleaned):
            self.errors.append(
                f"Error (Line {line_no}): Cannot apply increment/decrement to a constant (e.g. 5++ or 10-- is invalid)"
            )
        # Check for incrementing non-modifiable lvalues: (a+b)++, (x*2)--
        if re.search(r'\([^\)]+\)\s*(\+\+|--)\b', cleaned):
            self.errors.append(
                f"Error (Line {line_no}): Cannot apply increment/decrement to a non-modifiable lvalue (e.g. (a+b)++ is invalid)"
            )
        # Check for double increment/decrement: i++++, i----
        if re.search(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(\+\+){2,}', cleaned) or re.search(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(--){2,}', cleaned):
            self.errors.append(
                f"Error (Line {line_no}): Invalid double increment/decrement (e.g. i++++ is invalid)"
            )

    # ── Universal: semicolon at end ─────────────────────────────────────
    def _check_semicolon(self, line_no, line, stmt_type):
        # These statement types don't end with ';'
        NO_SEMI = {'IF', 'ELSE', 'FOR', 'WHILE', 'EMPTY', 'CONTROL_FLOW'}
        if stmt_type in NO_SEMI:
            return
        # Lines ending with '{' or '}' don't need ';'
        stripped = line.rstrip()
        if stripped.endswith(('{', '}')):
            return
        if not stripped.endswith(';'):
            self.errors.append(
                f"Error (Line {line_no}): Missing semicolon ';' at end of "
                f"{stmt_type} statement"
            )

    # ── Universal: parenthesis balance ──────────────────────────────────
    def _check_paren_balance(self, line_no, line):
        depth = 0
        for col, ch in enumerate(line, start=1):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth < 0:
                    self.errors.append(
                        f"Error (Line {line_no}, Col {col}): "
                        f"Unmatched ')' — no opening '('"
                    )
                    return
        if depth > 0:
            self.errors.append(
                f"Error (Line {line_no}): Unclosed '(' — missing closing ')'"
            )

    # ==================================================================== #
    #  Helpers
    # ==================================================================== #
    def _strip_comments(self, code):
        """Remove // single-line and /* */ block comments."""
        code = re.sub(r'//[^\n]*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

    def _line_of(self, content, pos):
        return content[:pos].count('\n') + 1

    # ==================================================================== #
    #  Output
    # ==================================================================== #
    def print_errors(self):
        if not self.errors:
            print("✓ No syntax errors found!")
        else:
            print(f"Found {len(self.errors)} issue(s):")
            for e in self.errors:
                prefix = "⚠️ " if e.startswith("Warning") else "❌ "
                print(f"  {prefix}{e}")


# ======================================================================== #
#  CLI entry point
# ======================================================================== #
def main():
    if len(sys.argv) != 2:
        print("Usage: python c_syntax_checker.py <c_file>")
        return
    checker = CSyntaxChecker()
    filename = sys.argv[1]
    print(f"Checking: {filename}")
    print("=" * 50)
    checker.check_file(filename)
    checker.print_errors()


if __name__ == "__main__":
    main()
