#include <stdio.h>

int main() {
    int x, y, z;
    
    // Test various semicolon patterns
    ab;cd          // Should error: missing semicolon after cd
    ef;gh;         // Should be valid: two statements
    ij;kl;mn       // Should error: missing semicolon after mn
    op qr          // Should error: missing semicolon between op and qr
    st;uv;wx;yz    // Should be valid: multiple statements
    
    return 0;
}
