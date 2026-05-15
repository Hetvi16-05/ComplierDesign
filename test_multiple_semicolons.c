#include <stdio.h>

int main() {
    int x, y, z;
    
    // Test multiple semicolon patterns
    ab;;cd         // Double semicolon
    ef;;;gh        // Triple semicolon
    ij;kl;;mn      // Mixed pattern
    op;;;;qr       // Many semicolons
    st;uv;wx;yz    // Valid multiple statements
    
    return 0;
}
