#include <array>
#include <iostream>
#include <fstream>
#include <cmath>

const double dt = 0.01;
const double G = 1.0;
double tick = 0.0;
std::array<double, 3 > radius {0.5, 0.5, 0.5};

struct Vec2 {
    double x{};
    double y{};

    Vec2& operator+=(const Vec2& other) {
        x += other.x;
        y += other.y;
        return *this;
    }
};

Vec2 operator-(const Vec2& a, const Vec2& b) {
    return {a.x - b.x, a.y - b.y};
}

Vec2 operator*(double scalar, const Vec2& v) {
    return {scalar * v.x, scalar * v.y};
}

double norm(const Vec2& v) {
    return std::hypot(v.x, v.y);
}


std::array<Vec2, 3> pos{{
    {-0.97000436,  0.24308753},
    { 0.97000436, -0.24308753},
    { 0.0,         0.0}
}};

// Stable

/*
std::array<Vec2, 3> vel{{
    { 0.466203685,  0.432365730},
    { 0.466203685,  0.432365730},
    {-0.932407370, -0.864731460}
}};
*/


// Chaotic


std::array<Vec2, 3> vel{{
    { 0.25037508,  0.13672605},
    { 0.14447802,  0.23672605},
    {-0.29485310, -0.27345210}
}};


std::array<Vec2, 3> acc{};

int main () {
    std::ofstream file("three_body_perturbed.csv");
    file << "time, x1, y1, x2, y2, x3, y3\n";

    for (int e = 0; e<1000; ++e){
        
        for (int i = 0; i<3; ++i){
            acc[i] = {};

            for (int j = 0; j<3; ++j){
                if (i != j){

                    Vec2 diff = pos[j] - pos[i];
                    double r = norm(diff);

                    acc[i] += (G/(r*r*r))*diff;
                }
            }
        }
        
        for (int i = 0; i < 3; ++i) {
            vel[i] += dt * acc[i];
            pos[i] += dt * vel[i];
        }

        tick += dt;
        file << tick << "," << pos[0].x << "," << pos[0].y << "," << pos[1].x << "," << pos[1].y << "," << pos[2].x << "," << pos[2].y << "\n";
    }
}