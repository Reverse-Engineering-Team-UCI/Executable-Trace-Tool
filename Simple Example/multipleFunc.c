#include <stdio.h>

void innerFunc()
{
	int a = 3;
	int b = 5; 
	if(a == b)
	{
		printf("Equal\n");
	}
}

int add(int a, int b)
{
	int x = 5;
	if(x==5)
	{
		innerFunc();
	}
	return a+b;
}

int main()
{
	int x = 5;
	if(x==5)
	{
		printf("True\n");
	}
	int result = add(4, 5);
	printf("result: %d\n", result);
	getch();
	return 0;
}