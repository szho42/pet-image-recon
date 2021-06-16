from ast import literal_eval


def get_image_resolution(image, resolution):
    nz, ny, nx = image.dimensions()

    if resolution:
        height, width = literal_eval(resolution)
        _image_size = (int(nz), int(height), int(width))
    else:
        _image_size = (nz, ny, nx)

    return _image_size


def get_image_voxel_size(image, voxel_size):
    vz, vy, vx = image.voxel_sizes()

    if voxel_size:
        spacing_x, spacing_y = literal_eval(voxel_size)
        _voxel_size = (float(vz), spacing_x, spacing_y)
    else:
        _voxel_size = (vz, vy, vx)

    return _voxel_size