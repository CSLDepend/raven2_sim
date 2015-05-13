all: random_num unrandom malicious_wrapper 
random_num: random_num.c
	gcc random_num.c -o random_num
unrandom: unrandom.c
	gcc -shared -fPIC unrandom.c -o unrandom.so
malicious_wrapper: malicious_wrapper.c
	gcc -shared -fPIC  malicious_wrapper.c -o malicious_wrapper.so
clean:
	rm -f random_num unrandom.so malicious_wrapper.so
