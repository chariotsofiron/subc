int abs_diff(int a, int b) {
    if (a > b) {
        return a - b;
    }
    return b - a;
}

void line(int x1, int y1, int x2, int y2) {
    // Bresenham's line algorithm
    int temp, dx, dy, error, ystep, y, maxX, x;
    int steep = abs_diff(y2, y1) > abs_diff(x2, x1);
    if (steep) {
        // swap x1, y1
        temp = x1;
        x1 = y1;
        y1 = temp;
        // swap x2, y2
        temp = x2;
        x2 = y2;
        y2 = temp;
    }

    if (x1 > x2) {
        // swap x1, x2
        temp = x1;
        x1 = x2;
        x2 = temp;
        // swap y1, y2
        temp = y1;
        y1 = y2;
        y2 = temp;
    }

    dx = x2 - x1;
    dy = abs_diff(y2, y1);
    error = dx / 2;
    ystep = (y1 < y2) ? 1 : -1;
    y = y1;

    maxX = x2;
    x = x1;
    while (x <= maxX) {
    //     if (steep) {
    //         printf("%d, %d\n", y, x);
    //     } else {
    //         printf("%d, %d\n", x, y);
    //     }

    //     error = error - dy;
    //     if (error < 0) {
    //         y = y + ystep;
    //         error = error + dx;
    //     }
        ++x;
    }
}


int main() {
    line(0, 1, 6, 4);
}