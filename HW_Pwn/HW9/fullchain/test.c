#include <unistd.h>

int main(){
    char buf[100];
    read(1, buf, 4);
    write(1, buf, 4);
    return 0;
}
