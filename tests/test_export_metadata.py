from wsi_deid.export import tiff_resolution_from_mpp
from wsi_deid.export import inspect_tiff_pyramid


class DummySlide:
    properties = {
        "openslide.mpp-x": "0.5",
        "openslide.mpp-y": "0.25",
    }


def test_tiff_resolution_from_mpp_returns_pixels_per_centimeter():
    resolution, unit = tiff_resolution_from_mpp(DummySlide())

    assert resolution == (20000.0, 40000.0)
    assert unit == "CENTIMETER"


def test_inspect_tiff_pyramid_counts_subifd_levels(tmp_path):
    import numpy as np
    import tifffile

    path = tmp_path / "pyramid.ome.tif"
    base = np.zeros((64, 64, 3), dtype=np.uint8)
    level_1 = np.zeros((32, 32, 3), dtype=np.uint8)

    with tifffile.TiffWriter(path, bigtiff=True) as tif:
        tif.write(
            base,
            tile=(16, 16),
            photometric="rgb",
            subifds=1,
            metadata=None,
        )
        tif.write(
            level_1,
            tile=(16, 16),
            photometric="rgb",
            subfiletype=1,
            metadata=None,
        )

    info = inspect_tiff_pyramid(path)

    assert info["level_count"] == 2
    assert info["levels"][0]["shape"] == [64, 64, 3]
    assert info["levels"][1]["shape"] == [32, 32, 3]
