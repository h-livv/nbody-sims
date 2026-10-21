// Imports
#include <vector>
#include <iostream>
#include <fstream>
#include <cmath>
#include <random>

//Constants
const double dt = 0.01;
const double G = 10.0;
const int n = 250;


// Type definitions

// Define a type representing a 3D vector with x, y, and z components
struct Vec3 {
    double x{};
    double y{};
    double z{};

    // Take a += b
    // "a" is the object on which the function is called
    // "b" is passed as "other", a const reference
    // "this" is a pointer to "a"
    // *this dereferences the pointer, referring to the actual "a"
    // Returns a reference to the updated "a"
    Vec3& operator+=(const Vec3& other) {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }
};

// Define a type representing one body
struct Body {
    Vec3 pos{};
    Vec3 vel{};
    Vec3 acc{};

    double mass{1.0};
    double radius{0.5};
};



// Mathematical operations

// Takes const references to a and b
// Computes their component-wise difference and returns a new Vec3 by value
Vec3 operator-(const Vec3& a, const Vec3& b) {
    return {a.x - b.x, a.y - b.y, a.z - b.z};
}

// Takes a scalar and a const reference to a Vec3
// Multiplies each component by the scalar and returns a new Vec3
Vec3 operator*(double scalar, const Vec3& v) {
    return {scalar * v.x, scalar * v.y, scalar * v.z};
}

// Takes a const reference to a Vec3
// Returns its magnitude as a double
double norm(const Vec3& v) {
    return std::hypot(v.x, v.y, v.z);
}



// Simulation functions


void populate (std::vector<Body>& bodies) {
    // Initialize a reproducible pseudo-random number generator and distributions
    std::mt19937 rng(12345);
    std::uniform_real_distribution<double> pos_dist(-5.0, 5.0);
    std::uniform_real_distribution<double> vel_dist(-10.0, 10.0);

    // Initialize positions and velocities for all n bodies with random components
    for (int i = 0; i < bodies.size(); ++i) {
        bodies[i].pos = {
            pos_dist(rng),
            pos_dist(rng),
            pos_dist(rng)
        };

        bodies[i].vel = {
            vel_dist(rng),
            vel_dist(rng),
            vel_dist(rng)
        };
    }
}


void compute_acc(std::vector<Body>& bodies, double G) {

    for (int i = 0; i<bodies.size(); ++i){
    // Initialize body acc to zero every time step to avoid accumulation
    bodies[i].acc = {};
    
    // Loop over all bodies, excluding body i itself
    for (int j = 0; j<bodies.size(); ++j){
        if (i != j){

        // Calculate the displacement vector pointing from body i to body j
        Vec3 diff = bodies[j].pos - bodies[i].pos;

        // Calculate the magnitude of the vector
        double dist = norm(diff);

        // Update the acceleration of that body
        bodies[i].acc += (bodies[j].mass)*(G/(dist*dist*dist))*diff;
            }
        }
    } 
}

void euler(std::vector<Body>& bodies, double dt) {

    for (int i = 0; i < bodies.size(); ++i) {
            bodies[i].vel += dt * bodies[i].acc;
            bodies[i].pos += dt * bodies[i].vel;
        }
}



// I/O Functions

void set_up_csv(std::ofstream& file, const std::vector<Body>& bodies){

    // Write headings to csv file
    file << "time";

    for (int i = 0; i < bodies.size(); ++i) {
        file << ",x" << i + 1
            << ",y" << i + 1
            << ",z" << i + 1;
    }

    file << '\n';
}

void write_to_csv (std::ofstream& file, const std::vector<Body>& bodies, double tick) {
    
    file << tick;

    for (const Body& body : bodies) {
    file << "," << body.pos.x
         << "," << body.pos.y
         << "," << body.pos.z;
    }

    file << '\n';
}



int main() {

    double tick = 0.0;

    std::vector<Body> bodies(n);

    std::ofstream file("n_body.csv");

    if (!file) {
        std::cerr << "Error opening n_body.csv\n";
        return 1;
    }

    set_up_csv(file, bodies);

    populate(bodies);

    // Loop
    for (int i = 0; i<1000; ++i){

        compute_acc(bodies, G);
        
        euler(bodies, dt);
        
        tick += dt;
        
        write_to_csv(file, bodies, tick);

    }
}

