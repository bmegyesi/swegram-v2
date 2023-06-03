

import os

from swegram_main.handler.parser import main_parser
from swegram_main.handler.visualization import Visualization
from swegram_main.lib.logger import get_logger
from swegram_main.pipeline.pipeline import Pipeline


ANNOTATION_PARSER = {
    "en": "udpipe",
    "sv": "efselab"
}


logger = get_logger(__file__)


class CommandLineError(Exception):
    """Command line error"""


def main():
    args = main_parser()
    logger.info(f"Command: {args.command}")
    logger.info(f"Input File/Directory: {args.input_path}")
    logger.info(f"Output Directory: {args.output_dir if args.output_dir else os.getcwd()}")

    if args.command == "annotate":
        logger.info(f"Normalization: {bool(args.NORMALIZE)}")
        pipeline = Pipeline(input_path=args.input_path, output_dir=args.output_dir, language=args.language)
        if args.NORMALIZE:
            pipeline.normalize()
        if args.PARSE or (not args.NORMALIZE and not args.TAG and not args.TOKENIZE):
            logger.info("Annotation: parse")
            pipeline.parse()
        elif args.TAG:
            logger.info("Annotation: tag")
            pipeline.tag()
        elif not args.NORMALIZE:
            logger.info("Annotation: tokenize")
            pipeline.tokenize()
        pipeline.postprocess(args.save_as, args.AGGREGATE)

    elif args.command == "statistic":
        logger.info("Swegram statistics")

        if args.include_metadata:
            logger.info(f"Include metadata: {args.include_metadata}")
        if args.exclude_metadata:
            logger.info(f"Exclude metadata: {args.exclude_metadata}")

        logger.info(f"UNITS: {args.UNITS}")
        logger.info(f"Aspects: {args.ASPECTS}")

        if args.include_features:
            logger.info(f"Include features: {args.include_features}")
        if args.exclude_features:
            logger.info(f"Exclude features: {args.exclude_features}")
        Visualization(
            args.input_path, language=args.language, output_dir=args.output_dir,
            include_tags=args.include_metadata, exclude_tags=args.exclude_metadata
        ).filter(
            args.UNITS, args.ASPECTS,
            include_features=args.include_features,
            exclude_features=args.exclude_features,
            pprint=args.PPRINT,
            save_as=args.save_as
        )

    else:
        raise CommandLineError(f"Unknown command, {args.command}")
