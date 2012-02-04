import gtk

def scale_pixbuf(pixbuf, width, height):
    pixbuf_width = int(pixbuf.get_width())
    pixbuf_height = int(pixbuf.get_height())

    image_height = int(0.9 * height)
    image_width = int(
        (float(image_height * pixbuf_width)) / float(pixbuf_height))

    scaled_pixbuf = pixbuf.scale_simple(
        image_width, image_height, gtk.gdk.INTERP_HYPER)

    return scaled_pixbuf

