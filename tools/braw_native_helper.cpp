/*
 * DataHelper BRAW native helper.
 * Based on Blackmagic RAW SDK sample patterns. Requires locally installed SDK/runtime.
 */
#include "BlackmagicRawAPI.h"

#include <CoreFoundation/CoreFoundation.h>
#include <CoreGraphics/CoreGraphics.h>
#include <CoreServices/CoreServices.h>
#include <ImageIO/ImageIO.h>

#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

static const BlackmagicRawResourceFormat kResourceFormat = blackmagicRawResourceFormatRGBAU8;
static const int kBufferSize = 4096;

static std::string cf_to_string(CFStringRef value) {
    if (value == nullptr) return "";
    char buffer[kBufferSize];
    if (CFStringGetCString(value, buffer, sizeof(buffer), kCFStringEncodingUTF8)) {
        return std::string(buffer);
    }
    return "";
}

static CFStringRef cf_from_path(const char* path) {
    return CFStringCreateWithCString(nullptr, path, kCFStringEncodingUTF8);
}

static std::string json_escape(const std::string& input) {
    std::ostringstream out;
    for (unsigned char c : input) {
        switch (c) {
            case '\\': out << "\\\\"; break;
            case '"': out << "\\\""; break;
            case '\b': out << "\\b"; break;
            case '\f': out << "\\f"; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default:
                if (c < 0x20) {
                    out << "\\u" << std::hex << std::uppercase << (int)c;
                } else {
                    out << c;
                }
        }
    }
    return out.str();
}

static std::string variant_to_string(Variant* value) {
    std::ostringstream out;
    switch (value->vt) {
        case blackmagicRawVariantTypeS16: out << value->iVal; break;
        case blackmagicRawVariantTypeU16: out << value->uiVal; break;
        case blackmagicRawVariantTypeS32: out << value->intVal; break;
        case blackmagicRawVariantTypeU32: out << value->uintVal; break;
        case blackmagicRawVariantTypeFloat32: out << value->fltVal; break;
        case blackmagicRawVariantTypeString: out << cf_to_string(value->bstrVal); break;
        case blackmagicRawVariantTypeSafeArray: {
            SafeArray* safeArray = value->parray;
            if (safeArray == nullptr) break;
            void* data = nullptr;
            if (SafeArrayAccessData(safeArray, &data) != S_OK) break;
            BlackmagicRawVariantType arrayType;
            long lower = 0;
            long upper = -1;
            if (SafeArrayGetVartype(safeArray, &arrayType) == S_OK &&
                SafeArrayGetLBound(safeArray, 1, &lower) == S_OK &&
                SafeArrayGetUBound(safeArray, 1, &upper) == S_OK) {
                long count = std::min<long>((upper - lower) + 1, 32);
                for (long i = 0; i < count; ++i) {
                    if (i > 0) out << " ";
                    switch (arrayType) {
                        case blackmagicRawVariantTypeU8: out << (int)(static_cast<unsigned char*>(data)[i]); break;
                        case blackmagicRawVariantTypeS16: out << static_cast<short*>(data)[i]; break;
                        case blackmagicRawVariantTypeU16: out << static_cast<unsigned short*>(data)[i]; break;
                        case blackmagicRawVariantTypeS32: out << static_cast<int*>(data)[i]; break;
                        case blackmagicRawVariantTypeU32: out << static_cast<unsigned int*>(data)[i]; break;
                        case blackmagicRawVariantTypeFloat32: out << static_cast<float*>(data)[i]; break;
                        default: break;
                    }
                }
            }
            SafeArrayUnaccessData(safeArray);
            break;
        }
        default: break;
    }
    return out.str();
}

static void collect_metadata(IBlackmagicRawMetadataIterator* iterator, const std::string& prefix, std::map<std::string, std::string>& metadata) {
    if (iterator == nullptr) return;
    CFStringRef key = nullptr;
    int seen = 0;
    while (seen < 256 && SUCCEEDED(iterator->GetKey(&key))) {
        std::string keyString = cf_to_string(key);
        Variant value;
        VariantInit(&value);
        if (!keyString.empty() && iterator->GetData(&value) == S_OK) {
            metadata[prefix + keyString] = variant_to_string(&value);
        }
        ++seen;
    }
}

class ProbeCallback : public IBlackmagicRawCallback {
public:
    IBlackmagicRawFrame* frame = nullptr;
    std::atomic<int32_t> refs{0};

    ~ProbeCallback() override { if (frame) frame->Release(); }
    void ReadComplete(IBlackmagicRawJob*, HRESULT result, IBlackmagicRawFrame* readFrame) override {
        if (result == S_OK && readFrame != nullptr) {
            if (frame) frame->Release();
            frame = readFrame;
            frame->AddRef();
        }
    }
    void ProcessComplete(IBlackmagicRawJob*, HRESULT, IBlackmagicRawProcessedImage*) override {}
    void DecodeComplete(IBlackmagicRawJob*, HRESULT) override {}
    void TrimProgress(IBlackmagicRawJob*, float) override {}
    void TrimComplete(IBlackmagicRawJob*, HRESULT) override {}
    void SidecarMetadataParseWarning(IBlackmagicRawClip*, CFStringRef, uint32_t, CFStringRef) override {}
    void SidecarMetadataParseError(IBlackmagicRawClip*, CFStringRef, uint32_t, CFStringRef) override {}
    void PreparePipelineComplete(void*, HRESULT) override {}
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID, LPVOID*) override { return E_NOTIMPL; }
    ULONG STDMETHODCALLTYPE AddRef() override { return ++refs; }
    ULONG STDMETHODCALLTYPE Release() override { auto v = --refs; if (v == 0) delete this; return v; }
};

class CaptureCallback : public IBlackmagicRawCallback {
public:
    explicit CaptureCallback(CFStringRef outputPath) : outputPath_(outputPath) { CFRetain(outputPath_); }
    ~CaptureCallback() override { CFRelease(outputPath_); }
    bool wrote = false;
    HRESULT finalResult = S_OK;

    void ReadComplete(IBlackmagicRawJob* readJob, HRESULT result, IBlackmagicRawFrame* frame) override {
        IBlackmagicRawJob* processJob = nullptr;
        if (result == S_OK) result = frame->SetResourceFormat(kResourceFormat);
        if (result == S_OK) result = frame->CreateJobDecodeAndProcessFrame(nullptr, nullptr, &processJob);
        if (result == S_OK) result = processJob->Submit();
        if (result != S_OK && processJob != nullptr) processJob->Release();
        if (result != S_OK) finalResult = result;
        readJob->Release();
    }

    void ProcessComplete(IBlackmagicRawJob* job, HRESULT result, IBlackmagicRawProcessedImage* processedImage) override {
        uint32_t width = 0, height = 0, sizeBytes = 0;
        void* imageData = nullptr;
        if (result == S_OK) result = processedImage->GetWidth(&width);
        if (result == S_OK) result = processedImage->GetHeight(&height);
        if (result == S_OK) result = processedImage->GetResourceSizeBytes(&sizeBytes);
        if (result == S_OK) result = processedImage->GetResource(&imageData);
        if (result == S_OK) result = write_png(width, height, sizeBytes, imageData) ? S_OK : E_FAIL;
        finalResult = result;
        job->Release();
    }

    void DecodeComplete(IBlackmagicRawJob*, HRESULT) override {}
    void TrimProgress(IBlackmagicRawJob*, float) override {}
    void TrimComplete(IBlackmagicRawJob*, HRESULT) override {}
    void SidecarMetadataParseWarning(IBlackmagicRawClip*, CFStringRef, uint32_t, CFStringRef) override {}
    void SidecarMetadataParseError(IBlackmagicRawClip*, CFStringRef, uint32_t, CFStringRef) override {}
    void PreparePipelineComplete(void*, HRESULT) override {}
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID, LPVOID*) override { return E_NOTIMPL; }
    ULONG STDMETHODCALLTYPE AddRef() override { return 1; }
    ULONG STDMETHODCALLTYPE Release() override { return 1; }

private:
    CFStringRef outputPath_;

    bool write_png(uint32_t width, uint32_t height, uint32_t sizeBytes, void* imageData) {
        CFURLRef file = CFURLCreateWithFileSystemPath(kCFAllocatorDefault, outputPath_, kCFURLPOSIXPathStyle, false);
        if (file == nullptr) return false;
        CGColorSpaceRef space = CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
        CGDataProviderRef provider = CGDataProviderCreateWithData(nullptr, imageData, sizeBytes, nullptr);
        CGImageRef imageRef = CGImageCreate(width, height, 8, 32, 4 * width, space, kCGImageAlphaNoneSkipLast | kCGImageByteOrderDefault, provider, nullptr, false, kCGRenderingIntentDefault);
        bool ok = false;
        if (imageRef != nullptr) {
            CGImageDestinationRef dest = CGImageDestinationCreateWithURL(file, kUTTypePNG, 1, nullptr);
            if (dest != nullptr) {
                CGImageDestinationAddImage(dest, imageRef, nullptr);
                ok = CGImageDestinationFinalize(dest);
                CFRelease(dest);
            }
            CGImageRelease(imageRef);
        }
        CGDataProviderRelease(provider);
        CGColorSpaceRelease(space);
        CFRelease(file);
        wrote = ok;
        return ok;
    }
};

static IBlackmagicRawFactory* make_factory(const char* sdkLibPath) {
    CFStringRef path = cf_from_path(sdkLibPath);
    IBlackmagicRawFactory* factory = CreateBlackmagicRawFactoryInstanceFromPath(path);
    CFRelease(path);
    return factory;
}

static int fail_json(const std::string& message) {
    std::cout << "{\"ok\":false,\"error\":\"" << json_escape(message) << "\"}" << std::endl;
    return 2;
}

static int check_runtime(const char* sdkLibPath) {
    IBlackmagicRawFactory* factory = make_factory(sdkLibPath);
    if (!factory) return fail_json("Failed to create Blackmagic RAW factory. Verify Blackmagic RAW SDK/runtime 5.1 is installed and sdk_libraries_path points to the SDK Mac/Libraries directory.");
    IBlackmagicRaw* codec = nullptr;
    HRESULT result = factory->CreateCodec(&codec);
    if (result != S_OK || codec == nullptr) {
        if (codec) codec->Release();
        factory->Release();
        return fail_json("Failed to create Blackmagic RAW codec. Verify the SDK framework can be loaded and initialized.");
    }
    codec->Release();
    factory->Release();
    std::cout << "{\"ok\":true,\"sdk_initialized\":true}" << std::endl;
    return 0;
}

static int probe_clip(const char* clipPath, const char* sdkLibPath) {
    IBlackmagicRawFactory* factory = make_factory(sdkLibPath);
    if (!factory) return fail_json("Failed to create Blackmagic RAW factory. Verify Blackmagic RAW SDK/runtime 5.1 is installed and sdk_libraries_path points to the SDK Mac/Libraries directory.");
    IBlackmagicRaw* codec = nullptr;
    IBlackmagicRawClip* clip = nullptr;
    CFStringRef clipName = cf_from_path(clipPath);
    HRESULT result = factory->CreateCodec(&codec);
    if (result == S_OK) result = codec->OpenClip(clipName, &clip);
    if (result != S_OK || clip == nullptr) {
        if (codec) codec->Release();
        factory->Release();
        CFRelease(clipName);
        return fail_json("Failed to open BRAW clip via Blackmagic RAW SDK.");
    }

    uint32_t width = 0, height = 0;
    float fps = 0.0f;
    uint64_t frameCount = 0;
    clip->GetWidth(&width);
    clip->GetHeight(&height);
    clip->GetFrameRate(&fps);
    clip->GetFrameCount(&frameCount);
    CFStringRef tc = nullptr;
    std::string startTimecode;
    if (clip->GetTimecodeForFrame(0, &tc) == S_OK && tc != nullptr) {
        startTimecode = cf_to_string(tc);
        CFRelease(tc);
    }

    std::map<std::string, std::string> metadata;
    IBlackmagicRawMetadataIterator* clipIt = nullptr;
    if (clip->GetMetadataIterator(&clipIt) == S_OK) {
        collect_metadata(clipIt, "clip.", metadata);
        clipIt->Release();
    }

    ProbeCallback* callback = new ProbeCallback();
    callback->AddRef();
    if (codec->SetCallback(callback) == S_OK && frameCount > 0) {
        IBlackmagicRawJob* readJob = nullptr;
        if (clip->CreateJobReadFrame(0, &readJob) == S_OK && readJob->Submit() == S_OK) {
            readJob->Release();
            codec->FlushJobs();
            if (callback->frame != nullptr) {
                IBlackmagicRawMetadataIterator* frameIt = nullptr;
                if (callback->frame->GetMetadataIterator(&frameIt) == S_OK) {
                    collect_metadata(frameIt, "frame0.", metadata);
                    frameIt->Release();
                }
            }
        } else if (readJob != nullptr) {
            readJob->Release();
        }
    }
    callback->Release();

    double duration = (fps > 0.0f) ? static_cast<double>(frameCount) / static_cast<double>(fps) : 0.0;
    std::cout << "{\"ok\":true,\"frame_count\":" << frameCount
              << ",\"fps\":" << fps
              << ",\"duration_seconds\":" << duration
              << ",\"width\":" << width
              << ",\"height\":" << height
              << ",\"start_timecode\":\"" << json_escape(startTimecode) << "\""
              << ",\"metadata\":{";
    bool first = true;
    for (const auto& item : metadata) {
        if (!first) std::cout << ",";
        first = false;
        std::cout << "\"" << json_escape(item.first) << "\":\"" << json_escape(item.second) << "\"";
    }
    std::cout << "}}" << std::endl;

    clip->Release();
    codec->Release();
    factory->Release();
    CFRelease(clipName);
    return 0;
}

static int capture_frame(const char* clipPath, uint64_t frameIndex, const char* outputPath, const char* sdkLibPath) {
    IBlackmagicRawFactory* factory = make_factory(sdkLibPath);
    if (!factory) return fail_json("Failed to create Blackmagic RAW factory. Verify Blackmagic RAW SDK/runtime 5.1 is installed and sdk_libraries_path points to the SDK Mac/Libraries directory.");
    IBlackmagicRaw* codec = nullptr;
    IBlackmagicRawClip* clip = nullptr;
    CFStringRef clipName = cf_from_path(clipPath);
    HRESULT result = factory->CreateCodec(&codec);
    if (result == S_OK) result = codec->OpenClip(clipName, &clip);
    if (result != S_OK || clip == nullptr) {
        if (codec) codec->Release();
        factory->Release();
        CFRelease(clipName);
        return fail_json("Failed to open BRAW clip via Blackmagic RAW SDK.");
    }
    uint64_t frameCount = 0;
    clip->GetFrameCount(&frameCount);
    if (frameCount == 0 || frameIndex >= frameCount) frameIndex = frameCount > 0 ? frameCount - 1 : 0;

    CFStringRef outName = cf_from_path(outputPath);
    CaptureCallback callback(outName);
    CFRelease(outName);
    result = codec->SetCallback(&callback);
    IBlackmagicRawJob* readJob = nullptr;
    if (result == S_OK) result = clip->CreateJobReadFrame(frameIndex, &readJob);
    if (result == S_OK) result = readJob->Submit();
    if (result != S_OK) {
        if (readJob) readJob->Release();
    } else {
        codec->FlushJobs();
        result = callback.finalResult;
    }

    clip->Release();
    codec->Release();
    factory->Release();
    CFRelease(clipName);

    if (result != S_OK || !callback.wrote) return fail_json("Failed to decode/write BRAW frame via Blackmagic RAW SDK.");
    std::cout << "{\"ok\":true,\"actual_frame_index\":" << frameIndex << ",\"image_path\":\"" << json_escape(outputPath) << "\"}" << std::endl;
    return 0;
}

int main(int argc, const char* argv[]) {
    if (argc < 2) return fail_json("Usage: braw_native_helper version [SDK_LIBRARIES] | probe CLIP [SDK_LIBRARIES] | capture CLIP FRAME OUTPUT [SDK_LIBRARIES]");
    std::string command = argv[1];
    const char* defaultLibs = "/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries";
    if (command == "version") {
        const char* libs = argc >= 3 ? argv[2] : defaultLibs;
        return check_runtime(libs);
    }
    if (command == "probe") {
        if (argc < 3) return fail_json("Usage: braw_native_helper probe CLIP [SDK_LIBRARIES]");
        const char* libs = argc >= 4 ? argv[3] : defaultLibs;
        return probe_clip(argv[2], libs);
    }
    if (command == "capture") {
        if (argc < 5) return fail_json("Usage: braw_native_helper capture CLIP FRAME OUTPUT [SDK_LIBRARIES]");
        uint64_t frame = std::strtoull(argv[3], nullptr, 10);
        const char* libs = argc >= 6 ? argv[5] : defaultLibs;
        return capture_frame(argv[2], frame, argv[4], libs);
    }
    return fail_json("Unknown command.");
}
