#!/usr/bin/env bash

while getopts ":i:f:" option; do
    case "${option}" in
    	i)
            INPUT_FILE="${OPTARG}";;
		f)
            FILEFORMAT="${OPTARG}";;
    	*)
			break;;
    esac
done

echo "Running unittests"
docker run -it python_developer_test_unittests
echo "Finished unittests"

echo "Running main"
docker run -it -v $(pwd)/data_output:/matmatch/data_output python_developer_test "$INPUT_FILE" "$FILEFORMAT"
echo "Finished main"