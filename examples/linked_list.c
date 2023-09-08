struct Node {
    int value;
    struct Node *next;
};

struct Node *construct(int value, struct Node *next) {
    struct Node *node = malloc(sizeof(struct Node));
    node->value = value;
    node->next = next;
    return node;
}

int length(struct Node *head) {
    struct Node *current = head;
    int length = 0;
    while (current != 0) {
        length++;
        current = current->next;
    }
    return length;
}

int index(struct Node *head, int target)
{
    struct Node *current = head;
    int i = 0;
    while (current != 0){
        if (current->value == target){
            return i;   
        }
        current = current -> next; 
        i++;
    }
    return -1; 
} 

void print_list(struct Node *head) {
    struct Node *current = head;
    while (current->next != 0) {
        printf("%d -> ", current->value);
        current = current->next;
    } 
    printf("%d\n", current->value);
}

int main() {
    struct Node *head = 0;
    head = construct(3, head);
    head = construct(5, head);
    head = construct(4, head);
    head = construct(2, head);

    printf("Length: %d\n", length(head));
    print_list(head);
    printf("idx %d: %d\n", 5, index(head, 5));
}