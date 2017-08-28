// compile using:
// g++ docopt/docopt.cpp ExampleReader.c -o PhotonStreamTest -lm -std=gnu++11
// 
// gunzip the example binary run in the photon_stream/tests/resources and
// run the executable right next tu the unzipped binary file.
// It will print some basic event information on the command line.

#include <stdio.h>
#include <string.h>
#include "photon_stream.h"
#include "docopt/docopt.h"
#include <fstream>
#include <iostream>

namespace ps = photon_stream;

static const char USAGE[] =
R"(Show FACT event overview

    Usage:
      PhsShow --input=PATH [--trigger=TYPE]
      PhsShow (-h | --help)
      PhsShow --version

    Options:
      -i --input=PATH     Input event list path.
      -t --trigger=TYPE   Only show certain trigger type.
      -h --help           Show this screen.
      --version           Show version.
      
)";


void print_event_info_line(ps::ObservationEvent &event) {
    printf(
        "%05d %03d %5d %6d  %3.2f  %3.2f  %10.6f  %6d\n",  
        event.id.night,
        event.id.run,
        event.id.event,
        event.info.trigger_type,
        event.pointing.az,
        event.pointing.zd,
        float(event.info.unix_time_s) + 1e-6*float(event.info.unix_time_us),
        event.photon_stream.number_of_photons()
    );
};

int main(int argc, char* argv[]) {

    std::map<std::string, docopt::value> args = docopt::docopt(
        USAGE,
        { argv + 1, argv + argc },
        true,        // show help if requested
        "mct 0.0"
    );  // version string

    std::string path = args.find("--input")->second.asString();
    std::ifstream fin(path.c_str(), std::ios::in | std::ios::binary);

    printf("night    run event trigger  Az[deg] ZD[deg]  UnixTime[s]   photons\n");
    printf("------------------------------------------------------------------\n");
    if (fin.is_open()) {
        while(true) {
            ps::Descriptor desc = ps::read_Descriptor_from_file(fin);
            if(fin.eof())
                break;

            ps::ObservationEvent event = ps::read_ObservationEvent_from_file(fin);

            if(args.find("--trigger")->second) {
                if(
                    std::stoi(args.find("--trigger")->second.asString()) == 
                    event.info.trigger_type
                ) {
                    print_event_info_line(event);
                }
            }else{
                print_event_info_line(event);     
            }
        }
    }else{
        std::cout << "Error opening file:" << path << "\n";
    }

    fin.close();
    return 0;
};