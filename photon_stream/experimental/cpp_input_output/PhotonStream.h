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

void append_float32(float &v, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&v), sizeof(v));
}

float read_float32(std::ifstream &fin) {
    float v;
    fin.read(reinterpret_cast<char*>(&v), sizeof(v));
    return v;
}

void append_uint32(uint32_t &v, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&v), sizeof(v));
}
uint32_t read_uint32(std::ifstream &fin) {
    uint32_t v;
    fin.read(reinterpret_cast<char*>(&v), sizeof(v));
    return v;
}

void append_uint16(uint16_t &v, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&v), sizeof(v));
}
uint16_t read_uint16(std::ifstream &fin) {
    uint16_t v;
    fin.read(reinterpret_cast<char*>(&v), sizeof(v));
    return v;
}

void append_uint8(uint8_t &v, std::ofstream &fout) {
    fout.write(reinterpret_cast<char*>(&v), sizeof(v));
}
uint8_t read_uint8(std::ifstream &fin) {
    uint8_t v;
    fin.read(reinterpret_cast<char*>(&v), sizeof(v));
    return v;
}

//------------------------------------------------------------------------------
struct Descriptor {
    uint8_t pass_version;
    uint8_t event_type;
};

Descriptor read_Descriptor_from_file(std::ifstream &fin) {
    Descriptor d;
    d.pass_version = read_uint8(fin);
    d.event_type = read_uint8(fin);
    return d;
}

void append_Descriptor_to_file(Descriptor &d, std::ofstream &fout) {
    append_uint8(d.pass_version, fout);
    append_uint8(d.event_type, fout);
}

//------------------------------------------------------------------------------
struct ObservationIdentifier {
    uint32_t night;
    uint32_t run;
    uint32_t event; 
};

ObservationIdentifier read_ObservationIdentifier_from_file(std::ifstream &fin) {
    ObservationIdentifier obsid;
    obsid.night = read_uint32(fin);
    obsid.run = read_uint32(fin);
    obsid.event = read_uint32(fin);
    return obsid;
}

void append_ObservationIdentifier_to_file(ObservationIdentifier &obsid, std::ofstream &fout) {
    append_uint32(obsid.night, fout);
    append_uint32(obsid.run, fout);
    append_uint32(obsid.event, fout);
}

//------------------------------------------------------------------------------
struct ObservationInformation {
    uint32_t unix_time_s;
    uint32_t unix_time_us;
    uint32_t trigger_type;
};

ObservationInformation read_ObservationInformation_from_file(std::ifstream &fin) {
    ObservationInformation obsinfo;
    obsinfo.unix_time_s = read_uint32(fin);
    obsinfo.unix_time_us = read_uint32(fin);
    obsinfo.trigger_type = read_uint32(fin);
    return obsinfo;
}

void append_ObservationInformation_to_file(ObservationInformation &obsinfo, std::ofstream &fout) {
    append_uint32(obsinfo.unix_time_s , fout);
    append_uint32(obsinfo.unix_time_us, fout);
    append_uint32(obsinfo.trigger_type, fout);
}

//------------------------------------------------------------------------------
struct SimulationIdentifier {
    uint32_t run;
    uint32_t event;
    uint32_t reuse;
};

SimulationIdentifier read_SimulationIdentifier_from_file(std::ifstream &fin) {
    SimulationIdentifier simid;
    simid.run = read_uint32(fin);
    simid.event = read_uint32(fin);
    simid.reuse = read_uint32(fin);
    return simid;
}

void append_SimulationIdentifier_to_file(SimulationIdentifier &simid, std::ofstream &fout) {
    append_uint32(simid.run , fout);
    append_uint32(simid.event, fout);
    append_uint32(simid.reuse, fout);
}

//------------------------------------------------------------------------------
struct Pointing {
    float zd;
    float az;
};

Pointing read_Pointing_from_file(std::ifstream &fin) {
    Pointing p;
    p.zd = read_float32(fin);
    p.az = read_float32(fin);
    return p;
}

void append_Pointing_to_file(Pointing &p, std::ofstream &fout) {
    append_float32(p.zd, fout);
    append_float32(p.az, fout);
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
    uint32_t number_of_pixels_plus_number_of_photons = read_uint32(fin);

    phs.raw.resize(number_of_pixels_plus_number_of_photons);
    fin.read(
        reinterpret_cast<char*>(&phs.raw[0]), 
        number_of_pixels_plus_number_of_photons
    );

    uint16_t number_of_saturated_pixels = read_uint16(fin);

    phs.saturated_pixels.resize(number_of_saturated_pixels);
    fin.read(
        reinterpret_cast<char*>(&phs.saturated_pixels[0]), 
        sizeof(uint16_t)*number_of_saturated_pixels
    );
    return phs;
}

void append_PhotonStream_to_file(PhotonStream &phs, std::ofstream &fout) {
    uint32_t number_of_pixels_plus_number_of_photons = phs.raw.size();
    append_uint32(number_of_pixels_plus_number_of_photons, fout);
    fout.write(
        reinterpret_cast<char*>(phs.raw.data()), 
        number_of_pixels_plus_number_of_photons
    );

    uint16_t number_of_saturated_pixels = phs.saturated_pixels.size();
    append_uint16(number_of_saturated_pixels, fout);
    fout.write(
        reinterpret_cast<char*>(phs.saturated_pixels.data()), 
        number_of_saturated_pixels
    );
}


//------------------------------------------------------------------------------
struct ObservationEvent {
    ObservationIdentifier id;
    ObservationInformation info;
    Pointing pointing;
    PhotonStream photon_stream;
};

ObservationEvent read_ObservationEvent_from_file(std::ifstream &fin) {
    ObservationEvent evt;
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
    append_ObservationIdentifier_to_file(evt.id, fout);
    append_ObservationInformation_to_file(evt.info, fout);
    append_PhotonStream_to_file(evt.photon_stream, fout);
}


//------------------------------------------------------------------------------
struct SimulationEvent {
    SimulationIdentifier id;
    Pointing pointing;
    PhotonStream photon_stream;
};

SimulationEvent read_SimulationEvent_from_file(std::ifstream &fin) {
    SimulationEvent evt;
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
    append_SimulationIdentifier_to_file(evt.id, fout);
    append_PhotonStream_to_file(evt.photon_stream, fout);
}

//------------------------------------------------------------------------------

#endif // __PhotonStreamPass4_H_INCLUDED__