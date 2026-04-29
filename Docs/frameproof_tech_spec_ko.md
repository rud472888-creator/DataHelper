# Frame Proof PDF Generator - Technical Specification

**문서 버전:** v0.2  
**작성일:** 2026-04-22  
**상태:** 구현 기획용 Draft  
**제품 가칭:** Frame Proof PDF Generator / Clip Contact Report

---

## 1. 제품 정의

본 프로그램은 사용자가 선택한 영상 원본 파일 또는 폴더를 스캔하여, 각 클립의 핵심 메타데이터와 시작/중간/끝 프레임 캡처를 자동으로 수집하고, 이를 PDF 리포트로 생성하는 로컬 데스크톱/CLI 도구다.

핵심 사용 목적은 다음과 같다.

- 촬영 원본 검수용 contact sheet 생성
- 백업/인수인계/납품 증빙용 PDF 생성
- 편집/후반 작업자가 원본을 직접 열지 않고 클립 내용을 빠르게 훑어보는 색인 문서 생성
- RAW 계열 원본(BRAW, R3D, ARRIRAW)의 메타데이터와 대표 프레임을 포함한 일관된 리포트 생성

---

## 2. 확정된 제품 조건

| 항목 | 결정 |
|---|---|
| 필수 RAW 지원 | BRAW, R3D, ARRIRAW |
| 일반 영상 지원 | MOV, MP4, MXF, AVI 등 FFmpeg/FFprobe 처리 가능 포맷 |
| 프레임 추출 규칙 | 시작 1장 + 중간 0~3장 + 끝 1장 |
| 중간 프레임 위치 | 균등 분할 |
| 시작 프레임 | 첫 디코딩 가능한 유효 프레임 |
| 끝 프레임 | 마지막 디코딩 가능한 유효 프레임 |
| 기본 PDF 레이아웃 | Layout B: 여러 클립을 한 페이지에 배치하는 contact-sheet 방식 |
| 상세 옵션 선택 시 | Layout A: 클립당 1페이지 상세 리포트 방식 |
| 캡처 이미지 저장 기본값 | 별도 파일 저장 안 함. PDF 내부에만 삽입 |
| 캡처 이미지 별도 추출 옵션 | 선택 시 PNG로 export |
| 메타데이터/timecode 규칙 | 원본 메타데이터 우선, 없으면 elapsed time fallback |
| 실패 처리 | 파일 단위 실패 허용, 전체 배치 중단 금지 |
| 출력 보조 로그 | CSV 및 JSON manifest 생성 권장 |

---

## 3. v1 범위

### 3.1 In Scope

- 파일/폴더/하위 폴더 스캔
- 클립 단위 grouping
- BRAW, R3D, ARRIRAW, MOV, MP4, MXF, AVI 지원
- 클립별 metadata probe
- 시작/중간/끝 프레임 추출
- Layout B 기본 PDF 생성
- 상세 옵션 선택 시 Layout A PDF 생성
- PDF 내 썸네일/프레임 삽입
- PNG 별도 export 옵션
- CSV/JSON 처리 로그 생성
- 실패/경고 클립 목록을 PDF 마지막 또는 별도 로그에 기록
- GUI와 CLI 동시 지원

### 3.2 Out of Scope for v1

- 컬러 그레이딩용 기준 이미지 생성
- 최종 마스터 QC급 색 정확도 보장
- DaVinci Resolve, Premiere Pro, ShotGrid, Notion 직접 연동
- 체크섬 백업 리포트 통합
- 장면 변화 기반 자동 best frame 선택
- OCR, 자막 추출, 오디오 파형 분석
- 클라우드 업로드/협업 기능

---

## 4. 지원 포맷 및 어댑터 전략

이 제품은 FFmpeg 하나로 모든 포맷을 처리하는 구조가 아니라, **포맷별 adapter layer**를 둔다. 특히 BRAW, R3D, ARRIRAW는 vendor SDK 또는 공식 reference tool을 우선 사용한다.

### 4.1 Format Support Matrix

| 포맷군 | 확장자/형태 | v1 지원 방식 | Primary probe | Primary capture | 비고 |
|---|---|---|---|---|---|
| Standard video | `.mov`, `.mp4`, `.mxf`, `.avi` | 직접 지원 | FFprobe + MediaInfo fallback | FFmpeg | MOV tmcd timecode, MXF metadata 등 |
| BRAW | `.braw` | 필수 지원 | Blackmagic RAW SDK adapter | Blackmagic RAW SDK adapter | native CLI adapter 권장 |
| RED R3D | `.r3d` | 필수 지원 | RED R3D SDK adapter | RED R3D SDK adapter | multi-file R3D clip grouping 필요 |
| ARRIRAW | `.ari`, MXF/ARRIRAW `.mxf` | 필수 지원 | ARRI Reference Tool CMD adapter | ARRI Reference Tool CMD adapter | native ARRI SDK 사용 가능 시 대체 가능 |
| ARRIRAW HDE | `.arx`, MXF/HDE | v1.1 후보 | ARRI Reference Tool CMD | ARRI Reference Tool CMD | ARRIRAW 요구 범위에 포함할지 별도 결정 가능 |
| Image sequence | `.dpx`, `.exr`, `.tif` sequence | v2 후보 | sequence scanner | image reader | 현재 요구 범위 밖 |

### 4.2 Adapter Layer 원칙

각 adapter는 동일한 인터페이스를 가져야 한다.

```text
probe(input_path) -> ClipInfo
capture(input_path, CapturePlan, CaptureProfile) -> CaptureResult[]
```

모든 adapter는 내부 구현 방식이 달라도 다음을 보장한다.

- normalized metadata schema 반환
- frame_count 또는 duration_seconds 중 최소 하나 반환
- 가능한 경우 start_timecode 반환
- 각 캡처 결과에 actual_frame_index 또는 actual_seconds 반환
- PNG 이미지 bytes 또는 staging image path 반환
- 오류 발생 시 adapter 단위 exception을 JSON error로 변환

### 4.3 Adapter Process Isolation

BRAW/R3D/ARRIRAW SDK는 크래시, GPU 드라이버, 라이선스, OS dependency 이슈가 있을 수 있다. 따라서 각 RAW adapter는 Python process 내부에 직접 import하지 않고, **별도 CLI subprocess**로 실행한다.

권장 구조:

```text
app/
  core/
    scanner.py
    report_builder.py
    metadata_normalizer.py
    timecode.py
  adapters/
    ffmpeg_adapter.py
    braw_adapter_client.py
    r3d_adapter_client.py
    arriraw_art_adapter_client.py
  native/
    braw_adapter   또는 braw_adapter.exe
    r3d_adapter    또는 r3d_adapter.exe
  tools/
    ffmpeg
    ffprobe
    mediainfo
```

---

## 5. RAW 포맷별 구현 방침

### 5.1 BRAW

BRAW는 Blackmagic RAW SDK 기반 adapter를 사용한다.

#### 요구사항

- `.braw` 파일 open
- clip metadata 추출
- frame count, fps, resolution, duration 추출
- start timecode 또는 clip timecode 추출
- 지정 frame index 또는 timestamp 근방의 프레임 decode
- preview용 색 변환 적용 후 PNG 출력

#### 권장 구현

- C++ native adapter 작성
- CLI 입출력은 JSON 사용
- SDK decode 결과를 8-bit 또는 16-bit RGB image buffer로 변환
- 최종 PDF용 PNG는 8-bit sRGB preview 사용
- color-critical 목적이 아니라는 disclaimer를 PDF 하단 또는 metadata에 표시

#### Adapter CLI 예시

```bash
braw_adapter probe /path/A001_0001.braw --json
braw_adapter capture /path/A001_0001.braw \
  --frames 0,120,240,360 \
  --profile preview_rec709 \
  --out /tmp/frameproof/A001_0001
```

### 5.2 R3D

R3D는 RED R3D SDK 기반 adapter를 사용한다.

#### 요구사항

- `.r3d` logical clip open
- multi-part R3D clip의 part files 식별
- clip metadata 및 per-frame metadata 추출
- frame count, fps, resolution, start timecode 추출
- 지정 frame index의 decode
- RMD sidecar metadata가 있는 경우 병합 또는 별도 표시

#### 권장 구현

- C++ native adapter 작성
- SDK의 clip open/decode API 사용
- per-frame metadata가 필요한 경우 adapter 내부에서 timecode 및 frame metadata 반환
- GPU decode 사용 가능하되, 기본값은 안정성 우선으로 CPU 또는 safe GPU mode 선택
- 동시 처리 개수 제한. 기본값: RAW adapter concurrency = 1

#### Adapter CLI 예시

```bash
r3d_adapter probe /path/A001_C001_001.R3D --json
r3d_adapter capture /path/A001_C001_001.R3D \
  --frames 0,500,1000,1499 \
  --profile ipp2_preview_rec709 \
  --out /tmp/frameproof/A001_C001
```

### 5.3 ARRIRAW

ARRIRAW는 v1에서 ARRI Reference Tool CMD를 감싼 adapter를 우선 사용한다. 추후 ARRI SDK 사용 권한 및 배포 조건이 명확해지면 native adapter로 전환할 수 있다.

#### 지원 대상

- `.ari`
- MXF/ARRIRAW `.mxf`
- 필요 시 HDE `.arx` 및 MXF/HDE는 v1.1 옵션으로 확장

#### 요구사항

- ARRIRAW/MXF-ARRIRAW clip 인식
- static/dynamic metadata export
- 지정 프레임 또는 시간의 still extraction
- PNG 생성을 위해 TIFF/OpenEXR 등 intermediate를 생성한 뒤 PNG 변환 가능

#### 권장 구현

- `arriraw_art_adapter_client.py`에서 ART CMD 실행
- ART CMD로 metadata JSON/CSV export
- ART CMD Process Mode로 selected frame을 TIFF/OpenEXR로 생성
- Pillow/ImageMagick/FFmpeg 등으로 PDF 삽입용 PNG 변환
- ART CMD dependency path는 설정 화면에서 지정 가능하게 함

#### Adapter CLI 예시

```bash
arriraw_adapter probe /path/A001C001.mxf --json
arriraw_adapter capture /path/A001C001.mxf \
  --frames 0,250,500,749 \
  --profile arri_preview_rec709 \
  --out /tmp/frameproof/A001C001
```

---

## 6. 시스템 아키텍처

### 6.1 전체 구조

```text
User Input
  -> Scanner
  -> Clip Grouper
  -> Adapter Resolver
  -> Probe Service
  -> Capture Planner
  -> Capture Service
  -> Metadata Normalizer
  -> Report Renderer
  -> Output Writer
  -> Log/Manifest Writer
```

### 6.2 주요 모듈

| 모듈 | 책임 |
|---|---|
| `scanner.py` | 파일/폴더 스캔, 확장자 필터, recursive option |
| `clip_grouper.py` | R3D multi-part clip, image sequence 후보 등 logical clip grouping |
| `adapter_resolver.py` | 확장자/metadata 기반 adapter 선택 |
| `probe_service.py` | adapter probe 실행 및 원본 metadata 수집 |
| `capture_planner.py` | 시작/중간/끝 캡처 위치 계산 |
| `capture_service.py` | adapter capture 실행, temporary image 관리 |
| `metadata_normalizer.py` | 서로 다른 adapter metadata를 공통 schema로 변환 |
| `timecode.py` | timecode parsing, frame offset 계산, drop-frame 처리 |
| `pdf_renderer.py` | Layout B/A PDF 생성 |
| `still_exporter.py` | 선택 시 PNG 별도 저장 |
| `manifest_writer.py` | CSV/JSON 로그 작성 |
| `settings.py` | GUI/CLI config 로딩 및 validation |

---

## 7. 입력 옵션

### 7.1 GUI 입력

- Source files: 다중 파일 선택
- Source folder: 폴더 선택
- Include subfolders: 기본 ON
- File extensions: 기본 자동
- Output folder: 필수
- Project name: 선택
- Report mode:
  - `Contact Sheet (Layout B)` 기본
  - `Detailed File Report (Layout A)` 상세 파일 옵션 선택 시
- Middle frame count: 0, 1, 2, 3 중 선택
- Export still PNGs: 기본 OFF
- Include CSV manifest: 기본 ON
- Include JSON manifest: 기본 ON
- Failed files section in PDF: 기본 ON

### 7.2 CLI 입력

```bash
frameproof \
  --input "/Volumes/Footage/Day01" \
  --recursive \
  --middle-count 3 \
  --layout contact_sheet \
  --output "/Exports/Day01_Frame_Report.pdf" \
  --csv "/Exports/Day01_Frame_Report.csv" \
  --json "/Exports/Day01_Frame_Report.json"
```

상세 리포트 및 PNG export 예시:

```bash
frameproof \
  --input "/Volumes/Footage/Day01" \
  --recursive \
  --middle-count 2 \
  --layout detail \
  --export-stills \
  --stills-dir "/Exports/stills" \
  --output "/Exports/Day01_Detail_Report.pdf"
```

---

## 8. 캡처 위치 계산 규칙

### 8.1 기본 규칙

사용자는 중간 캡처 개수 `middle_count`를 0~3 사이에서 선택한다. 시작과 끝은 항상 포함한다.

| middle_count | 캡처 label | ratio |
|---:|---|---|
| 0 | Start, End | 0.0, 1.0 |
| 1 | Start, Mid1, End | 0.0, 0.5, 1.0 |
| 2 | Start, Mid1, Mid2, End | 0.0, 0.333..., 0.666..., 1.0 |
| 3 | Start, Mid1, Mid2, Mid3, End | 0.0, 0.25, 0.5, 0.75, 1.0 |

### 8.2 Frame Count 기반 계산

`frame_count`를 알 수 있는 경우 frame index를 우선 사용한다.

```text
start_index = 0
end_index = frame_count - 1
mid_index = round(ratio * (frame_count - 1))
```

예: `frame_count = 1000`, `middle_count = 3`

```text
Start = 0
Mid1  = 250
Mid2  = 500
Mid3  = 749 or 750, rounding policy에 따라 결정
End   = 999
```

#### Rounding policy

- 기본값: nearest integer
- tie-breaking: half-up이 아니라 banker's rounding을 피하기 위해 `floor(x + 0.5)` 사용
- 모든 adapter에서 동일한 rounding 함수를 사용

### 8.3 Duration 기반 계산

`frame_count`를 알 수 없거나 신뢰할 수 없는 경우 duration 기준으로 계산한다.

```text
requested_seconds = ratio * duration_seconds
```

단, 끝 프레임은 EOF seek 실패를 피하기 위해 다음을 사용한다.

```text
end_requested_seconds = max(duration_seconds - frame_duration, 0)
```

`frame_duration`을 알 수 없으면 `0.001s` 또는 adapter-specific safe epsilon을 사용한다.

### 8.4 짧은 클립 처리

클립이 너무 짧아 여러 label이 같은 frame을 가리키는 경우에도 slot은 유지한다.

예: 1 frame clip, `middle_count=3`

```text
Start = frame 0
Mid1  = frame 0, duplicate_of=Start
Mid2  = frame 0, duplicate_of=Start
Mid3  = frame 0, duplicate_of=Start
End   = frame 0, duplicate_of=Start
```

PDF에는 다음 warning을 표시한다.

```text
Warning: requested capture points collapsed to the same actual frame because the clip is too short.
```

### 8.5 실제 추출 시점 기록

PDF와 CSV/JSON에는 반드시 다음을 모두 기록한다.

- requested_ratio
- requested_frame_index 또는 requested_seconds
- actual_frame_index 또는 actual_seconds
- actual_timecode
- capture_status
- adapter_name

---

## 9. Timecode 규칙

### 9.1 우선순위

timecode는 다음 순서로 사용한다.

1. RAW/native adapter가 반환한 per-frame timecode
2. clip start timecode + actual frame offset
3. container/stream metadata의 timecode
4. elapsed time fallback

### 9.2 표시 형식

| 케이스 | 표시 |
|---|---|
| 정상 timecode | `HH:MM:SS:FF` |
| drop-frame timecode | `HH:MM:SS;FF` |
| timecode 없음 | `N/A` |
| elapsed fallback | `+HH:MM:SS.mmm` |
| 계산값 | `HH:MM:SS:FF (calculated)` |

### 9.3 Drop-frame 처리

- fps가 `30000/1001`, `60000/1001` 등 NTSC 계열이고 metadata에 drop-frame flag가 있으면 drop-frame으로 계산한다.
- flag가 없으면 non-drop으로 표시하고 `tc_drop_frame_unknown=true` 경고를 남긴다.
- PDF에는 사용자가 혼동하지 않도록 세미콜론(`;`)과 콜론(`:`) 구분을 유지한다.

### 9.4 VFR 처리

VFR 또는 fps 불명확 파일에서는 frame number 기반 timecode 합성을 하지 않는다. 이 경우 actual timestamp와 elapsed fallback을 우선 표시한다.

---

## 10. Metadata Normalization Schema

### 10.1 ClipInfo

```json
{
  "clip_id": "sha1-or-uuid",
  "clip_name": "A001_C001_0422AB",
  "logical_clip_name": "A001_C001",
  "source_path": "/Volumes/Footage/A001_C001.R3D",
  "part_files": [],
  "format_family": "r3d",
  "container": "R3D",
  "codec": "REDCODE RAW",
  "file_size_bytes": 123456789,
  "duration_seconds": 42.375,
  "frame_count": 1017,
  "fps_num": 24000,
  "fps_den": 1001,
  "width": 8192,
  "height": 4320,
  "camera_make": "RED",
  "camera_model": "V-RAPTOR",
  "reel": "A001",
  "camera_id": "A",
  "start_timecode": "01:00:00:00",
  "end_timecode": "01:00:42:16",
  "timecode_source": "native_adapter",
  "metadata_raw": {}
}
```

### 10.2 CapturePoint

```json
{
  "label": "Mid2",
  "requested_ratio": 0.5,
  "requested_frame_index": 508,
  "requested_seconds": 21.1875,
  "actual_frame_index": 508,
  "actual_seconds": 21.1875,
  "actual_timecode": "01:00:21:05",
  "actual_timecode_source": "native_adapter",
  "image_path_temp": "/tmp/frameproof/A001_C001_mid2.png",
  "image_path_exported": null,
  "duplicate_of": null,
  "status": "success",
  "warnings": []
}
```

### 10.3 ReportItem

```json
{
  "clip": {},
  "captures": [],
  "status": "success",
  "warnings": [],
  "errors": []
}
```

---

## 11. PDF 레이아웃

## 11.1 Layout B - Contact Sheet 기본값

Layout B는 기본 export 방식이다. 여러 클립을 한 페이지에 배치해 빠르게 훑어보는 목적이다.

### 페이지 구성

- Header
  - Project name
  - Source root
  - Generated at
  - Total clips / Success / Failed
  - middle_count
- Clip block 반복
  - Clip name
  - short metadata line
  - timecode range
  - thumbnails: Start / Mid1 / Mid2 / Mid3 / End
  - warnings icon/text
- Footer
  - page number
  - report file name
  - "Preview frames only - not color-critical" 표시

### Clip block 정보

Layout B에서는 과도한 metadata를 숨기고, 다음 정보만 기본 표시한다.

```text
Clip: A001_C001.R3D
TC: 01:00:00:00 - 01:00:42:16
Format: R3D | 8192x4320 | 23.976 fps | 42.4s
```

### 자동 밀도 정책

| 프레임 수 | 권장 clips/page |
|---:|---:|
| 2 frames | 6 clips/page |
| 3 frames | 4 clips/page |
| 4 frames | 3 clips/page |
| 5 frames | 2~3 clips/page |

기본 구현은 `auto`로 두고, 썸네일 최소 크기를 보장한다.

### Layout B 와이어프레임

```text
+----------------------------------------------------------+
| Project / Source / Generated / Summary                   |
+----------------------------------------------------------+
| Clip A001_C001 | TC 01:00:00:00 - 01:00:42:16             |
| [Start] [Mid1] [Mid2] [Mid3] [End]                       |
| Format | Resolution | FPS | Duration                     |
+----------------------------------------------------------+
| Clip A001_C002 | TC ...                                  |
| [Start] [Mid1] [Mid2] [Mid3] [End]                       |
| Format | Resolution | FPS | Duration                     |
+----------------------------------------------------------+
| Footer                                                   |
+----------------------------------------------------------+
```

---

## 11.2 Layout A - 상세 파일 옵션 선택 시

Layout A는 사용자가 "상세 파일 옵션"을 선택했을 때 사용한다. 클립당 1페이지를 생성한다.

### 페이지 구성

- Clip title
- Source path
- Metadata table
- Capture frames 2~5장
- 각 프레임 아래 상세 정보
  - label
  - requested ratio
  - requested frame/time
  - actual frame/time
  - actual timecode
- Warnings/errors
- Raw metadata summary 또는 collapsed appendix

### Layout A 와이어프레임

```text
+----------------------------------------------------------+
| Clip: A001_C001.R3D                                      |
| Path: /Volumes/Footage/A001_C001.R3D                     |
+----------------------+-----------------------------------+
| Format               | R3D                               |
| Resolution           | 8192 x 4320                       |
| FPS                  | 23.976                            |
| Duration             | 00:00:42.375                      |
| Start TC             | 01:00:00:00                       |
+----------------------+-----------------------------------+
| [Start]             [Mid1]              [Mid2]            |
| TC ...              TC ...              TC ...            |
| [Mid3]              [End]                                  |
| TC ...              TC ...                                 |
+----------------------------------------------------------+
```

---

## 12. PNG 별도 추출 옵션

### 12.1 기본 동작

기본값에서는 캡처 이미지를 PDF에만 삽입한다.

```text
export_stills = false
```

이 경우 pipeline은 temporary staging directory에 PNG를 생성한 뒤 PDF가 정상 생성되면 임시 파일을 삭제한다.

### 12.2 옵션 선택 시

사용자가 `Export still PNGs`를 선택하면 각 캡처 이미지를 별도 파일로 저장한다.

```text
export_stills = true
```

저장 규칙:

```text
/stills/
  A001_C001/
    A001_C001__start__tc_01000000.png
    A001_C001__mid1__tc_01001012.png
    A001_C001__mid2__tc_01002105.png
    A001_C001__mid3__tc_01003117.png
    A001_C001__end__tc_01004216.png
```

### 12.3 파일명 sanitize 규칙

- path separator 제거
- colon `:` 제거 또는 `_`로 치환
- drop-frame semicolon `;` 제거 또는 `_df_` 표기
- 동일 파일명 충돌 시 suffix 추가: `_001`, `_002`
- 원본 clip 이름이 너무 길면 hash suffix 사용

---

## 13. 출력 파일

### 13.1 기본 출력

```text
FrameProof_<project>_<YYYYMMDD_HHMMSS>.pdf
FrameProof_<project>_<YYYYMMDD_HHMMSS>.csv
FrameProof_<project>_<YYYYMMDD_HHMMSS>.json
```

### 13.2 CSV columns

| column | 설명 |
|---|---|
| `clip_name` | 파일명 |
| `source_path` | 원본 경로 |
| `format_family` | standard/braw/r3d/arriraw |
| `adapter_name` | 사용 adapter |
| `capture_label` | Start/Mid/End |
| `requested_ratio` | 0.0~1.0 |
| `requested_frame_index` | 요청 frame |
| `actual_frame_index` | 실제 추출 frame |
| `actual_seconds` | 실제 추출 timestamp |
| `actual_timecode` | 실제 timecode |
| `image_path` | PNG export 시 파일 경로 |
| `status` | success/failure |
| `warnings` | 경고 |
| `errors` | 오류 |

---

## 14. Report Rendering

### 14.1 PDF Engine

권장 engine은 Python + ReportLab이다.

이유:

- 이미지/표/텍스트를 programmatic하게 배치하기 쉽다.
- CLI/GUI와 독립적으로 rendering 가능하다.
- contact sheet와 detailed page를 모두 하나의 renderer에서 제어 가능하다.
- 한글 폰트 embedding을 제어할 수 있다.

### 14.2 이미지 처리

- PDF 삽입용 preview image는 PNG 사용
- 긴 변 기준 max pixel size를 제한해 PDF 용량 제어
- 기본 thumbnail max width:
  - Layout B: 360~480 px source thumbnail
  - Layout A: 720~1080 px source thumbnail
- 원본 RAW full-resolution frame을 PDF에 그대로 넣지 않는다.
- PDF용 preview와 별도 PNG export용 이미지는 동일 파일을 사용할 수 있지만, export quality 옵션을 분리할 수 있게 설계한다.

### 14.3 Color Pipeline

이 리포트는 색보정 판단용 reference가 아니라 **원본 식별 및 검수용 preview**다.

기본 profile:

```text
preview_rec709_sdr
```

포맷별 기본값:

| 포맷 | 기본 preview 처리 |
|---|---|
| Standard video | FFmpeg decode 후 sRGB/Rec.709 preview |
| BRAW | SDK default decode + Rec.709 preview transform |
| R3D | IPP2 또는 SDK default preview transform |
| ARRIRAW | ART/ARRI default preview or LogC to Rec.709 preview |

PDF footer에 다음 문구를 표시한다.

```text
Preview frames are for clip identification and review only; not a color-critical reference.
```

---

## 15. 설정 파일

설정은 GUI에서 저장 가능해야 하며, CLI에서도 JSON/YAML config를 받을 수 있어야 한다.

```json
{
  "input": {
    "paths": ["/Volumes/Footage/Day01"],
    "recursive": true,
    "extensions": ["mov", "mp4", "mxf", "avi", "braw", "r3d", "ari"]
  },
  "capture": {
    "middle_count": 3,
    "profile": "preview_rec709_sdr",
    "prefer_frame_index": true
  },
  "report": {
    "layout": "contact_sheet",
    "project_name": "Project Name",
    "include_failed_section": true,
    "include_summary_page": true
  },
  "output": {
    "pdf_path": "/Exports/FrameProof_Project_20260422.pdf",
    "export_stills": false,
    "stills_dir": "/Exports/stills",
    "write_csv": true,
    "write_json": true
  },
  "adapters": {
    "ffmpeg_path": "ffmpeg",
    "ffprobe_path": "ffprobe",
    "mediainfo_path": "mediainfo",
    "braw_adapter_path": "/Applications/FrameProof/native/braw_adapter",
    "r3d_adapter_path": "/Applications/FrameProof/native/r3d_adapter",
    "arri_art_cmd_path": "/Applications/ARRI Reference Tool/art-cmd"
  }
}
```

---

## 16. Dependency Management

### 16.1 Required

| Dependency | 목적 |
|---|---|
| Python runtime | core app, GUI, renderer |
| FFmpeg | standard video frame extraction |
| FFprobe | standard video metadata/timecode |
| MediaInfo | metadata fallback/cross-check |
| ReportLab | PDF rendering |
| Pillow | image resizing/conversion |
| PySide6 | desktop GUI |

### 16.2 RAW Dependencies

| Dependency | 목적 |
|---|---|
| Blackmagic RAW SDK | `.braw` metadata/decode |
| RED R3D SDK | `.r3d` metadata/decode |
| ARRI Reference Tool CMD | ARRIRAW metadata/export/process |

### 16.3 Bundling Policy

- FFmpeg/FFprobe bundling은 라이선스 검토 후 결정한다.
- proprietary SDK는 재배포 조건을 확인하기 전까지 앱에 무단 bundling하지 않는다.
- BRAW/R3D/ARRIRAW dependency는 installer 단계에서 사용자가 설치 경로를 지정하거나, 공식 설치 파일을 별도로 설치한 뒤 app 설정에서 path를 인식하게 한다.
- Adapter binary는 SDK 라이선스가 허용하는 범위 안에서만 배포한다.

---

## 17. 에러 처리

### 17.1 상태값

| status | 의미 |
|---|---|
| `success` | probe와 모든 capture 성공 |
| `partial_success` | 일부 capture 실패, 나머지 성공 |
| `probe_failed` | metadata probe 실패 |
| `decode_failed` | frame decode 실패 |
| `unsupported_format` | 지원하지 않는 포맷 |
| `dependency_missing` | adapter/SDK/tool 미설치 |
| `metadata_incomplete` | 핵심 metadata 일부 누락 |
| `skipped_duplicate` | 중복 logical clip 처리로 skip |

### 17.2 PDF 실패 섹션

PDF 마지막에 실패 섹션을 포함한다.

```text
Failed / Partial Clips
- A001_C003.R3D: decode_failed, failed at Mid2, adapter=r3d_adapter
- B002_0001.braw: metadata_incomplete, timecode missing, elapsed fallback used
```

### 17.3 전체 배치 중단 조건

다음 상황에서만 전체 작업을 중단한다.

- output path write 불가
- PDF renderer fatal error
- 사용자가 취소
- 모든 adapter dependency가 미설치되어 처리 가능한 파일이 0개

그 외에는 파일 단위로 실패 기록 후 계속 진행한다.

---

## 18. 성능 및 병렬 처리

### 18.1 기본 원칙

- Standard video는 병렬 처리 가능
- RAW decode는 GPU/CPU 부하가 크므로 제한된 병렬 처리
- PDF rendering은 캡처 완료 후 단일 pass로 수행
- 대용량 배치에서는 metadata probe와 capture를 분리해 progress를 표시

### 18.2 권장 기본값

| 작업 | concurrency |
|---|---:|
| scanner | 1 |
| standard probe | 4 |
| standard capture | 2 |
| BRAW capture | 1 |
| R3D capture | 1 |
| ARRIRAW capture | 1 |
| PDF rendering | 1 |

### 18.3 Cache

선택적으로 cache를 둔다.

Cache key:

```text
source_path + file_size + modified_time + adapter_version + capture_profile + middle_count
```

Cache 대상:

- normalized metadata
- temporary thumbnail
- capture result

---

## 19. GUI 설계

### 19.1 Main Screen

- Source selector
- Output selector
- Middle frame count selector
- Layout selector
  - Contact Sheet 기본
  - Detailed File Report
- Export still PNGs checkbox
- Start button
- Progress table

### 19.2 Dependency Check Screen

앱 시작 또는 설정 화면에서 dependency 상태를 표시한다.

```text
FFmpeg: OK
FFprobe: OK
MediaInfo: OK
BRAW Adapter: Missing
R3D Adapter: OK
ARRI Reference Tool CMD: OK
```

dependency가 없으면 해당 포맷 처리만 비활성화하고, 나머지 포맷은 계속 처리할 수 있다.

### 19.3 Progress Table

| column | 설명 |
|---|---|
| Clip | 클립명 |
| Format | 포맷 |
| Probe | 대기/진행/성공/실패 |
| Capture | 대기/진행/성공/부분성공/실패 |
| PDF | 포함 여부 |
| Warning | 요약 경고 |

---

## 20. 보안 및 파일 안전성

- 원본 파일은 절대 수정하지 않는다.
- RMD, sidecar, metadata 파일도 v1에서는 read-only로만 사용한다.
- 출력 폴더가 원본 폴더 내부인 경우 명시적으로 허용하되, 기본 추천은 별도 export 폴더다.
- path traversal 방지를 위해 export filename sanitize를 수행한다.
- 로그에 개인정보성 경로가 포함될 수 있으므로, 공유용 PDF에는 full path 숨김 옵션을 제공한다.
- 네트워크 업로드 기능은 없다.

---

## 21. 테스트 계획

### 21.1 Format Test Set

| 포맷 | 케이스 |
|---|---|
| MOV | timecode 있음/없음, ProRes, H.264 |
| MP4 | timecode 없음, VFR |
| MXF | OP1a, timecode 있음 |
| BRAW | timecode 있음/없음, 여러 fps |
| R3D | single-file, multi-file, RMD sidecar |
| ARRIRAW | `.ari`, MXF/ARRIRAW |
| Short clip | 1 frame, 2 frames, 1초 이하 |
| Damaged clip | probe 가능/decode 실패 |
| Long clip | 1시간 이상 |
| Non-ASCII path | 한글/공백/특수문자 경로 |

### 21.2 Functional Tests

- middle_count 0/1/2/3별 capture slot 수 확인
- Layout B 기본 export 확인
- 상세 옵션 선택 시 Layout A export 확인
- PNG export off일 때 stills 폴더 미생성 확인
- PNG export on일 때 PNG 파일명/경로 확인
- timecode fallback 동작 확인
- failed section 생성 확인
- CSV/JSON manifest와 PDF 내용 일치 확인

### 21.3 Acceptance Criteria

v1 릴리즈 기준:

- BRAW, R3D, ARRIRAW 각각 최소 3개 샘플 클립에서 probe/capture/PDF 생성 성공
- MOV/MP4/MXF/AVI standard test set에서 probe/capture/PDF 생성 성공
- middle_count 0~3 모든 값에서 PDF 레이아웃 깨짐 없음
- Layout B가 기본값으로 동작
- 상세 파일 옵션 선택 시 Layout A로 export
- PNG export 기본 OFF
- PNG export ON일 때 지정 폴더에 PNG 생성
- timecode가 없는 파일에서 `N/A` 또는 elapsed fallback이 명확히 표시
- 파일 하나 실패해도 나머지 파일은 계속 처리
- PDF와 manifest에 actual capture point 기록

---

## 22. 개발 마일스톤

### M1 - Core Standard Pipeline

- Scanner
- FFmpeg/FFprobe adapter
- capture planner
- metadata schema
- Layout B PDF renderer
- CSV/JSON manifest
- CLI

### M2 - RAW Adapter Integration

- BRAW native adapter
- R3D native adapter
- ARRIRAW ART CMD adapter
- adapter dependency detection
- RAW test clips integration

### M3 - Layout A and GUI

- Detailed File Report Layout A
- PySide6 GUI
- settings persistence
- progress table
- error/failure section UX

### M4 - Packaging and QA

- macOS package
- Windows installer
- dependency path setup
- regression test set
- PDF visual QA
- performance profiling

---

## 23. 주요 리스크 및 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| RAW SDK 재배포 제한 | installer/배포 복잡도 증가 | 사용자가 SDK/공식 툴 설치 후 path 지정 |
| RAW preview 색 차이 | 사용자 오해 가능 | PDF에 preview-only 문구 명시 |
| 마지막 프레임 seek 실패 | End capture 실패 | frame_count 기반 decode 우선, duration 기반일 때 epsilon 적용 |
| R3D multi-part grouping 실패 | 중복/누락 클립 | SDK file list API 또는 logical clip grouping 사용 |
| ARRIRAW ART CMD 속도 | 대량 처리 지연 | concurrency 1, cache, progress 표시 |
| timecode metadata 불완전 | TC 표시 오류 | source priority와 calculated/fallback label 표시 |
| GPU driver crash | 앱 전체 중단 | adapter subprocess isolation |

---

## 24. 구현 시 우선순위

1. 공통 schema와 capture planner를 먼저 고정한다.
2. Standard FFmpeg adapter로 PDF pipeline을 완성한다.
3. RAW adapter는 동일 JSON interface에 맞춰 하나씩 붙인다.
4. Layout B를 먼저 안정화한다.
5. Layout A는 같은 ReportItem 데이터를 더 자세히 보여주는 renderer variant로 구현한다.
6. PNG export는 capture 결과 저장 정책만 바꾸는 옵션으로 구현한다.
7. GUI는 CLI pipeline이 안정화된 뒤 붙인다.

---

## 25. Source References

아래 자료는 포맷 지원 및 구현 전략의 근거로 사용했다.

| 구분 | 출처 | 요지 |
|---|---|---|
| Blackmagic RAW SDK | https://www.blackmagicdesign.com/developer/products/braw/sdk-and-software | BRAW SDK 파일과 SDK manual 제공, Mac/Windows/Linux download 제공 |
| RED R3D SDK | https://www.red.com/download/r3d-sdk | R3D SDK release history, decode/metadata 관련 API 및 최신 release 정보 |
| ARRI Reference Tool | https://www.arri.com/en/learn-help/learn-help-camera-system/tools/arri-reference-tool | ART CMD가 ARRIRAW/MXF-ARRIRAW 처리, metadata JSON/CSV export, transcode/process 기능 제공 |
| ARRIRAW FAQ | https://www.arri.com/en/learn-help/learn-help-camera-system/pre-postproduction/file-formats-data-handling/arriraw-faq | ARRIRAW 확장자 `.ari` 또는 `.mxf`, de-bayer/color processing 필요 |
| FFprobe documentation | https://ffmpeg.org/ffprobe.html | MOV tmcd, MPEG GOP, DV/GXF/AVI timecode extraction |
| MediaInfo | https://mediaarea.net/en/MediaInfo | video/audio technical and tag metadata display, JSON/XML pivot output 지원 |

---

## 26. 요약 결정안

v1은 **포맷별 adapter 기반의 로컬 PDF 리포터**로 구현한다. 기본 PDF는 Layout B contact-sheet이며, 사용자가 상세 파일 옵션을 선택하면 Layout A 클립별 상세 리포트를 생성한다. 캡처 이미지는 기본적으로 PDF 내부에만 삽입하고, 별도 추출 옵션을 켰을 때만 PNG로 저장한다. BRAW/R3D/ARRIRAW는 각각 vendor SDK 또는 공식 reference tool 기반 adapter로 처리하며, 모든 포맷의 결과는 동일한 ClipInfo/CapturePoint schema로 정규화한다.
