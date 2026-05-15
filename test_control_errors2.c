#include <stdio.h>

int main() {
    int x = 5;
    
    // Missing parentheses
    if x > 0 {
        printf("Positive\n");
    }
    
    // Invalid for loop syntax
    for (int i = 0; i < 10 i++) {
        printf("%d ", i);
    }
    
    // Missing parentheses in while
    while x < 20 {
        x++;
    }
    
    // Missing parentheses in switch
    switch x {
        case 1:
            printf("One");
            break;
    }
    
    // Else without matching if
    else {
        printf("Error: no matching if");
    }
    
    // Mixed brace and semicolon
    if (x > 10) {
        printf("Greater"); };
    
    return 0;
}
