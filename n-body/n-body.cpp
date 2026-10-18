#include <vector>
#include <array>
#include <iostream>
#include <fstream>
#include <cmath>
#include <random>


struct Vec3 {
    double x{};
    double y{};
    double z{};

    Vec3& operator+=(const Vec3& other) {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }
};

Vec3 operator-(const Vec3& a, const Vec3& b) {
    return {a.x - b.x, a.y - b.y, a.z - b.z};
}

Vec3 operator*(double scalar, const Vec3& v) {
    return {scalar * v.x, scalar * v.y, scalar * v.z};
}

double norm(const Vec3& v) {
    return std::hypot(v.x, v.y, v.z);
}

const double dt = 0.01;
const double G = 1.0;
double tick = 0.0;
const int n = 250;
std::vector<double> radius(n, 0.5);
std::vector<double> mass(n, 1);


std::vector<Vec3> pos(n);
std::vector<Vec3> vel(n);

std::vector<Vec3> acc(n);

int main() {
    std::ofstream file("n_body.csv");

    if (!file) {
        std::cerr << "Error opening n_body.csv\n";
        return 1;
    }

    file << "time";

    for (int i = 0; i < n; ++i) {
        file << ",x" << i + 1
            << ",y" << i + 1
            << ",z" << i + 1;
    }

    file << '\n';

    radius[0] = 2;
    mass[0] = 10;

    std::mt19937 rng(12345);
    std::uniform_real_distribution<double> pos_dist(-25.0, 25.0);
    std::uniform_real_distribution<double> vel_dist(-5.0, 5.0);

    pos[0] = {0.0, 0.0, 0.0};
    vel[0] = {0.0, 0.0, 0.0};

    for (int i = 1; i < n; ++i) {
        pos[i] = {
            pos_dist(rng),
            pos_dist(rng),
            pos_dist(rng)
        };

        vel[i] = {
            vel_dist(rng),
            vel_dist(rng),
            vel_dist(rng)
        };
    }

    for (int e = 0; e<1000; ++e){
        
        for (int i = 1; i<n; ++i){
            acc[i] = {};

            for (int j = 0; j<n; ++j){
                if (i != j){

                    Vec3 diff = pos[j] - pos[i];
                    double r = norm(diff);

                    acc[i] += mass[j]*(G/(r*r*r))*diff;
                }
            }
        }
        
        for (int i = 1; i < n; ++i) {
            vel[i] += dt * acc[i];
            pos[i] += dt * vel[i];
        }

    tick += dt;
    file << tick;

    for (int i = 0; i < n; ++i) {
        file << "," << pos[i].x
            << "," << pos[i].y
            << "," << pos[i].z;
    }

    file << '\n';

    }
}
