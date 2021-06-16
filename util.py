from sirf import STIR
import typing
from dataclasses import dataclass


class SinogramTemplate(object):
    def __init__(
        self,
        scanner: str = "Siemens_mMR",
        span: int = 11,
        max_ring_diff: int = 60,
        view_mash_factor: int = 1,
    ):
        self.scanner = scanner = scanner
        self.span = span
        self.max_ring_diff = max_ring_diff
        self.view_mash_factor = view_mash_factor

    def create(self) -> STIR.AcquisitionData:
        self._acq_data = STIR.AcquisitionData(
            self.scanner,
            span=self.span,
            max_ring_diff=self.max_ring_diff,
            view_mash_factor=self.view_mash_factor,
        )
        return self._acq_data

    def get_template(self) -> STIR.AcquisitionData:
        return self._acq_data

    def get_shape(self):
        return self._acq_data.shape

    def write(self, filename) -> None:
        self._acq_data.write(f"{filename}.hs")


@dataclass
class BinningConfig(object):
    start: float = 0
    end: float = float("inf")
    count_threshold: int = 10


class ListmodeData(object):
    def __init__(self, listmode_file: str):
        self._listmode_file = listmode_file
        self._lm2sino = STIR.ListmodeToSinograms()
        self._lm2sino.set_input(self._listmode_file)
        self._sinogram = None
        self._randoms = None

    def to_sinogram(
        self,
        template_file: str,
        prefix: str = "sinogram_",
        binning: BinningConfig = None,
    ) -> STIR.AcquisitionData:
        self._lm2sino.set_output_prefix(prefix)
        self._lm2sino.set_template(template_file)

        if binning:
            self.time_shift = self.get_time_by_count_threshold(binning.count_threshold)
            if self.time_shift > 0:
                self._lm2sino.set_time_interval(
                    binning.start + self.time_shift, binning.end + self.time_shift
                )

        self._lm2sino.set_up()
        print("start conversion...")
        self._lm2sino.process()

        self._sinogram = self._lm2sino.get_output()

        return self._sinogram

    def get_time_by_count_threshold(self, count_threshold):
        return self._lm2sino.get_time_at_which_num_prompts_exceeds_threshold(
            count_threshold
        )

    def estimate_randoms(self):
        if self._sinogram:
            self._randoms = self._lm2sino.estimate_randoms()
            return self._randoms

        return None

    def get_sinogram(self):
        return self._sinogram

    def get_randoms(self):
        return self._randoms


class uMAP(object):
    def __init__(self, mu_map_file: str):
        self._mu_map_file = mu_map_file
        self._umap = STIR.ImageData(self._mu_map_file)

    @property
    def shape(self):
        return self._umap.shape


@dataclass
class ImageResolution:
    height: int
    width: int


# class SinogramData(object):
#     def __init__(self):
#         pass

#     def fit(self):
#         pass
