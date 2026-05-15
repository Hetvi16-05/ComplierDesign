#include <stdio.h>

int main() {
    int @var = 5;
    float #data = 3.14;
    
    if @var > #data
        printf("Comparison")
    
    for @var = 0; @var < 10; @var++
        printf("%d", @var)
    
    weird_function(@var, #data)
    
    "unclosed string
    printf("Hello")
    
    int arr[5 = {1, 2, 3, 4, 5;
    printf("arr[0] = %d", arr[0)
    
    return 0;
}

void weird_function(int a, float b) {
    int result = a + b
    printf("Result: %f", result)
}
