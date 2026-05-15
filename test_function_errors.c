#include <stdio.h>

// Invalid return type
mytype invalidFunction(int x) {
    return x * 2;
}

// Another invalid return type
custom calculate(int a, int b) {
    return a + b;
}

// Valid function for comparison
int validFunction(int x) {
    return x + 1;
}

// Function with invalid return type and no parameters
unknown noParams() {
    printf("Hello");
}

// Function with invalid return type and parameters
string processData(int num, char ch) {
    printf("Processing %d and %c", num, ch);
}

int main() {
    int result = validFunction(5);
    printf("Result: %d\n", result);
    
    return 0;
}
