int main() {
    int rows = 9;
    int i = 1;
    while (i <= rows) {
        int j = 1;
        while (j <= i) {
            printf("* ");
            j++;
        }
        printf("\n");
        i++;
    }
    return 0;

}