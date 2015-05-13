#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
 
typedef ssize_t(*orig_write_f_type)(int fd, void *buf, size_t nbyte);

ssize_t write(int fd, void *buf, size_t nbyte)
{
    FILE *fp;
    int target_pid = -1;
    int target_fd = -1;
    orig_write_f_type orig_write;

    /* Some evil injected code goes here. */
    //printf("The victim used write(...) to access '%d'!!!\n",fd); //remember to include stdio.h! 

    /* Check if target file exist */
    if (fp=fopen("/tmp/target", "r")) {
        fscanf(fp, "%d %d", &target_pid, &target_fd);
        fclose(fp);
        printf("&&& pid = %d, fd = %d\n", target_pid, target_fd);
      
        /* Check if PID and FD both match target */ 
        if (target_pid == getpid()) { 
            printf("&&& perform attack!!\n");
        }
    }

    orig_write = (orig_write_f_type)dlsym(RTLD_NEXT,"write");
    return orig_write(fd, buf, nbyte);
}
