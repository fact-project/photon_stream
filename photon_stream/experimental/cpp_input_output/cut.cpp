// compile using:
// g++ docopt/docopt.cpp example_cut.cpp -o phs.cut -std=gnu++11

#include <stdio.h>
#include <string.h>
#include <array>
#include "photon_stream.h"
#include "docopt/docopt.h"
#include <fstream>
#include <iostream>

namespace ps = photon_stream;

static const char USAGE[] =
R"(Show FACT photon-stream event overview in a table on stdout. Reads in phs
files from stdin. 

    Usage:
      phs.cut [options]
      phs.cut  (-h | --help)
      phs.cut  --version

    Options:
      --start_night=INT
      --stop_night=INT

      --start_run=INT
      --stop_run=INT

      --start_event=INT
      --stop_event=INT 

      --trigger=INT       Only show certain trigger type.

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

    printf("night    run event trigger  Az[deg] ZD[deg]  UnixTime[s]   photons\n");
    printf("------------------------------------------------------------------\n");

    bool cut_start_night = args.find("--start_night")->second;
    uint32_t start_night;
    if(cut_start_night) {start_night = std::stoi(args.find("--start_night")->second.asString())}

    bool cut_stop_night = args.find("--stop_night")->second;
    uint32_t stop_night;
    if(cut_stop_night) {stop_night = std::stoi(args.find("--stop_night")->second.asString())}

    bool cut_start_run = args.find("--start_run")->second;
    uint32_t start_run;
    if(cut_start_run) {start_run = std::stoi(args.find("--start_run")->second.asString())}

    bool cut_stop_run = args.find("--stop_run")->second;
    uint32_t stop_run;
    if(cut_stop_run) {stop_run = std::stoi(args.find("--stop_run")->second.asString())}

    bool cut_start_event= args.find("--start_event")->second;
    uint32_t start_event;
    if(cut_start_event) {start_event = std::stoi(args.find("--start_event")->second.asString())}

    bool cut_stop_event = args.find("--stop_event")->second;
    uint32_t stop_event;
    if(cut_stop_event) {stop_event = std::stoi(args.find("--stop_event")->second.asString())}

    bool cut_trigger = args.find("--trigger")->second;
    uint32_t trigger;
    if(cut_trigger) {trigger = std::stoi(args.find("--trigger")->second.asString())}


    while(true) {
        ps::ObservationEvent event = ps::read_ObservationEvent_from_file(std::cin);

        if(!event.descriptor.is_valid())
            break;

        if(cut_start_night && event.id.night < start_night)
            continue
        if(cut_stop_night && event.id.night >= stop_night)
            continue

        if(cut_start_run && event.id.run < start_run)
            continue
        if(cut_stop_run && event.id.night >= stop_run)
            continue

        if(cut_start_event && event.id.event < start_event)
            continue
        if(cut_stop_event && event.id.event >= stop_event)
            continue

        if(cut_trigger && event.info.trigger_type != trigger)
            continue

        ps::append_ObservationEvent_to_file(event, std::out);
    }
    return 0;
};