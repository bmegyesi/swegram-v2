

import os
from swegram_main.handler.parser import main_parser
from swegram_main.pipeline.pipeline import Pipeline
from swegram_main.lib.logger import get_logger


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
        logger.info(f"Normalization: {True if args.NORMALIZE else False}")
        pipeline = Pipeline(filepath=args.input_path, output_dir=args.output_dir)
        if args.NORMALIZE is True:
            pipeline.normalize(f"histnorm_{args.language}")
        if args.TAG is True:
            logger.info(f"Annotation: tag")
            pipeline.tag(ANNOTATION_PARSER[args.language])
        elif args.TOKENIZE is True and not args.NORMALIZE:
            logger.info(f"Annotation: tokenize")
            pipeline.tokenize(ANNOTATION_PARSER[args.language])
        else:
            logger.info(f"Annotation: parse")
            # default session for annotation
            pipeline.parse(ANNOTATION_PARSER[args.language])
    elif args.command == "statistic":
        ...
    else:
        raise CommandLineError(f"Unknown command, {args.command}")
