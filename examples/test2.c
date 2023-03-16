
void main() {
    int i = 0;
    int j = i;
    while (i < 10) {
        i = i + 1;
        i = j;
    }
}