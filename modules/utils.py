import gtk

def scale_pixbuf(pixbuf, width, height):
    pixbuf_width = int(pixbuf.get_width())
    pixbuf_height = int(pixbuf.get_height())

    # By default, attempt to match the display's height
    image_height = int(height)
    image_width = int(
        float(image_height * pixbuf_width) / float(pixbuf_height))

    # If the resulting width is wider than needed, match the display's width
    # instead

    if image_width > width:
        image_width = int(width)
        image_height = int(
            float(image_width * pixbuf_height) / float(pixbuf_width))

    assert image_width <= width
    assert image_height <= height

    scaled_pixbuf = pixbuf.scale_simple(
        image_width, image_height, gtk.gdk.INTERP_HYPER)

    return scaled_pixbuf

