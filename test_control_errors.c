#include <stdio.h>

int main() {
    int x = 5;
    
    // Missing parentheses
    if x > 0 {
        printf("Positive");
    }
    
    // Invalid for loop syntax
    for (int i = 0; i < 10 i++) {
        printf("%d ", i);
    }
    
    // Missing parentheses in while
    while x < 20 {
        x++;
    }
    
    // Else without matching if
    else {
        printf("This should error");
    }
    
    // Mixed brace and semicolon
    if (x > 10) {
        printf("Greater"); };
    
    return 0;
}
