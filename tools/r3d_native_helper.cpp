#include <algorithm>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include "R3DSDK.h"

namespace {

std::string json_escape(const std::string &value) {
    std::ostringstream out;
    for (char ch : value) {
        switch (ch) {
        case '\\':
            out << "\\\\";
            break;
        case '"':
            out << "\\\"";
            break;
        case '\n':
            out << "\\n";
            break;
        case '\r':
            out << "\\r";
            break;
        case '\t':
            out << "\\t";
            break;
        default:
            out << ch;
            break;
        }
    }
    return out.str();
}

void print_error(const std::string &message) {
    std::cout << "{\"ok\":false,\"error\":\"" << json_escape(message) << "\"}";
}

size_t adjusted_dimension(size_t value, R3DSDK::VideoDecodeMode mode) {
    size_t divisor = 1;
    if (mode == R3DSDK::DECODE_HALF_RES_GOOD || mode == R3DSDK::DECODE_HALF_RES_PREMIUM) {
        divisor = 2;
    } else if (mode == R3DSDK::DECODE_QUARTER_RES_GOOD) {
        divisor = 4;
    } else if (mode == R3DSDK::DECODE_EIGHT_RES_GOOD) {
        divisor = 8;
    } else if (mode == R3DSDK::DECODE_SIXTEENTH_RES_GOOD) {
        divisor = 16;
    }
    return std::max<size_t>(1, value / divisor);
}

unsigned char *aligned_malloc(size_t &adjusted, size_t size_needed) {
    unsigned char *raw = static_cast<unsigned char *>(std::malloc(size_needed + 15U));
    if (raw == nullptr) {
        return nullptr;
    }
    adjusted = 0U;
    auto ptr = reinterpret_cast<uintptr_t>(raw);
    if ((ptr % 16U) == 0U) {
        return raw;
    }
    adjusted = 16U - (ptr % 16U);
    return raw + adjusted;
}

int initialize(const char *sdk_libraries_path) {
    R3DSDK::InitializeStatus status = R3DSDK::InitializeSdk(sdk_libraries_path, OPTION_RED_NONE);
    if (status != R3DSDK::ISInitializeOK) {
        std::ostringstream message;
        message << "Failed to initialize RED R3D SDK: " << static_cast<int>(status)
                << " version=" << R3DSDK::GetSdkVersion();
        print_error(message.str());
        R3DSDK::FinalizeSdk();
        return 2;
    }
    return 0;
}

int version(const char *sdk_libraries_path) {
    if (initialize(sdk_libraries_path) != 0) {
        return 2;
    }
    std::cout << "{\"ok\":true,\"sdk_version\":\"" << json_escape(R3DSDK::GetSdkVersion()) << "\"}";
    R3DSDK::FinalizeSdk();
    return 0;
}

int probe(const char *source_path, const char *sdk_libraries_path) {
    if (initialize(sdk_libraries_path) != 0) {
        return 2;
    }
    std::unique_ptr<R3DSDK::Clip> clip(new R3DSDK::Clip(source_path));
    if (clip->Status() != R3DSDK::LSClipLoaded) {
        print_error("Error loading R3D clip");
        clip.reset();
        R3DSDK::FinalizeSdk();
        return 2;
    }

    double fps = static_cast<double>(clip->VideoAudioFramerate());
    size_t frame_count = clip->VideoFrameCount();
    double duration = fps > 0.0 ? static_cast<double>(frame_count) / fps : 0.0;
    std::string start_tc = frame_count > 0 ? std::string(clip->AbsoluteTimecode(0U)) : "";
    std::string end_tc = frame_count > 0 ? std::string(clip->AbsoluteTimecode(frame_count - 1U)) : "";

    std::cout << "{\"ok\":true"
              << ",\"sdk_version\":\"" << json_escape(R3DSDK::GetSdkVersion()) << "\""
              << ",\"width\":" << static_cast<unsigned int>(clip->Width())
              << ",\"height\":" << static_cast<unsigned int>(clip->Height())
              << ",\"fps\":" << fps
              << ",\"frame_count\":" << static_cast<unsigned int>(frame_count)
              << ",\"duration_seconds\":" << duration
              << ",\"start_timecode\":\"" << json_escape(start_tc) << "\""
              << ",\"end_timecode\":\"" << json_escape(end_tc) << "\""
              << "}";
    clip.reset();
    R3DSDK::FinalizeSdk();
    return 0;
}

int capture(const char *source_path, size_t frame_index, const char *output_path, const char *sdk_libraries_path) {
    if (initialize(sdk_libraries_path) != 0) {
        return 2;
    }
    std::unique_ptr<R3DSDK::Clip> clip(new R3DSDK::Clip(source_path));
    if (clip->Status() != R3DSDK::LSClipLoaded) {
        print_error("Error loading R3D clip");
        clip.reset();
        R3DSDK::FinalizeSdk();
        return 2;
    }
    if (clip->VideoFrameCount() == 0) {
        print_error("R3D clip has no video frames");
        clip.reset();
        R3DSDK::FinalizeSdk();
        return 2;
    }
    frame_index = std::min(frame_index, clip->VideoFrameCount() - 1U);

    R3DSDK::VideoDecodeMode mode = R3DSDK::DECODE_QUARTER_RES_GOOD;
    size_t width = adjusted_dimension(clip->Width(), mode);
    size_t height = adjusted_dimension(clip->Height(), mode);
    size_t mem_needed = width * height * 3U;
    size_t adjusted = 0U;
    unsigned char *buffer = aligned_malloc(adjusted, mem_needed);
    if (buffer == nullptr) {
        print_error("Failed to allocate R3D decode buffer");
        clip.reset();
        R3DSDK::FinalizeSdk();
        return 2;
    }

    R3DSDK::VideoDecodeJob job;
    job.Mode = mode;
    job.PixelType = R3DSDK::PixelType_8Bit_BGR_Interleaved;
    job.OutputBuffer = buffer;
    job.OutputBufferSize = mem_needed;

    R3DSDK::DecodeStatus decode_status = clip->DecodeVideoFrame(frame_index, job);
    if (decode_status != R3DSDK::DSDecodeOK) {
        std::free(buffer - adjusted);
        std::ostringstream message;
        message << "R3D decode failed: " << static_cast<int>(decode_status);
        print_error(message.str());
        clip.reset();
        R3DSDK::FinalizeSdk();
        return 2;
    }

    std::ofstream output(output_path, std::ios::binary);
    if (!output) {
        std::free(buffer - adjusted);
        print_error("Could not create R3D PPM output");
        clip.reset();
        R3DSDK::FinalizeSdk();
        return 2;
    }
    output << "P6\n" << width << " " << height << "\n255\n";
    for (size_t index = 0; index < mem_needed; index += 3U) {
        unsigned char rgb[3] = {buffer[index + 2U], buffer[index + 1U], buffer[index]};
        output.write(reinterpret_cast<char *>(rgb), 3);
    }
    output.close();
    std::free(buffer - adjusted);

    std::cout << "{\"ok\":true"
              << ",\"width\":" << static_cast<unsigned int>(width)
              << ",\"height\":" << static_cast<unsigned int>(height)
              << ",\"frame_index\":" << static_cast<unsigned int>(frame_index)
              << "}";
    clip.reset();
    R3DSDK::FinalizeSdk();
    return 0;
}

} // namespace

int main(int argc, char *argv[]) {
    if (argc < 3) {
        print_error("Usage: r3d_native_helper <version|probe|capture> ... <sdk_libraries_path>");
        return 2;
    }
    std::string command = argv[1];
    if (command == "version" && argc == 3) {
        return version(argv[2]);
    }
    if (command == "probe" && argc == 4) {
        return probe(argv[2], argv[3]);
    }
    if (command == "capture" && argc == 6) {
        return capture(argv[2], static_cast<size_t>(std::strtoull(argv[3], nullptr, 10)), argv[4], argv[5]);
    }
    print_error("Invalid r3d_native_helper arguments");
    return 2;
}
