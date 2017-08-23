#ifndef __PhotonStreamPass4_H_INCLUDED__
#define __PhotonStreamPass4_H_INCLUDED__

#include <stdint.h>
#include <vector>
#include <math.h>
#include <fstream>
#include <iostream>

const uint8_t NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI = 30;
const uint8_t NUMBER_OF_TIME_SLICES = 100;
const uint32_t NUMBER_OF_PIXELS = 1440;
const uint32_t NUMBER_OF_PHOTONS_IN_PIXEL_BEFORE_SATURATION = 500;
const uint8_t NEXT_PIXEL_MARKER = 255;
const float TIME_SLICE_DURATION_S = 0.5e-9;
const uint8_t OBSERVATION_KEY = 0;
const uint8_t SIMULATION_KEY = 1;
const uint8_t PASS_VERSION = 4;


//------------------------------------------------------------------------------
struct Descriptor {
    uint8_t pass_version;
    uint8_t event_type;
};

Descriptor read_Descriptor_from_file(std::ifstream &fin) {
    Descriptor d;
    fin.read(reinterpret_cast<char*>(&d.pass_version), sizeof(d.pass_version));
    fin.read(reinterpret_cast<char*>(&d.event_type), sizeof(d.event_type));
    return d;
}

void append_Descriptor_to_file(Descriptor &d, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&d.pass_version), sizeof(d.pass_version));
    fout.write(reinterpret_cast<char*>(&d.event_type), sizeof(d.event_type));
}

//------------------------------------------------------------------------------
struct FutureProblems {
    uint8_t a;
    uint8_t b;
};

FutureProblems read_FutureProblems_from_file(std::ifstream &fin) {
    FutureProblems f;
    fin.read(reinterpret_cast<char*>(&f.a), sizeof(f.a));
    fin.read(reinterpret_cast<char*>(&f.b), sizeof(f.b));
    return f;
}

void append_FutureProblems_to_file(FutureProblems &f, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&f.a), sizeof(f.a));
    fout.write(reinterpret_cast<char*>(&f.b), sizeof(f.b));
}

//------------------------------------------------------------------------------
struct ObservationIdentifier {
    uint32_t night;
    uint32_t run;
    uint32_t event; 
};

ObservationIdentifier read_ObservationIdentifier_from_file(std::ifstream &fin) {
    ObservationIdentifier obsid;
    fin.read(reinterpret_cast<char*>(&obsid.night), sizeof(obsid.night));
    fin.read(reinterpret_cast<char*>(&obsid.run), sizeof(obsid.run));
    fin.read(reinterpret_cast<char*>(&obsid.event), sizeof(obsid.event));
    return obsid;
}

void append_ObservationIdentifier_to_file(ObservationIdentifier &obsid, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&obsid.night), sizeof(obsid.night));
    fout.write(reinterpret_cast<char*>(&obsid.run), sizeof(obsid.run));
    fout.write(reinterpret_cast<char*>(&obsid.event), sizeof(obsid.event));
}

//------------------------------------------------------------------------------
struct ObservationInformation {
    uint32_t unix_time_s;
    uint32_t unix_time_us;
    uint32_t trigger_type;
};

ObservationInformation read_ObservationInformation_from_file(std::ifstream &fin) {
    ObservationInformation obsinfo;
    fin.read(reinterpret_cast<char*>(&obsinfo.unix_time_s), sizeof(obsinfo.unix_time_s));
    fin.read(reinterpret_cast<char*>(&obsinfo.unix_time_us), sizeof(obsinfo.unix_time_us));
    fin.read(reinterpret_cast<char*>(&obsinfo.trigger_type), sizeof(obsinfo.trigger_type));
    return obsinfo;
}

void append_ObservationInformation_to_file(ObservationInformation &obsinfo, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&obsinfo.unix_time_s), sizeof(obsinfo.unix_time_s));
    fout.write(reinterpret_cast<char*>(&obsinfo.unix_time_us), sizeof(obsinfo.unix_time_us));
    fout.write(reinterpret_cast<char*>(&obsinfo.trigger_type), sizeof(obsinfo.trigger_type));
}

//------------------------------------------------------------------------------
struct SimulationIdentifier {
    uint32_t run;
    uint32_t event;
    uint32_t reuse;
};

SimulationIdentifier read_SimulationIdentifier_from_file(std::ifstream &fin) {
    SimulationIdentifier simid;
    fin.read(reinterpret_cast<char*>(&simid.run), sizeof(simid.run));
    fin.read(reinterpret_cast<char*>(&simid.event), sizeof(simid.event));
    fin.read(reinterpret_cast<char*>(&simid.reuse), sizeof(simid.reuse));
    return simid;
}

void append_SimulationIdentifier_to_file(SimulationIdentifier &simid, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&simid.run), sizeof(simid.run));
    fout.write(reinterpret_cast<char*>(&simid.event), sizeof(simid.event));
    fout.write(reinterpret_cast<char*>(&simid.reuse), sizeof(simid.reuse));
}

//------------------------------------------------------------------------------
struct Pointing {
    float zd;
    float az;
};

Pointing read_Pointing_from_file(std::ifstream &fin) {
    Pointing p;
    fin.read(reinterpret_cast<char*>(&p.zd), sizeof(float));
    fin.read(reinterpret_cast<char*>(&p.az), sizeof(float));
    return p;
}

void append_Pointing_to_file(Pointing &p, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&p.zd), sizeof(float));
    fout.write(reinterpret_cast<char*>(&p.az), sizeof(float));
}

//------------------------------------------------------------------------------
struct PhotonStream {
    std::vector<uint8_t> raw;
    std::vector<uint16_t> saturated_pixels;

    uint32_t number_of_photons() {
        return raw.size() - NUMBER_OF_PIXELS;
    }

    void fixed_size_repr(uint16_t **image_sequence) {
        uint32_t pixel = 0;
        for(uint32_t i=0; i<raw.size(); i++) {
            if(raw[i] == NEXT_PIXEL_MARKER) {
                pixel++;
            }else{
                image_sequence[
                    raw[i] - NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI
                ][
                    pixel
                ]++;
            }
        }
    };

    void point_cloud_repr(const float *cx, const float *cy, float* point_cloud) {
        uint32_t pixel = 0;
        for(uint32_t i=0; i<raw.size(); i++) {
            if(raw[i] == NEXT_PIXEL_MARKER) {
                pixel++;
            }else{
                point_cloud[i, 0] = cx[pixel];
                point_cloud[i, 1] = cy[pixel];
                point_cloud[i, 2] = TIME_SLICE_DURATION_S*raw[i];
            }            
        }        
    }
};

PhotonStream read_PhotonStream_from_file(std::ifstream &fin) {
    PhotonStream phs;
    uint32_t number_of_pixels_plus_number_of_photons;
    fin.read(reinterpret_cast<char*>(&number_of_pixels_plus_number_of_photons), sizeof(uint32_t));

    phs.raw.resize(number_of_pixels_plus_number_of_photons);
    fin.read(reinterpret_cast<char*>(&phs.raw[0]), number_of_pixels_plus_number_of_photons);

    uint16_t number_of_saturated_pixels;
    fin.read(reinterpret_cast<char*>(&number_of_saturated_pixels), sizeof(uint16_t));

    phs.saturated_pixels.resize(number_of_saturated_pixels);
    fin.read(reinterpret_cast<char*>(&phs.saturated_pixels[0]), sizeof(uint16_t)*number_of_saturated_pixels);
    return phs;
}

void append_PhotonStream_to_file(PhotonStream &phs, std::ofstream &fout) {
    uint32_t number_of_pixels_plus_number_of_photons = phs.raw.size();
    fout.write(reinterpret_cast<char*>(&number_of_pixels_plus_number_of_photons), sizeof(uint32_t));
    fout.write(reinterpret_cast<char*>(phs.raw.data()), number_of_pixels_plus_number_of_photons);

    uint16_t number_of_saturated_pixels = phs.saturated_pixels.size();
    fout.write(reinterpret_cast<char*>(&number_of_saturated_pixels), sizeof(uint16_t));
    fout.write(reinterpret_cast<char*>(phs.saturated_pixels.data()), number_of_saturated_pixels);
}


//------------------------------------------------------------------------------
struct ObservationEvent {
    FutureProblems future_problems;
    ObservationIdentifier id;
    ObservationInformation info;
    Pointing pointing;
    PhotonStream photon_stream;
};

ObservationEvent read_ObservationEvent_from_file(std::ifstream &fin) {
    ObservationEvent evt;
    evt.future_problems = read_FutureProblems_from_file(fin);
    evt.id = read_ObservationIdentifier_from_file(fin);
    evt.info = read_ObservationInformation_from_file(fin);
    evt.pointing = read_Pointing_from_file(fin);
    evt.photon_stream = read_PhotonStream_from_file(fin);
    return evt;
};

void append_ObservationEvent_to_file(ObservationEvent evt, std::ofstream &fout) {
    Descriptor h;
    h.pass_version = PASS_VERSION;
    h.event_type = OBSERVATION_KEY;
    append_Descriptor_to_file(h, fout);
    append_FutureProblems_to_file(evt.future_problems, fout);
    append_ObservationIdentifier_to_file(evt.id, fout);
    append_ObservationInformation_to_file(evt.info, fout);
    append_PhotonStream_to_file(evt.photon_stream, fout);
}


//------------------------------------------------------------------------------
struct SimulationEvent {
    FutureProblems future_problems;
    SimulationIdentifier id;
    Pointing pointing;
    PhotonStream photon_stream;
};

SimulationEvent read_SimulationEvent_from_file(std::ifstream &fin) {
    SimulationEvent evt;
    evt.future_problems = read_FutureProblems_from_file(fin);
    evt.id = read_SimulationIdentifier_from_file(fin);
    evt.pointing = read_Pointing_from_file(fin);
    evt.photon_stream = read_PhotonStream_from_file(fin);
    return evt;
};

void append_SimulationEvent_to_file(SimulationEvent evt, std::ofstream &fout) {
    Descriptor h;
    h.pass_version = PASS_VERSION;
    h.event_type = SIMULATION_KEY;
    append_Descriptor_to_file(h, fout);
    append_FutureProblems_to_file(evt.future_problems, fout);
    append_SimulationIdentifier_to_file(evt.id, fout);
    append_PhotonStream_to_file(evt.photon_stream, fout);
}

//------------------------------------------------------------------------------

#endif // __PhotonStreamPass4_H_INCLUDED__