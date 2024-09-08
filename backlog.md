feature

1. How to maintain data saved in the server
    * Retention policy


2. Restriction on input
    * corpus size
    * file type

3. Integration test


4. Notes for the future developer working with Swegram

    The following components we have achieved with swegram
    * swegram cli
    * swegram gui
    * dockerized container
        * nginx + static files built on vue framework
        * fastapi to provide API for text parsing, file generation, interaction with database
        * mysql used for fast data processing

    The components that can be improved from a developer's view
    * More test cases are required to protect the product, from unit testing till end2end test
    * We need more pipeline to automate or simplify the process for deployment.
        * These pipelines will benefit the users who are not able to build docker image or static files to serve frontend pages.
    * Better doucmentation. (Documentation for developers and for end users.)

