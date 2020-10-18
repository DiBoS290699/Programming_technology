#include "pch.h" // use stdafx.h in Visual Studio 2017 and earlier
#include <utility>
#include "Prime_number.h"

bool isPrime(unsigned long long n)
{
    for (unsigned long long i = 2; i <= sqrt(n); i++)
        if (!(n % i))
        {
            return false;
        }
    return true;
}