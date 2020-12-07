#pragma once

#ifdef PRIMENUMBER_EXPORTS
#define PRIMENUMBER_API __declspec(dllexport)
#else
#define PRIMENUMBER_API __declspec(dllimport)
#endif

extern "C" PRIMENUMBER_API bool isPrime(unsigned long long n);