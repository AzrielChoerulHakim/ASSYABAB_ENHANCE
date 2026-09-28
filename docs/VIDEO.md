# Cahaya scroll film

The film is derived from the owner's supplied `18622.mp4`. The original file was
left unchanged and is not duplicated in this repository. The scene remains the
original Quran room, curtain transition, and multimedia workspace. This is a
careful edit and web encoding of that supplied film, not a regenerated scene.

## Editorial choices

- Trim 0.25 seconds from each end: 9.5 seconds at the original 24 fps.
- Reduce saturation slightly and ease the orange highlights, while retaining
  warm light, fabric texture, and the relationship between Quran and workspace.
- Retain the original composition and embedded provenance mark. No generative
  sharpening or frame interpolation was used.
- Remove the soundtrack from the scroll assets. Seeking should never scrub,
  repeat, or reverse speech; the page's optional sound is controlled separately.
- Match the poster to the first encoded frame to avoid a color or composition
  jump when the video becomes ready.

The curtain begins crossing the image at roughly 40% of the film. The new room
is revealed around 51–54%, with the final composition settling near 63%. These
are visual cue points, not frame-exact content boundaries.

## Delivered media

| Asset | Dimensions | Duration | Bytes |
| --- | --- | --- | ---: |
| `assets/cahaya-scroll.mp4` | 1280 × 720 | 9.5 s | 7,382,863 |
| `assets/cahaya-scroll-mobile.mp4` | 960 × 540 | 9.5 s | 3,866,806 |
| `assets/cahaya-poster.jpg` | 1280 × 720 | Still | 191,342 |

Both videos use H.264 High, level 3.1, `yuv420p`, a square pixel aspect ratio,
closed GOPs, and an IDR/keyframe every six frames (0.25 seconds). B-frames are
disabled to reduce the work required for repeated seeking. The MP4 `moov` box
precedes `mdat` (`faststart`) so duration and seeking metadata are available
before the entire download completes.

The frequent keyframes make these files larger than a normal playback encode.
That tradeoff is deliberate: the scene is controlled in both directions by
scroll. The smaller asset helps mobile transfers and decoding without changing
the aspect ratio or cropping the Quran out of the composition.

## Reproduce

Requirements: Python 3.10+ and FFmpeg built with `libx264`. No Python packages
are required. From the repository root:

```sh
python tools/prepare_video.py /path/to/18622.mp4 --ffmpeg /path/to/ffmpeg
```

Add `--contact-sheet /path/to/contact.jpg` for a 10-frame overview for visual QA.
Use `--output-dir /path/to/assets` to render elsewhere. The script replaces only
its three named output assets, decodes both videos completely to check for
corruption, and confirms that the original input checksum did not change.
Different FFmpeg/libx264 builds can produce different checksums.

## Verified output

Verified with FFmpeg 7.1: both files decode without errors, contain no audio,
and have 228 frames with 38 keyframes exactly six frames apart. The metadata box
is before the video payload in both files. A contact sheet was visually inspected
across the Quran, curtain, and computer scenes.

SHA-256 checksums for this render:

```text
source 18622.mp4:
bbc0c53aba271c321bbb45f127c0736e22a0b898bdcf6a386c8e4b7bd01dc957

cahaya-scroll.mp4:
4b9e97ea5ffeb452797a60df2f1ad9435d11c8f3d4b125dd3888792aca023842

cahaya-scroll-mobile.mp4:
4184bafdc144dcd1c363b99ffa7f5b14bdf1f77d73edfc1086ff06538d376fc5

cahaya-poster.jpg:
681bc1281bf01a80207384df0315f9316be9f61adf061f488266c1ccc9796b37
```
