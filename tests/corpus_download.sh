
output_file="${1:-sv-en.tgz}"
output_path="${2:-sv-en}"

if [ -z $output_file ]
then
  echo "Please Specify the output folder name"
else
  if [ -f $output_file ]
  then
    echo "$output_file exists, skip downloading"
  else
    curl --fail --silent --show-error --retry 5 --retry-delay 2 https://www.statmt.org/europarl/v7/sv-en.tgz -H "Accept: application/json" --output $output_file
  fi
  mkdir $output_path
  tar -xzvf $output_file -C $output_path
  rm $output_file
fi
