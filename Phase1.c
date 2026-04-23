#include <stdio.h>
#include <ctype.h>
#include <string.h>

#define MAX 1000

// Keywords list
char *keywords[] = {"int", "float", "if", "else", "while", "return", "char", "void"};
int keyword_count = 8;

// Function to check keyword
int isKeyword(char *word) {
    for(int i = 0; i < keyword_count; i++) {
        if(strcmp(word, keywords[i]) == 0)
            return 1;
    }
    return 0;
}

// Lexical Analyzer
void lexicalAnalysis(char *code) {
    char buffer[50];
    int j = 0;

    printf("\n--- TOKENS ---\n");

    for(int i = 0; i < strlen(code); i++) {
        if(isalnum(code[i])) {
            buffer[j++] = code[i];
        } else {
            if(j > 0) {
                buffer[j] = '\0';

                if(isKeyword(buffer))
                    printf("%s -> Keyword\n", buffer);
                else if(isdigit(buffer[0]))
                    printf("%s -> Number\n", buffer);
                else
                    printf("%s -> Identifier\n", buffer);

                j = 0;
            }

            // Operators and symbols
            if(code[i] == '+' || code[i] == '-' || code[i] == '*' || code[i] == '/' || code[i] == '=') {
                printf("%c -> Operator\n", code[i]);
            }
            else if(code[i] == ';' || code[i] == '{' || code[i] == '}' || code[i] == '(' || code[i] == ')') {
                printf("%c -> Symbol\n", code[i]);
            }
        }
    }
}

// Syntax Checker (Basic)
void syntaxCheck(char *code) {
    int semicolon = 0, open_brace = 0, close_brace = 0;

    for(int i = 0; i < strlen(code); i++) {
        if(code[i] == ';')
            semicolon++;

        if(code[i] == '{')
            open_brace++;

        if(code[i] == '}')
            close_brace++;
    }

    printf("\n--- SYNTAX CHECK ---\n");

    if(semicolon == 0)
        printf("Error: Missing semicolon(s)\n");
    else
        printf("Semicolons present\n");

    if(open_brace != close_brace)
        printf("Error: Unmatched braces\n");
    else
        printf("Braces matched\n");
}

// Main function
int main() {
    char code[MAX];

    printf("Enter C program (single line):\n");
    fgets(code, sizeof(code), stdin);

    lexicalAnalysis(code);
    syntaxCheck(code);

    return 0;
}