#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

int main()
{
    setuid(0);
    system("/usr/bin/python3 /home/julian/monitor.py");
    return 0;
}

