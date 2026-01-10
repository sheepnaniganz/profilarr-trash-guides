# Run tests on output data stored in regex_patterns, custom_formats and profiles
# Ensure al references are correct and no broken links have been generated.

# Every custom format pattern should exist in regex_patterns by a file with the same name.
# Every profile custom format reference should exist in custom_formats by a file with the same name.
# If a file can not be found the test should fail.

# Tests should cover all the files in the output directories, it can be assumed the data has been updated already.
# Instructions should exist in README on how to run the tests.
# Pytest framework is used for the tests
# Tests are run in github actions - after generation completion.
