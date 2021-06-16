from dataclasses import dataclass


@dataclass
class ReconParameters(object):
    scanner: str = "Siemens_mMR"
    span: int = 11
    max_ring_diff: int = 60
    view_mash_factor: int = 1
    num_LORs: int = 10

    resolution: str = "(344, 344)"
    voxel_size: str = "(1.39084, 1.39084)"

    num_subsets: int = 21
    num_subiterations: int = 40

    sino_pre: str = "recon"

    fwhm: tuple = (4, 4, 4)
    max_kernel_size: tuple = (5, 5, 5)


recon_parameters = ReconParameters()