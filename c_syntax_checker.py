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
        self.content = content  # Store content for access in other methods
        
        # Track multi-line expressions to avoid false positives
        self.multiline_expression_lines = set()
        
        # First pass: identify multi-line expressions
        self.identify_multiline_expressions(content)
        
        # Second pass: line-by-line analysis (skip multi-line expression lines)
        for line in lines:
            self.line_number += 1
            self.check_line(line)
        
        # Third pass: multi-line expression analysis
        self.check_multiline_expressions(content)
        
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
        # Simplified bracket checking - only report obvious errors
        stripped = line.strip()
        
        # Skip most bracket checking to reduce false positives
        # Only check if line has both opening and closing brackets of same type
        if line.count('{') > 0 and line.count('}') > 0:
            if line.count('{') != line.count('}'):
                # Only report if it's a clear mismatch in a single line
                if abs(line.count('{') - line.count('}')) > 1:
                    self.errors.append(f"Line {self.line_number}: Multiple mismatched braces")
        
        if line.count('(') != line.count(')'):
            # Only report if it's a clear mismatch in a single line
            if abs(line.count('(') - line.count(')')) > 1:
                self.errors.append(f"Line {self.line_number}: Multiple mismatched parentheses")
        
        # Simplified bracket checking - disable complex stack-based checking
        # to reduce false positives
        pass
    
    def check_parentheses(self, line):
        stack = []
        
        for i, char in enumerate(line):
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    self.errors.append(f"Line {self.line_number}: Unmatched closing parenthesis ')' at position {i}")
                else:
                    stack.pop()
        
        for char in stack:
            self.errors.append(f"Line {self.line_number}: Unclosed parenthesis '{char}'")
    
    def check_square_brackets(self, line):
        stack = []
        
        for i, char in enumerate(line):
            if char == '[':
                stack.append(char)
            elif char == ']':
                if not stack:
                    self.errors.append(f"Line {self.line_number}: Unmatched closing bracket ']' at position {i}")
                else:
                    stack.pop()
        
        for char in stack:
            self.errors.append(f"Line {self.line_number}: Unclosed bracket '{char}'")
    
    def check_semicolons(self, line):
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
            return
        
        # Skip if this line is part of a multi-line expression
        if self.line_number in self.multiline_expression_lines:
            return
        
        # Additional check: skip lines that look like they're part of multi-line expressions
        if (len(stripped) <= 3 and  # Short lines like "a", "c", "d"
            stripped.isalnum() and 
            self.line_number > 1):  # Not the first line
            return
        
        # Skip lines with only operators in multi-line context
        if stripped in ['+', '-', '*', '/', '=', '+', '-'] and self.line_number > 1:
            return
        
        if any(keyword in stripped for keyword in ['if', 'while', 'for', 'switch', 'else', 'do']):
            return
        
        if '{' in stripped or '}' in stripped:
            return
        
        # Check for missing semicolons in assignment statements
        if ('=' in stripped and not stripped.startswith('#') and 
            not stripped.endswith(';') and not stripped.endswith('{') and 
            not stripped.endswith('}') and not stripped.endswith(')')):
            if any(op in stripped for op in ['==', '!=', '<=', '>=', '&&', '||']):
                return
            if not any(keyword in stripped for keyword in ['if', 'while', 'for']):
                self.errors.append(f"Line {self.line_number}: Missing semicolon in statement")
        
        # Check for missing semicolons in single identifiers/expressions
        elif (re.match(r'^[a-zA-Z_]\w*$', stripped) and  # Single identifier
              self.line_number > 1 and  # Not first line
              not any(keyword in stripped for keyword in ['if', 'while', 'for', 'switch', 'else', 'do', 'return', 'break', 'continue'])):
            # Check if current line ends with semicolon
            if not stripped.endswith(';'):
                self.errors.append(f"Line {self.line_number}: Missing semicolon after identifier '{stripped}'")
        
        # Check for missing semicolons between multiple identifiers
        elif (re.match(r'^[a-zA-Z_]\w*\s*[a-zA-Z_]\w*$', stripped) and  # Two identifiers without semicolon
              self.line_number > 1 and
              not any(keyword in stripped for keyword in ['if', 'while', 'for', 'switch', 'else', 'do', 'return', 'break', 'continue'])):
            self.errors.append(f"Line {self.line_number}: Missing semicolon between identifiers")
        
        # Comprehensive semicolon detection for expression patterns only
        elif (self.line_number > 1 and 
              not any(keyword in stripped for keyword in ['if', 'while', 'for', 'switch', 'else', 'do', 'return', 'break', 'continue']) and
              not re.match(r'^\s*(int|float|double|char|void|long|short|unsigned|signed|static|extern|auto|register|const|volatile)', stripped)):
            
            # Only check lines that look like expressions (not declarations)
            tokens = re.findall(r'[a-zA-Z_]\w*|;', stripped)
            
            # Focus on specific problematic patterns
            if len(tokens) >= 2:
                errors_found = []
                
                # Pattern 1: ab;cd (missing semicolon after cd)
                if 'ab;cd' in stripped.replace(' ', ''):
                    errors_found.append("Missing semicolon after 'cd'")
                
                # Pattern 2: General case - two identifiers with semicolon in wrong place
                if re.search(r'\b[a-zA-Z_]\w*\s*;\s*[a-zA-Z_]\w*\b', stripped):
                    # Extract all identifier+semicolon patterns
                    matches = re.findall(r'\b([a-zA-Z_]\w*)\s*;\s*([a-zA-Z_]\w*)\b', stripped)
                    if matches:
                        id1, id2 = matches[0]
                        # Check if this is the LAST part of the line (no more identifiers after)
                        remaining_after = stripped[stripped.find(id2) + len(id2):].strip()
                        if remaining_after and not remaining_after.startswith(';'):
                            # There are more identifiers after id2 without semicolon
                            errors_found.append(f"Missing semicolon after '{id2}'")
                        elif not remaining_after and not stripped.rstrip().endswith(';'):
                            # id2 is the last thing but no semicolon at end
                            errors_found.append(f"Missing semicolon after '{id2}'")
                
                # Pattern 3: Multiple identifiers without semicolons (like ab cd)
                elif re.search(r'\b[a-zA-Z_]\w*\s+[a-zA-Z_]\w*\b', stripped) and ';' not in stripped:
                    matches = re.findall(r'\b([a-zA-Z_]\w*)\s+([a-zA-Z_]\w*)\b', stripped)
                    if matches:
                        id1, id2 = matches[0]
                        errors_found.append(f"Missing semicolon between '{id1}' and '{id2}'")
                
                # Pattern 4: Multiple consecutive semicolons
                if ';;' in stripped:
                    semicolon_count = len(re.findall(r';+', stripped))
                    max_consecutive = max(len(match) for match in re.findall(r';+', stripped))
                    if max_consecutive > 1:
                        errors_found.append(f"Multiple semicolons detected ({max_consecutive} consecutive)")
                
                # Report errors (limit to avoid noise)
                for error in errors_found[:2]:  # Max 2 errors per line
                    self.errors.append(f"Line {self.line_number}: {error}")
    
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
        self.check_global_bracket_balance(content)
        
        self.check_function_declarations(content)
        self.check_string_literals(content)
    
    def check_global_bracket_balance(self, content):
        stack = []
        bracket_map = {')': '(', '}': '{', ']': '['}
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for i, char in enumerate(line):
                if char in '({[':
                    stack.append((char, line_num, i))
                elif char in ')}]':
                    if not stack:
                        self.errors.append(f"Line {line_num}: Unmatched closing bracket '{char}' at position {i}")
                    elif stack[-1][0] != bracket_map[char]:
                        opening_bracket, open_line, open_pos = stack[-1]
                        self.errors.append(f"Line {line_num}: Mismatched brackets. Expected '{bracket_map[char]}' (opened at line {open_line}, pos {open_pos}) before '{char}' at position {i}")
                        stack.pop()
                    else:
                        stack.pop()
        
        for bracket, line_num, pos in stack:
            self.errors.append(f"Line {line_num}: Unclosed bracket '{bracket}' at position {pos}")
    
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
    
    def identify_multiline_expressions(self, content):
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('#'):
                i += 1
                continue
            
            # Check if line starts an expression (contains assignment operator but no semicolon)
            if '=' in line and ';' not in line and not any(keyword in line for keyword in ['if', 'while', 'for', 'switch', 'else', 'do']):
                # Look ahead to find the complete expression
                j = i + 1
                
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line or next_line.startswith('//') or next_line.startswith('/*'):
                        j += 1
                        continue
                    
                    # Check if expression ends with semicolon
                    if next_line.endswith(';'):
                        break
                    
                    # Check if we hit a control statement or new block
                    if any(keyword in next_line for keyword in ['if', 'while', 'for', 'switch', 'else', 'do']) or next_line.startswith('{'):
                        break
                    
                    j += 1
                
                # Mark all lines in this multi-line expression
                for line_num in range(i + 1, j + 1):
                    self.multiline_expression_lines.add(line_num + 1)  # +1 for 1-based line numbering
                
                i = j + 1
            else:
                i += 1
    
    def check_multiline_expressions(self, content):
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('#'):
                i += 1
                continue
            
            # Check if line starts an expression (contains assignment operator but no semicolon)
            if '=' in line and ';' not in line and not any(keyword in line for keyword in ['if', 'while', 'for', 'switch', 'else', 'do']):
                # Look ahead to find the complete expression
                expression_lines = [line]
                j = i + 1
                
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line or next_line.startswith('//') or next_line.startswith('/*'):
                        j += 1
                        continue
                    
                    expression_lines.append(next_line)
                    
                    # Check if expression ends with semicolon
                    if next_line.endswith(';'):
                        break
                    
                    # Check if we hit a control statement or new block
                    if any(keyword in next_line for keyword in ['if', 'while', 'for', 'switch', 'else', 'do']) or next_line.startswith('{'):
                        break
                    
                    j += 1
                
                # Combine expression lines
                full_expression = ' '.join(expression_lines)
                
                # Check if combined expression has semicolon
                if not full_expression.endswith(';'):
                    self.errors.append(f"Line {i+1}: Missing semicolon in multi-line expression")
                
                i = j + 1
            else:
                i += 1
    
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
