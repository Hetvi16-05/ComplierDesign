#include <stdio.h>

int main() {
    int x = 5;
    int @invalid = 10;  // @ is not valid in C identifiers
    
    printf("Value: %d\n", x);
    int y$ = 20;  // $ is not valid in C identifiers
    
    char ch = '#';  // # is valid in character literals
    float f = 3.14;  // . is valid in floats
    
    // More invalid characters
    int num% = 15;  // % is not valid in identifiers
    int& ref = x;   // & is not valid in identifiers
    
    printf("Testing: %d, %d, %d\n", @invalid, y$, num%);
    
    // Valid characters for comparison
    int valid_var = 100;
    int _underscore = 200;
    int with123 = 300;
    
    return 0;
}
