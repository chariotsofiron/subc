
int a;
int *b, **c;

struct P1 {int x, y;} d;
struct P2 {char x; int y; char z; int w;} e;

enum E1 {Good, Bad=12};
enum {Hi};

int foo(int x, struct Point {int x, y;} g) {
    int a;
    int *b, **c;

    struct P1 {int x, y;} d;
    struct P2 {char x; int y; char z; int w;} e;

    enum E1 {Good, Bad=12};
    enum {Hi};
}

int main() {
    int i = 0;
}