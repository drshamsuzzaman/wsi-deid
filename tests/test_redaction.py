from PIL import Image, ImageDraw

from wsi_deid.redaction import redact_slide_ends


def test_redact_slide_ends_masks_both_ends():
    img = Image.new("RGB", (750, 250), (235, 239, 238))
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 25, 730, 225), fill=(220, 230, 230), outline=(100, 100, 100))
    draw.rectangle((30, 45, 190, 205), fill=(245, 245, 225), outline=(20, 20, 20))
    for x in range(50, 175, 12):
        draw.rectangle((x, 70, x + 5, 180), fill=(10, 10, 10))
    draw.text((610, 95), "B-300", fill=(20, 20, 20))

    redacted, mask, info = redact_slide_ends(
        img,
        barcode_side="left",
        barcode_end_mm=22,
        handwritten_end_mm=12,
    )

    assert info["barcode_side"] == "left"
    assert mask.getpixel((80, 100)) == 255
    assert mask.getpixel((690, 100)) == 255
    assert redacted.getpixel((80, 100)) == (255, 255, 255)
    assert redacted.getpixel((690, 100)) == (255, 255, 255)
