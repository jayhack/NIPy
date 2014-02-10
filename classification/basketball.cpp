#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;

#define SEASON_LENGTH 10

int main () {

	/*### Step 1: get the team names ###*/
	char * name_1 = "Auburn";
	char * name_2 = "FSU";
	char * name_3 = "Stanford";
	char * name_4 = "MSU";
	char ** names [4] = {name_1, name_2, name_3, name_4};

	for (int i=0;i<4;i++) {
		printf("%s\n", names[i]);
	}

	/*### Step 1: get the teams scores ###*/
	// int scores_1 [SEASON_LENGTH] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
	// int scores_2 [SEASON_LENGTH] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
	// int scores_3 [SEASON_LENGTH] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
	// int scores_4 [SEASON_LENGTH] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};			


}