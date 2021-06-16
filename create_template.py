from util import SinogramTemplate
import argparse
from config import recon_parameters


def main(args):
    sino_template = SinogramTemplate(
        args.scanner if args.scanner else recon_parameters.scanner,
        span=args.span if args.span else recon_parameters.span,
        max_ring_diff=args.max_ring_diff
        if args.max_ring_diff
        else recon_parameters.max_ring_diff,
        view_mash_factor=args.view_mash_factor
        if args.view_mash_factor
        else recon_parameters.view_mash_factor,
    ).create()

    print("template created.")

    if args.output:
        sino_template.write(args.output)
        print(f"templated saved as {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scanner",
        type=str,
        default="Siemens mMR",
        help="the scanner specified to create the sinogram template",
    )
    parser.add_argument(
        "--span", type=int, default=11, help="the scanner span parameter"
    )
    parser.add_argument(
        "--max_ring_diff", type=int, default=60, help="the maximal ring difference"
    )
    parser.add_argument(
        "--view_mash_factor", type=int, default=1, help="view mash factor"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="the filename to save the template"
    )

    args = parser.parse_args()

    main(args)