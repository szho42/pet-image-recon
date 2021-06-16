The default configuration of the reconstruction is in the **config.py**, which can be modified for different settings.


**How to reconstruct from list mode**
the script **recon_pet.py** is the main function for reconstrucing listmode into PET images.
the arguments are:
* listmode : the listmode data in STIR interfile format, that can be converted from vendor's format by using the tool, PET-RD-TOOL (https://github.com/UCL/pet-rd-tools)
* sinogram_prefix: the prefix for output of the intermediate sniogram file, default "sinogram_"
* norm_file : the normalization file in STIR interfile format, similarly, can be obtained using PET-RD-TOOL.
* umap : the uMap used for attenuation correction in the reconstruction, that can be converted with nm_mrac command in PET-RD-TOOL. Flags of "--head" needs to be enabled, and "--orient" needs to be set accordingly.
* start_time: the start time (in seconds) of the time window for binning listmode data. Default "0"
* end_time: the end time (in seconds) of the time window for binning listmode data, Default "inf"
* count_threshold: a value set for identifying the real start time, usually with a very small number, e.g. 10 and 20. In some data exported from scanner, the start time might not be 0, instead a random number. This threshold needs to set, to get the right time window with start_time and offset.
* output_prefix: the prefix for the result images, saved in nifti format.

** Example **
The below example shows the scripts used to i) create a template, where the scanner related information can be set; ii) reconstruct the PET image.

(1) Create template
> python3 create_template.py --output template

(2a) Static reconstruction:
> python3 recon_pet.py --listmode listmode.l.hdr --sinogram_template template.hs --norm_file norm.n.hdr --umap umap.hv --output_prefix output_static
the reconstructed PET image is saved as a file in 3D nifti format.


(2b) Dynamic reconstruction:
> python3 recon_pet.py --listmode listmode.l.hdr --sinogram_template template.hs --norm_file norm.n.hdr --umap umap.hv --output_prefix output_dynamic --start_time 600 --end_time 900
the dynamic PET image is saved as a file in 4D nifti format.

** Dataset **
The code is tested with the public dataset shared on OpenNeuro (**https://openneuro.org/datasets/ds003382**)