#include "BlackmagicRawAPI.h"
#include <CoreFoundation/CoreFoundation.h>
#include <iostream>
#include <cmath>

static void print_cf(const char* key, CFStringRef s) {
  if (!s) return;
  char buf[2048];
  if (CFStringGetCString(s, buf, sizeof(buf), kCFStringEncodingUTF8)) std::cout << key << "=" << buf << "\n";
}
static void print_meta(IBlackmagicRawClip* clip, const char* key) {
  Variant v; VariantInit(&v); CFStringRef k=CFStringCreateWithCString(nullptr,key,kCFStringEncodingUTF8);
  if (k && clip->GetMetadata(k,&v)==S_OK) {
    if (v.vt==blackmagicRawVariantTypeString) print_cf(key, v.bstrVal);
    else if (v.vt==blackmagicRawVariantTypeS32) std::cout<<key<<"="<<v.intVal<<"\n";
    else if (v.vt==blackmagicRawVariantTypeU32) std::cout<<key<<"="<<v.uintVal<<"\n";
    else if (v.vt==blackmagicRawVariantTypeFloat32) std::cout<<key<<"="<<v.fltVal<<"\n";
    VariantClear(&v);
  }
  if (k) CFRelease(k);
}
int main(int argc, const char* argv[]) {
  if (argc != 2) { std::cerr << "Usage: " << argv[0] << " clip.braw\n"; return 1; }
  CFStringRef clipName = CFStringCreateWithCString(nullptr, argv[1], kCFStringEncodingUTF8);
  IBlackmagicRawFactory* factory = CreateBlackmagicRawFactoryInstanceFromPath(CFSTR("/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries"));
  if (!factory) { std::cerr << "Blackmagic RAW SDK runtime not found at /Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries\n"; return 2; }
  IBlackmagicRaw* codec=nullptr; IBlackmagicRawClip* clip=nullptr; HRESULT r=factory->CreateCodec(&codec);
  if (r!=S_OK || !codec) { std::cerr << "Failed to create Blackmagic RAW codec\n"; factory->Release(); return 3; }
  r=codec->OpenClip(clipName, &clip); if (r!=S_OK || !clip) { std::cerr << "Failed to open BRAW clip\n"; codec->Release(); factory->Release(); CFRelease(clipName); return 4; }
  uint32_t w=0,h=0; uint64_t fc=0; float fps=0; CFStringRef tc=nullptr; CFStringRef camera=nullptr;
  clip->GetWidth(&w); clip->GetHeight(&h); clip->GetFrameCount(&fc); clip->GetFrameRate(&fps); clip->GetTimecodeForFrame(0,&tc); clip->GetCameraType(&camera);
  std::cout << "width="<<w<<"\nheight="<<h<<"\nframe_count="<<fc<<"\nfps="<<fps<<"\n";
  print_cf("start_timecode", tc); print_cf("camera_type", camera);
  print_meta(clip,"manufacturer"); print_meta(clip,"camera_id"); print_meta(clip,"reel_name"); print_meta(clip,"clip_number"); print_meta(clip,"date_recorded");
  if (tc) CFRelease(tc); if (camera) CFRelease(camera); clip->Release(); codec->Release(); factory->Release(); CFRelease(clipName); return 0;
}
