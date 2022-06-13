# install pandoc 2.18 for linux user
# To run this scirpt, please do
# . ./install.sh

wget https://github.com/jgm/pandoc/releases/download/2.18/pandoc-2.18-linux-amd64.tar.gz
tar -xzvf pandoc-2.18-linux-amd64.tar.gz
rm -r pandoc-2.18-linux-amd64.tar.gz
export PATH="$(pwd)/pandoc-2.18/bin:$PATH"

