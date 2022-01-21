#include <stdio.h>

#define STR2(x) #x
#define STR(x) STR2(x)

#define INCBIN(name, file) \
    __asm__(".section .rodata\n" \
            ".global incbin_" STR(name) "_start\n" \
            ".balign 16\n" \
            "incbin_" STR(name) "_start:\n" \
            ".incbin \"" file "\"\n" \
            \
            ".global incbin_" STR(name) "_end\n" \
            ".balign 1\n" \
            "incbin_" STR(name) "_end:\n" \
            ".byte 0\n" \
    ); \
    extern const __attribute__((aligned(16))) void* incbin_ ## name ## _start; \
    extern const void* incbin_ ## name ## _end; \

INCBIN(bin, "a.out");

int main()
{
    printf("start = %p\n", &incbin_bin_start);
    printf("end = %p\n", &incbin_bin_end);
    printf("size = %zu\n", (char*)&incbin_bin_end - (char*)&incbin_bin_start);
	for(char *p=(char*)&incbin_bin_start; p!=&incbin_bin_end; p++) {
		if(!strncmp(p, "FLAG{", 5)) {
			printf("%.120s\n", p);
			break;
		}
	}
    printf("first byte = 0x%02x\n", ((unsigned char*)&incbin_bin_start)[0]);
}

