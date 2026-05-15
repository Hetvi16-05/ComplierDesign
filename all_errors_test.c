// This file contains C code snippets that trigger each error detected by the C Syntax Checker.
// Each snippet is separated by comments indicating the error type.

// 1. Multiple Mismatched Braces {}
int main() {{
    printf("Hello");
}

// 2. Multiple Mismatched Parentheses ()
printf((("Hello");

// 3. Unmatched Closing Parenthesis ')'
printf("Hello"));

// 4. Unclosed Parenthesis '('
printf(("Hello");

// 5. Unmatched Closing Square Bracket ']'
arr[5]];

// 6. Unclosed Square Bracket '['
arr[5;

// 7. Missing Semicolon in Statement
int a = 10

// 8. Missing Semicolon After Identifier
value

// 9. Missing Semicolon Between Identifiers
abc def

// 10. Missing Semicolon After Second Identifier
ab;cd

// 11. Multiple Consecutive Semicolons
int a = 5;;;

// 12. Invalid Characters
int a = 10 ₹

// 13. Missing Parentheses After 'if'
if x > 0

// 14. Missing Parentheses After 'while'
while x < 10

// 15. Missing Parentheses After 'for'
for i=0;i<5;i++

// 16. Missing Parentheses After 'switch'
switch x

// 17. Empty Condition in 'if'
if ()

// 18. Empty Condition in 'while'
while ()

// 19. Empty Condition in 'for'
for ()

// 20. Invalid 'for' Loop Syntax
for(i=0 i<10 i++)

// 21. Mixed Brace and Semicolon Usage
if(x>0){ printf("Hi");

// 22. Unmatched Closing Bracket Globally
int main() {
    printf("Hello");
}}

// 23. Mismatched Brackets
int main( {

// 24. Unclosed Global Brackets
int main() {
    printf("Hello");

// 25. Invalid Function Return Type
number add() {
}

// 26. Unterminated String Literal
printf("Hello);

// 27. 'else' Without Matching 'if'
else {
    printf("Error");
}

// 28. Missing Semicolon in Multi-line Expression
a =
b +
c

// 29. Invalid Preprocessor Directive
#invalid something
