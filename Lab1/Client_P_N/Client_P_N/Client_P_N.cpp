#include <iostream>
#include "Prime_number.h"
using namespace std;

int main()
{
	//for (unsigned long long i = 1; i <= 100; ++i) {
	//	if (isPrime(i)) {
	//		cout << "The number " << i << "\tis prime" << endl;
	//	}
	//}
	while (true) {
		long long number;
		string cont;
		cout << "Please, input the number: " << boolalpha;
		while (!(cin >> number) || (cin.peek() != '\n') || (cin.peek() == ' ') || number <= 0) {
			cin.clear();
			while (cin.get() != '\n') {}
			cout << "Incorrect number! Input a number again> ";
		}
		number = (unsigned long long)number;
		cout << "This number is prime? - " << isPrime(number) << "\nContinue? (y or other) ";
		cin >> cont;
		if (cont != "y" && cont != "Y") {
			return 0;
		}
	}
}
