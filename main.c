int rock(int x, int y){
    int h;
    h = x + y;
    return(h);
}

void recursive(int x){
    if(x > 0){
        printf(x);
        recursive(x-1);
    } else {
        printf(x);
    }
}

void loop_up(int n, int i){
    while(i < n){
        printf(i);
        i = i + 1;
    }
}



int main(){
    recursive(5);
    loop_up(10,8);
    int x;
    x = rock(10, 2);
    printf(x);
    return(5);
}