#include <stdio.h>

int main()
{
	int a = 1; 
	int b = 5; 
	if(a == b)
	{
		printf("test equal\n");
	}
	else if(a > b)
	{
		printf("test greater\n");
	}
	else if(a < b)
	{
		printf("test less than\n");
	}
	else if(a <= b)
	{
		printf("test less than and equal\n");
	}
	else if(a >= b)
	{
		printf("test greater than and equal\n");
	}
	else if(a != b)
	{
		printf("test not equal\n");
	}
	
	return 0;
}