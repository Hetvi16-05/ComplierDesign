#include <stdio.h>

int main() {
    // Unterminated string
    printf("This string is not terminated\n);
    
    // Another unterminated string
    char *str = "Hello world;
    
    // Valid string for comparison
    printf("This is valid\n");
    
    // Multiple unterminated strings
    printf("First bad\n);
    printf("Second bad\n);
    
    // Mixed valid and invalid
    char *valid = "This is valid";
    char *invalid = "This is invalid;
    
    // String with quotes inside (should be valid)
    printf("He said \"Hello\"\n");
    
    // Unterminated with escaped quotes
    printf("She said \"Goodbye\n);
    
    return 0;
}
