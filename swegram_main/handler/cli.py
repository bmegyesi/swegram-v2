

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
            if args.TAG or args.PARSE:
                pipeline.normalize(f"histnorm_{args.language}")
            else:
                logger.info(f"Annotation: normalize")
                pipeline.run(f"histnorm_{args.language}", "normalize")

        if args.PARSE is True:
            action = "parse"
        elif args.TAG is True:
            action = "tag"
        elif args.TOKENIZE is True and not args.NORMALIZE:
            action = "tokenize"
        elif args.NORMALIZE:
            action = None
        else:
            # default session for annotation
            action = "parse"
        if action:
            logger.info(f"Annotation: {action}")
            pipeline.run(ANNOTATION_PARSER[args.language], action)

    elif args.command == "statistic":
        ...
    else:
        raise CommandLineError(f"Unknown command, {args.command}")

if __name__ == "__main__":
    main()
