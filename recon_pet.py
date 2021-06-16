from sirf import STIR
from sirf import Reg
import argparse
from ast import literal_eval
import numpy as np
from sirf.Utilities import show_2D_array
from util import BinningConfig
from util import ListmodeData
from helper import get_image_resolution, get_image_voxel_size
from config import recon_parameters


def main(args):
    ##########
    # binning
    ##########
    listmode_data = ListmodeData(args.listmode)
    binning_config = BinningConfig(
        start=args.start_time, end=args.end_time, count_threshold=args.count_threshold
    )
    sinogram_data = listmode_data.to_sinogram(
        args.sinogram_template, recon_parameters.sino_pre, binning_config
    )

    ###################
    # estimate randoms
    ###################
    randoms_data = listmode_data.estimate_randoms()

    ################
    # initial image
    ################
    image_default = sinogram_data.create_uniform_image(
        1.0, literal_eval(recon_parameters.resolution)
    )

    ###################################
    # set image resolution and spacing
    ###################################
    if recon_parameters.resolution or recon_parameters.voxel_size:
        image = STIR.ImageData()
        image.initialise(
            get_image_resolution(image_default, recon_parameters.resolution),
            get_image_voxel_size(image_default, recon_parameters.voxel_size),
        )

    ###########################
    # define acquisition model
    ###########################
    acqusition_model = STIR.AcquisitionModelUsingRayTracingMatrix()
    acqusition_model.set_num_tangential_LORs(recon_parameters.num_LORs)

    #######################
    # read attenuation map
    #######################
    attn_image = STIR.ImageData(args.umap)

    ###############################################################
    # create acquisition sensitivity model from normalisation data
    ###############################################################
    asm_norm = STIR.AcquisitionSensitivityModel(args.norm_file)

    #############################
    # create attenuation factors
    #############################
    asm_attn = STIR.AcquisitionSensitivityModel(attn_image, acqusition_model)
    asm_attn.set_up(sinogram_data)
    bin_eff = sinogram_data.get_uniform_copy(value=1)
    asm_attn.unnormalise(bin_eff)
    asm_attn = STIR.AcquisitionSensitivityModel(bin_eff)

    #####################
    # scatter estimation
    #####################
    scatter_estimator = STIR.ScatterEstimator()

    scatter_estimator.set_input(sinogram_data)
    scatter_estimator.set_attenuation_image(attn_image)
    scatter_estimator.set_randoms(randoms_data)
    scatter_estimator.set_asm(asm_norm)

    acf_factors = sinogram_data.get_uniform_copy()
    acf_factors.fill(1 / bin_eff.as_array())
    scatter_estimator.set_attenuation_correction_factors(acf_factors)
    scatter_estimator.set_output_prefix(recon_parameters.sino_pre + "_scatter")
    scatter_estimator.set_num_iterations(3)
    scatter_estimator.set_up()
    scatter_estimator.process()
    scatter_estimate = scatter_estimator.get_output()

    #########################################
    # chain up attenuation and normalization
    #########################################
    asm = STIR.AcquisitionSensitivityModel(asm_norm, asm_attn)

    acqusition_model.set_acquisition_sensitivity(asm)
    acqusition_model.set_background_term(randoms_data + scatter_estimate)

    #################
    # reconstruction
    #################
    obj_fun = STIR.make_Poisson_loglikelihood(sinogram_data)
    obj_fun.set_acquisition_model(acqusition_model)
    recon = STIR.OSMAPOSLReconstructor()
    recon.set_objective_function(obj_fun)
    recon.set_num_subsets(recon_parameters.num_subsets)
    recon.set_num_subiterations(recon_parameters.num_subiterations)
    recon.set_up(image)
    recon.set_current_estimate(image)

    print("reconstructing...")
    recon.process()
    out = recon.get_output()

    #####################
    # Gaussian smoothing
    #####################
    smoothed = out.copy()

    gaussian_filter = STIR.SeparableGaussianImageFilter()
    gaussian_filter.set_fwhms(recon_parameters.fwhm)
    gaussian_filter.set_max_kernel_sizes(recon_parameters.max_kernel_size)
    gaussian_filter.set_normalise()
    gaussian_filter.set_up(smoothed)
    gaussian_filter.apply(smoothed)

    if args.output_prefix:
        Reg.NiftiImageData(smoothed).write(args.output_prefix)
        print("reconstructed images saved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--listmode", type=str, help="listmode file")
    parser.add_argument(
        "--sinogram_template",
        type=str,
        help="the generated sinogram template file",
    )
    parser.add_argument("--norm_file", type=str, help="normalization file")
    parser.add_argument("--umap", type=str, help="The attenuation umap file")
    parser.add_argument(
        "--start_time",
        type=float,
        default=0,
        help="start time of time window for resconstruction",
    )
    parser.add_argument(
        "--end_time",
        type=float,
        default=float("inf"),
        help="start time of time window for resconstruction",
    )
    parser.add_argument(
        "--output_prefix", type=str, default="output", help="the output filename prefix"
    )
    parser.add_argument(
        "--count_threshold",
        type=int,
        default=20,
        help="the count threshold to identify the real start time",
    )

    args = parser.parse_args()
    main(args)