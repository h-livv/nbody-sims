#include <iostream>
#include <fstream>

const double g{-10};
const double dt[] = {0.01};
double tick[] = {0};
double radius[] = {0.5};

double pos[] = {10};
double vel[] = {0};
double acc[] = {g};
double boundary[] = {0};

int main () {
    std::ofstream file("ball.csv");
    file << "time, position\n";
    for (int i = 0; i<2000; ++i) {
        vel[0] = vel[0] + dt[0]*acc[0];
        // std::cout << "Updated velocity: " << vel[0] << "\n";
        pos[0] = pos[0] + dt[0]*vel[0];
        // std::cout << "Updated position: " << pos[0] << "\n";
        tick[0] = tick[0] + dt[0];

        if (pos[0] - radius[0] <= boundary[0] && vel[0] < 0) {
            vel[0] = -0.75*vel[0];
            pos[0] = boundary[0] + radius[0];;
        }
        file << tick[0] << "," << pos[0] << "\n";
    }
}