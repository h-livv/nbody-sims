#include <vector>
#include <iostream>
#include <fstream>
#include <cmath>
#include <random>
#include <print>

const double dt = std::pow(10, -9);
int n = 1;


struct Vec3{
    double x{};
    double y{};
    double z{};

    Vec3& operator +=(const Vec3& other){
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }
};

struct Particle{
    Vec3 pos{};
    Vec3 vel{};
    Vec3 acc{};

    double mass{1.67262192*(std::pow(10, -27))};
    double charge{1.602*(std::pow(10, -19))};
};

Vec3 operator +(const Vec3& a, const Vec3& b){
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}

Vec3 operator -(const Vec3& a, const Vec3& b){
    return {a.x - b.x, a.y - b.y, a.z - b.z};
}

Vec3 operator*(double scalar, const Vec3& v) {
    return {scalar * v.x, scalar * v.y, scalar * v.z};
}

Vec3 operator/(const Vec3& v, double scalar) {
    return {v.x/scalar, v.y/scalar, v.z/scalar};
}

double norm(const Vec3& v) {
    return std::hypot(v.x, v.y, v.z);
}

Vec3 operator^(const Vec3& a, const Vec3& b){
    return {a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x};
}

int main(){

    double tick = 0.0;

    std::ofstream file("path.csv");

    // Write headings to csv file
    file << "time";

    file << ",x"
        << ",y"
        << ",z";

    file << '\n';

    std::vector <Particle> particles(1);

    Vec3 mag_field = {0.0, 0.0, 1.0};

    particles[0].vel.x = {2.0};

    for (int i=0; i<1000; ++i){

        Vec3 rotation_vec = (particles[0].charge*dt)/(2*particles[0].mass)*mag_field;

        Vec3 v_dash = particles[0].vel + ((particles[0].vel)^(rotation_vec));

        Vec3 auxilliary_vec = (2*rotation_vec)/(1+(std::pow((norm(rotation_vec)), 2)));

        Vec3 v_new = particles[0].vel + ((v_dash)^(auxilliary_vec));

        particles[0].vel = v_new;

        particles[0].pos += dt*v_new;

        tick += dt;

        file << tick;

        file << "," << particles[0].pos.x
            << "," << particles[0].pos.y
            << "," << particles[0].pos.z;

        file << '\n';
    }
}

