from wsi_deid.export import tiff_resolution_from_mpp


class DummySlide:
    properties = {
        "openslide.mpp-x": "0.5",
        "openslide.mpp-y": "0.25",
    }


def test_tiff_resolution_from_mpp_returns_pixels_per_centimeter():
    resolution, unit = tiff_resolution_from_mpp(DummySlide())

    assert resolution == (20000.0, 40000.0)
    assert unit == "CENTIMETER"
