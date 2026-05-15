#include <stdio.h>

int main() {
    int x = 5;
    
    if x > 0
        printf("positive")
    
    while x < 10
        x++
    
    for i = 0; i < 5; i++
        printf("%d", i)
    
    switch x
        case 1:
            printf("one")
    
    else
        printf("else without if")
    
    do
        printf("do-while")
    while x > 0
    
    return 0;
}
