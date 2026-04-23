import re
import sys

class CSyntaxChecker:
    def __init__(self):
        self.keywords = {
            'int', 'float', 'double', 'char', 'void', 'long', 'short', 'unsigned', 'signed',
            'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default', 'break', 'continue',
            'return', 'goto', 'sizeof', 'typedef', 'struct', 'union', 'enum', 'const', 'static',
            'extern', 'auto', 'register', 'volatile'
        }
        self.operators = {'+', '-', '*', '/', '%', '++', '--', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '=', '+=', '-=', '*=', '/=', '%='}
        self.errors = []
        self.line_number = 0
        
    def check_file(self, filename):
        try:
            with open(filename, 'r') as file:
                content = file.read()
                self.check_content(content)
            return self.errors
        except FileNotFoundError:
            return [f"Error: File '{filename}' not found"]
    
    def check_content(self, content):
        lines = content.split('\n')
        self.line_number = 0
        
        for line in lines:
            self.line_number += 1
            self.check_line(line)
        
        self.check_global_structure(content)
        self.check_keyword_sequence(content)
    
    def check_line(self, line):
        stripped = line.strip()
        
        if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
            return
        
        self.check_brackets(line)
        self.check_semicolons(line)
        self.check_parentheses(line)
        self.check_square_brackets(line)
        self.check_invalid_characters(line)
        self.check_control_statements(line)
    
    def check_brackets(self, line):
        pass
    
    def check_parentheses(self, line):
        pass
    
    def check_square_brackets(self, line):
        pass
    
    def check_semicolons(self, line):
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
            return
        
        if any(keyword in stripped for keyword in ['if', 'while', 'for', 'switch', 'else', 'do']):
            return
        
        if '{' in stripped or '}' in stripped:
            return
        
        if ('=' in stripped and not stripped.startswith('#') and 
            not stripped.endswith(';') and not stripped.endswith('{') and 
            not stripped.endswith('}') and not stripped.endswith(')')):
            if any(op in stripped for op in ['==', '!=', '<=', '>=', '&&', '||']):
                return
            if not any(keyword in stripped for keyword in ['if', 'while', 'for']):
                self.errors.append(f"Line {self.line_number}: Missing semicolon in statement")
    
    def check_invalid_characters(self, line):
        invalid_chars = re.findall(r'[^\w\s\{\}\(\)\[\];,\.\+\-\*/%<>=!&|^~?:#\'"\\]', line)
        if invalid_chars:
            self.errors.append(f"Line {self.line_number}: Invalid character(s): {', '.join(set(invalid_chars))}")
    
    def check_control_statements(self, line):
        stripped = line.strip()
        
        if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
            return
        
        self.check_control_parentheses(stripped)
        self.check_for_loop_syntax(stripped)
        self.check_control_braces(stripped)
    
    def check_control_parentheses(self, line):
        control_keywords = ['if', 'while', 'for', 'switch']
        
        for keyword in control_keywords:
            pattern = rf'\b{keyword}\b\s*(?!\()'
            if re.search(pattern, line):
                self.errors.append(f"Line {self.line_number}: Missing parentheses after '{keyword}'")
        
        for keyword in control_keywords:
            pattern = rf'\b{keyword}\s*\(([^)]*)'
            matches = re.findall(pattern, line)
            for match in matches:
                if not match.strip():
                    self.errors.append(f"Line {self.line_number}: Empty condition in '{keyword}' statement")
    
    def check_for_loop_syntax(self, line):
        if 'for' in line:
            for_pattern = r'for\s*\(([^)]*)\)'
            match = re.search(for_pattern, line)
            if match:
                for_content = match.group(1).strip()
                parts = [part.strip() for part in for_content.split(';')]
                
                if len(parts) != 3:
                    self.errors.append(f"Line {self.line_number}: Invalid for loop syntax - expected 2 semicolons")
                else:
                    if parts[0] and not (re.match(r'^[a-zA-Z_]\w*\s*[a-zA-Z_]\w*\s*=\s*\w+', parts[0]) or 
                                       parts[0] in [';', ''] or re.match(r'^\s*[a-zA-Z_]\w+\s*$', parts[0])):
                        pass
    
    def check_control_braces(self, line):
        control_keywords = ['if', 'while', 'for', 'switch', 'else']
        
        for keyword in control_keywords:
            pattern = rf'\b{keyword}\b.*\{{'
            if re.search(pattern, line):
                next_brace = line.find('{', line.find(keyword))
                if next_brace != -1:
                    remaining = line[next_brace+1:]
                    if '}' not in remaining and ';' in remaining:
                        self.errors.append(f"Line {self.line_number}: Mixed brace and semicolon usage in '{keyword}' statement")
    
    def check_global_structure(self, content):
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            self.errors.append(f"Global: Unmatched braces. Found {open_braces} '{{' and {close_braces} '}}'")
        
        open_parens = content.count('(')
        close_parens = content.count(')')
        
        if open_parens != close_parens:
            self.errors.append(f"Global: Unmatched parentheses. Found {open_parens} '(' and {close_parens} ')'")
        
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        
        if open_brackets != close_brackets:
            self.errors.append(f"Global: Unmatched square brackets. Found {open_brackets} '[' and {close_brackets} ']'")
        
        self.check_function_declarations(content)
        self.check_string_literals(content)
    
    def check_function_declarations(self, content):
        functions = re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', content)
        
        for func in functions:
            if not any(keyword in func.split('(')[0] for keyword in self.keywords):
                parts = func.split('(')[0].strip().split()
                if len(parts) >= 2:
                    return_type, func_name = parts[0], parts[1]
                    if return_type not in self.keywords:
                        self.errors.append(f"Possible invalid return type '{return_type}' in function '{func_name}'")
    
    def check_string_literals(self, content):
        strings = re.findall(r'"[^"]*"', content)
        for string in strings:
            if string.count('"') % 2 != 0:
                self.errors.append(f"Unterminated string literal: {string}")
    
    def check_keyword_sequence(self, content):
        lines = content.split('\n')
        line_num = 0
        
        for line in lines:
            line_num += 1
            stripped = line.strip()
            
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                continue
            
            if 'else' in stripped and 'if' not in stripped:
                prev_lines = lines[:line_num-1]
                found_matching_if = False
                
                for prev_line in reversed(prev_lines[-10:]):
                    prev_stripped = prev_line.strip()
                    if 'if' in prev_stripped and 'else' not in prev_stripped:
                        found_matching_if = True
                        break
                    elif '{' in prev_stripped and '}' in prev_stripped:
                        break
                
                if not found_matching_if:
                    self.errors.append(f"Line {line_num}: 'else' without matching 'if'")
    
    def check_preprocessor_directives(self, content):
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                if not re.match(r'^#\s*(include|define|undef|ifdef|ifndef|if|else|elif|endif|pragma|error)\b', stripped):
                    self.errors.append(f"Line {i}: Invalid preprocessor directive: {stripped}")
    
    def print_errors(self):
        if not self.errors:
            print("✓ No syntax errors found!")
        else:
            print(f"Found {len(self.errors)} syntax error(s):")
            for error in self.errors:
                print(f"  ❌ {error}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python c_syntax_checker.py <c_file>")
        print("Example: python c_syntax_checker.py program.c")
        return
    
    filename = sys.argv[1]
    checker = CSyntaxChecker()
    
    print(f"Checking C file: {filename}")
    print("=" * 50)
    
    errors = checker.check_file(filename)
    checker.print_errors()

if __name__ == "__main__":
    main()
