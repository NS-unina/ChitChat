#include <iostream>
#include <fstream>
#include "flag_func.h"

void secret_function() {
    // Apre il file in modalità append
    std::ofstream outfile("log_call.txt", std::ios_base::app); // `std::ios_base::app` è per aggiungere al file

    if (outfile.is_open()) {
        outfile << "well done!" << std::endl;
        outfile.close();
    } else {
        std::cerr << "Impossibile aprire il file per la scrittura!" << std::endl;
    }
}
