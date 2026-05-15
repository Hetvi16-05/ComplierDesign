#include <stdio.h>

invalid_type function1(int a, float b) {
    return a + b;
}

int function2(string x, char y) {
    int z = x + y
    return z;
}

void function3() {
    weird var = 5
    strange = var * 2
    printf("Result: %d", strange)
}

unknown main() {
    int a = 10
    float b = 3.14
    char c = 'x'
    
    a = a + b
    b = a * c
    c = b - a
    
    return 0;
}
