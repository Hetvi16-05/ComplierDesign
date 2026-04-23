# C Syntax Checker Documentation

## Overview
The C Syntax Checker is a Python program designed to detect common syntax errors in C source code. It performs line-by-line analysis and global structure validation to identify structural issues that would prevent compilation.

## Architecture

### Main Class: `CSyntaxChecker`
- **Purpose**: Central class that orchestrates all syntax checking functionality
- **Data Structures**: 
  - `self.keywords`: Set of C keywords for validation
  - `self.operators`: Set of C operators for pattern recognition
  - `self.errors`: List to store detected syntax errors
  - `self.line_number`: Integer to track current line being analyzed

### Core Data Structures Used

| Data Structure | Purpose | Location |
|---------------|---------|----------|
| **Set** | Store C keywords and operators for O(1) lookup | `__init__()` |
| **List** | Store error messages with line numbers | Throughout class |
| **String** | Line content manipulation and analysis | All check methods |
| **Regex Patterns** | Pattern matching for complex syntax detection | Multiple methods |

## Syntax Error Detection Methods

### 1. Missing Semicolons Detection
**Method**: `check_semicolons()`

**Data Structures Used**:
- **String**: Line content analysis
- **List**: Control statement keywords for exclusion

**Logic/Algorithm**:
1. Strip whitespace from line
2. Skip comments, preprocessor directives, and empty lines
3. Exclude control statements (`if`, `while`, `for`, `switch`, `else`, `do`)
4. Exclude lines with braces (`{`, `}`)
5. Check for assignment statements containing `=` but not ending with `;`
6. Filter out comparison operators (`==`, `!=`, `<=`, `>=`, `&&`, `||`)
7. Report error if semicolon is missing

**Code Pattern**:
```python
if ('=' in stripped and not stripped.startswith('#') and 
    not stripped.endswith(';') and not stripped.endswith('{') and 
    not stripped.endswith('}') and not stripped.endswith(')')):
    if any(op in stripped for op in ['==', '!=', '<=', '>=', '&&', '||']):
        return
    if not any(keyword in stripped for keyword in ['if', 'while', 'for']):
        self.errors.append(f"Line {self.line_number}: Missing semicolon in statement")
```

### 2. Control Statement Parentheses Validation
**Method**: `check_control_parentheses()`

**Data Structures Used**:
- **List**: Control keywords (`if`, `while`, `for`, `switch`)
- **Regex Pattern**: For pattern matching

**Logic/Algorithm**:
1. Iterate through each control keyword
2. Use negative lookahead regex `\b{keyword}\b\s*(?!\()` to find missing parentheses
3. Extract content within parentheses using `\b{keyword}\s*\(([^)]*)`
4. Check for empty conditions within parentheses
5. Report specific errors for each type of violation

**Regex Patterns**:
- Missing parentheses: `rf'\b{keyword}\b\s*(?!\()'`
- Empty conditions: `rf'\b{keyword}\s*\(([^)]*)'`

### 3. For Loop Structure Validation
**Method**: `check_for_loop_syntax()`

**Data Structures Used**:
- **String**: For loop content extraction
- **List**: Split parts of for loop (init, condition, increment)

**Logic/Algorithm**:
1. Detect lines containing 'for'
2. Extract for loop content using regex `for\s*\(([^)]*)\)`
3. Split content by semicolons: `for_content.split(';')`
4. Validate exactly 3 parts exist (init; condition; increment)
5. Report error if semicolon count is incorrect

**Code Structure**:
```python
for_pattern = r'for\s*\(([^)]*)\)'
match = re.search(for_pattern, line)
if match:
    for_content = match.group(1).strip()
    parts = [part.strip() for part in for_content.split(';')]
    if len(parts) != 3:
        self.errors.append(f"Line {self.line_number}: Invalid for loop syntax - expected 2 semicolons")
```

### 4. Global Bracket Matching
**Method**: `check_global_structure()`

**Data Structures Used**:
- **Integer**: Count variables for each bracket type
- **String**: Entire file content

**Logic/Algorithm**:
1. Count opening brackets: `content.count('{')`
2. Count closing brackets: `content.count('}')`
3. Compare counts for equality
4. Repeat for parentheses `()` and square brackets `[]`
5. Report global mismatch errors

**Algorithm Complexity**: O(n) where n is file length

### 5. Invalid Character Detection
**Method**: `check_invalid_characters()`

**Data Structures Used**:
- **Regex Pattern**: Character class definition
- **Set**: For deduplication of invalid characters

**Logic/Algorithm**:
1. Define valid C character set using regex negation
2. Find characters outside valid set: `[^\w\s\{\}\(\)\[\];,\.\+\-\*/%<>=!&|^~?:#\'"\\]`
3. Use `set()` to remove duplicates
4. Report unique invalid characters found

**Regex Explanation**:
- `[^...]` = Negation (match anything NOT in brackets)
- `\w` = Word characters (letters, digits, underscore)
- `\s` = Whitespace characters
- All valid C operators and symbols explicitly listed

### 6. Function Declaration Validation
**Method**: `check_function_declarations()`

**Data Structures Used**:
- **List**: Extracted function patterns
- **Set**: C keywords for return type validation
- **String**: Function name and return type extraction

**Logic/Algorithm**:
1. Find function patterns using regex: `\w+\s+\w+\s*\([^)]*\)\s*{`
2. Split pattern to extract return type and function name
3. Check return type against C keywords set
4. Report invalid return types

**Pattern Breakdown**:
- `\w+\s+` = Return type (word + space)
- `\w+\s*` = Function name
- `\([^)]*\)` = Parameter list (anything except closing paren)
- `\s*{` = Opening brace

### 7. String Literal Validation
**Method**: `check_string_literals()`

**Data Structures Used**:
- **List**: All string literals found
- **String**: Individual string analysis

**Logic/Algorithm**:
1. Extract all string literals using regex: `"[^"]*"`
2. For each string, count quote marks
3. Check if count is odd (unterminated)
4. Report unterminated string literals

**Regex Pattern**: `"[^"]*"` = Double quote, any non-quote chars, closing quote

### 8. If-Else Sequence Validation
**Method**: `check_keyword_sequence()`

**Data Structures Used**:
- **List**: Previous lines for context analysis
- **String**: Line content and stripped versions
- **Boolean**: Flag for matching if found

**Logic/Algorithm**:
1. Iterate through all lines with line numbers
2. When `else` is found without `if`:
   - Look back at previous 10 lines
   - Search for matching `if` statement
   - Stop at complete code blocks (`{` and `}`)
   - Report error if no matching `if` found

**Context Window**: Last 10 lines for efficiency

### 9. Control Statement Brace Issues
**Method**: `check_control_braces()`

**Data Structures Used**:
- **List**: Control keywords
- **String**: Line content analysis

**Logic/Algorithm**:
1. Find control statements with braces: `\b{keyword}\b.*\{`
2. Extract content after opening brace
3. Check for mixed `}` and `;` usage
4. Report semantic errors like `if() { statement; };`

### 10. Preprocessor Directive Validation
**Method**: `check_preprocessor_directives()`

**Data Structures Used**:
- **List**: Valid directive keywords
- **Regex Pattern**: Directive validation

**Logic/Algorithm**:
1. Find lines starting with `#`
2. Validate against allowed directives: `include|define|undef|ifdef|ifndef|if|else|elif|endif|pragma|error`
3. Report invalid preprocessor directives

**Validation Pattern**: `^#\s*(include|define|undef|ifdef|ifndef|if|else|elif|endif|pragma|error)\b`

## Algorithm Complexity Analysis

| Method | Time Complexity | Space Complexity | Notes |
|--------|----------------|------------------|-------|
| `check_semicolons()` | O(1) per line | O(1) | Constant time per line |
| `check_control_parentheses()` | O(k) per line | O(1) | k = number of keywords |
| `check_for_loop_syntax()` | O(1) per line | O(1) | Regex matching |
| `check_global_structure()` | O(n) | O(1) | n = file length |
| `check_invalid_characters()` | O(m) per line | O(1) | m = line length |
| `check_function_declarations()` | O(f) | O(f) | f = number of functions |
| `check_string_literals()` | O(s) | O(s) | s = number of strings |
| `check_keyword_sequence()` | O(L²) | O(1) | L = number of lines (10-line window) |

## Usage Examples

### Basic Usage:
```bash
python c_syntax_checker.py program.c
```

### Error Output Format:
```
Checking C file: program.c
==================================================
Found 3 syntax error(s):
  ❌ Line 4: Missing semicolon in statement
  ❌ Line 7: Missing parentheses after 'if'
  ❌ Global: Unmatched braces. Found 3 '{' and 2 '}'
```

### Test Cases Covered:
1. **Missing semicolons**: `int x = 5` (no semicolon)
2. **Missing parentheses**: `if x > 0` (no parentheses)
3. **Invalid for loop**: `for (i = 0; i < 10 i++)` (missing semicolon)
4. **Unmatched brackets**: Global bracket count mismatch
5. **Invalid characters**: Non-C symbols in code
6. **Invalid return types**: Functions with non-standard return types
7. **Unterminated strings**: `"unclosed string`
8. **Else without if**: `else` without preceding `if`
9. **Mixed brace syntax**: `if() { statement; };`

## Limitations

1. **Semantic Errors**: Does not detect type mismatches, undeclared variables, or logical errors
2. **Complex Macros**: Limited validation of complex preprocessor macros
3. **Multi-line Constructs**: Limited analysis of multi-line statements
4. **Template Support**: No C++ template syntax support
5. **Context Sensitivity**: Limited understanding of variable scope and context

## Future Enhancements

1. **Variable Declaration Tracking**: Track variable declarations and usage
2. **Type Checking**: Basic type compatibility validation
3. **Function Call Validation**: Check function call argument counts
4. **Macro Expansion**: Basic macro syntax validation
5. **Multi-line Statement Analysis**: Handle statements spanning multiple lines

## Conclusion

The C Syntax Checker provides comprehensive structural syntax validation using efficient pattern matching and string analysis techniques. It combines multiple data structures (sets, lists, strings, regex patterns) with various algorithms (counting, pattern matching, context analysis) to detect common C programming errors that prevent compilation.
