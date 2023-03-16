
int factorial(int n) {
    if (n == 1)
        return 1;
    else
        return n * factorial(n - 1);
}
int main() {
    int f;
    f = factorial(5);
    printf("Factorial = %d\n", f);
    return 0;
}