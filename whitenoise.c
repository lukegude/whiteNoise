#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SAMPLE_RATE 44100
#define DURATION 5

void white_noise(){
    int i;
    int num_samples = SAMPLE_RATE * DURATION;
    short *buffer = malloc(num_samples * sizeof(short));
    while (1){
        for (i = 0; i < num_samples; i++)
        {
            buffer[i] = rand();
        }
        fwrite(buffer, sizeof(short), num_samples, stdout);
    }
}

void brown_noise(){
    srand(time(0));

    double current_sample = 0;
    while (1) { 
        double white = (double)(rand() % 65536) / 32768.0 - 1.0;         
        current_sample += white; 
        
        current_sample = current_sample * 0.5;
        if (current_sample > 1.0) current_sample = 1.0;
        if (current_sample < -1.0) current_sample = -1.0;
        
        short output_sample = (short)(current_sample * 32767); 
        fwrite(&output_sample, sizeof(short), 1, stdout);     
    }

}


int main(int argc, char *argv[]) {
    srand(time(NULL));
    if (argc > 1){
        if (argv[1][1] == 'w'){
            white_noise();
        }
        else if (argv[1][1] == 'b'){
            brown_noise();
        }
    }
    else{
        printf("Usage: %s -w for white noise, -b for brown noise\n", argv[0]);
    }
    return 0;
}

