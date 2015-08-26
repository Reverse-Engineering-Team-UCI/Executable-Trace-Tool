#include <stdio.h>
#include <conio.h>
 int main()
{
	int number; 
	int i; //Temp variable for loop
	printf("Enter a number: ");
	scanf("%d", &number);
	printf("Number: %d\n", number);
	for(i=0; i<10; i++)
	{
		number = number % 10; 
		if(number > 5)
		{
			printf("Number is greater than 5\n");
		}
		number ++;
	}
	getch();
	return 0;
}