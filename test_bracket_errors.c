#include <stdio.h>

int main() {
    int x = 5;
    
    // Unmatched braces
    if (x > 0) {
        printf("Positive\n");
    // Missing closing brace
    
    // Unmatched parentheses
    printf("Value: %d\n", x;
    
    // Unmatched square brackets
    int arr[5] = {1, 2, 3, 4, 5;
    printf("arr[0] = %d\n", arr[0);
    
    // Multiple bracket issues
    if (x > 0 && (y < 10 || z > 20 {
        printf("Complex condition");
    }
    
    // Nested bracket errors
    for (int i = 0; i < 5; i++ {
        if (arr[i] > 2 {
            printf("Found: %d\n", arr[i];
        }
    }
    
    return 0;
// Missing closing brace for main
