#!/usr/bin/env bash

while getopts ":i:f:" option; do
    case "${option}" in
    	i)
            INPUT_FILE="${OPTARG}"
            echo "$INPUT_FILE";;
		f)
            FILEFORMAT="${OPTARG}"
            echo "$FILEFORMAT";;
    	*)
			break;;
    esac
done

docker run -it python_developer_test_unittests
docker run -it -v $(pwd)/data_output:/matmatch/data_output python_developer_test "$INPUT_FILE" "$FILEFORMAT"