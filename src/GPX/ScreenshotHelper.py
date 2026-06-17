import os
import piexif
from PIL import Image

def _to_dms(value):
    d = int(abs(value))
    m = int((abs(value)-d) * 60)
    s = round(((abs(value) - d ) * 60 - m) *60 * 1000)
    return ((d,1),(m,1),(s,1000))

def save_screenshot_with_exif(png_path, output_path, lat, lon):
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: b"N" if lat >= 0 else b"S",
        piexif.GPSIFD.GPSLatitude: _to_dms(lat),
        piexif.GPSIFD.GPSLongitudeRef: b"E" if lon >= 0 else b"W",
        piexif.GPSIFD.GPSLongitude: _to_dms(lon)
    }
    exif_bytes = piexif.dump({"GPS": gps_ifd})
    Image.open(png_path).save(output_path, "jpeg", exif=exif_bytes)
    os.remove(png_path)
