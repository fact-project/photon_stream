// g++ UnitTest.c -o PhotonStreamTest -lm
#include <stdio.h>
#include <string.h>
#include "PhotonStream.h"
#include <fstream>
#include <iostream>

int main() {

    std::string path = "20170119_229_pass4_100events.phs.bin";
    std::ifstream fin(path.c_str(), std::ios::in | std::ios::binary);

    if (fin.is_open()) {
        while(true) {
            Descriptor desc = read_Descriptor_from_file(fin);
            if(fin.eof())
                break;

            ObservationEvent event = read_ObservationEvent_from_file(fin);
            std::cout << "Event(night:" << event.id.night << ", ";
            std::cout << "run:" << event.id.run << ", ";
            std::cout << "event:" << event.id.event << ") ";
            std::cout << "photons:" << event.photon_stream.number_of_photons() << "\n";
    }

    }else {
        std::cout << "Error opening file:" << path << "\n";
    }

    fin.close();
    return 0;
};