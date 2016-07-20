#!/bin/bash

FILE="$1"
#FILE=/home/lpzhang/Desktop/crawler/gettyimages/fpath.txt
EXTENSION=.jpg

USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"

if [ ! -f $FILE ]; then
	echo "$FILE : does not exists"
	exit 1
elif [ ! -r $FILE ]; then
	echo "$FILE : can not read"
	exit 2
fi

echo "Start..."
while read fpath; do
	#skip empty line and skip comments
	[[ -z "$fpath" ]] && continue
	if [ "${fpath:0:1}" != "#" ]; then
		# create outdir for save images
		outdir="${fpath%.*}"
		mkdir $outdir
        echo "output dir: ${outdir}"
        #start calculate the time
        SECONDS=0

		while read line; do
			#skip empty line and skip comments
			[[ -z "$line" ]] && continue
			if [ "${line:0:1}" != "#" ]; then
				# get id and url
				ele=( $line )
				img_name=${ele[0]}$EXTENSION
				img_url=${ele[1]}
				# download images to img_path
				img_path=${outdir}'/'${img_name}
                # if img_path exists, then skip
                if [ -f "$img_path" ]
                then
                    echo "$img_path found."
                else
                    # use wget to download images
                    wget $img_url -O $img_path
                    echo "${img_name} downloaded to: ${img_path}"
                fi
			fi
		done < $fpath
        #calculate the duration
        duration=$SECONDS
        echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
        echo "---------------------"
        echo " "
	fi
done < $FILE

echo "...Done"
