// Test file for bracket imbalance detection
#include <stdio.h>

int main() {
    // Test case 1: Mismatched brackets
    int arr[10];
    if (arr[0] > 5) {
        printf("Mismatched: ( { ] )");
    }
    
    // Test case 2: Unmatched opening brackets
    for (int i = 0; i < 10; i++) {
        if (i % 2 == 0) {
            printf("Unclosed: ( ( {");
    
    // Test case 3: Unmatched closing brackets
    printf("Unmatched closing: ) } ]");
    
    // Test case 4: Proper nesting
    if (true) {
        for (int j = 0; j < 5; j++) {
            arr[j] = j * 2;
        }
    }
    
    return 0;
}
