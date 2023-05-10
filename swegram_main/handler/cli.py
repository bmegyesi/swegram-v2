

import os
from swegram_main.handler.parser import main_parser
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
        logger.info(f"Normalization: {True if args.NORMALIZE else False}")
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
        pipeline.postprocess()

    elif args.command == "statistic":
        print("to do statistic commands")
        # Corpus(args.input_path, args.language, args.LEVELS).generate()
    else:
        raise CommandLineError(f"Unknown command, {args.command}")

if __name__ == "__main__":
    main()
