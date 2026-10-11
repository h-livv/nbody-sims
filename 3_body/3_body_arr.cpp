#include <array>
#include <iostream>
#include <fstream>
#include <cmath>

const double dt = 0.01;
const double G = 1.0;
double tick = 0.0;
std::array<double, 3 > radius {0.5, 0.5, 0.5};

std::array<std::array<double, 2>, 3> pos{{
    {{-0.97000436,  0.24308753}},
    {{ 0.97000436, -0.24308753}},
    {{ 0.0,         0.0}}
}};

// Stable

std::array<std::array<double, 2>, 3> vel{{
    {{ 0.466203685,  0.432365730}},
    {{ 0.466203685,  0.432365730}},
    {{-0.932407370, -0.864731460}}
}};

//Chaotic
/*
std::array<std::array<double, 2>, 3> vel{{
    {{ 0.25037508,  0.13672605}},
    {{ 0.14447802,  0.23672605}},
    {{-0.29485310, -0.27345210}}
}};
*/

std::array<std::array<double, 2>, 3> acc{};

int main () {
    std::ofstream file("three_body.csv");
    file << "time, x1, y1, x2, y2, x3, y3\n";
    double diff[2] = {};
    double term[2] = {};

    for (int w = 0; w<1000; ++w){
        
        for (int i = 0; i < 3; ++i){
            for (int m=0; m<2; ++m){acc[i][m] = 0;}

            for (int j = 0; j < 3; ++j) {
                if (i != j){

                    for (int k = 0; k < 2; ++k){
                        diff[k] = pos[j][k] - pos[i][k];
                    }
                    
                    double mag = std::sqrt(diff[0]*diff[0] + diff[1]*diff[1]);

                    for (int k = 0; k < 2; ++k){
                        term[k] = G*(diff[k]/(mag*mag*mag));
                        acc[i][k] += term[k];
                    }
                }
            }
        }
        
       for (int p=0; p < 3; ++p){
        for (int q=0; q<2; ++q){
            vel[p][q] += dt*acc[p][q];
            pos[p][q] += dt*vel[p][q];
        }
       }
    tick += dt;
    file << tick << "," << pos[0][0] << "," << pos[0][1] << "," << pos[1][0] << "," << pos[1][1] << "," << pos[2][0] << "," << pos[2][1] << "\n";
    }
}

