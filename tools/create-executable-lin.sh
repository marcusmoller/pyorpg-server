echo "--------------------------------------------------------"
echo "PyORPG (Server) Executable Tool for GNU/Linux (using PyInstaller)"
echo "--------------------------------------------------------"

read -p "Choose a name for your executable (ex 'pyorpg-server'): " execname

echo "Building executable using PyInstaller..."
pyinstaller ../src/main.py -F -o ../tmp -n $execname

echo "Making bin folder if it doesnt exist..."
mkdir ../bin

echo "Moving binary into the bin folder..."
mv ../tmp/dist/$execname ../bin/

echo "Generating launcher for executable..."
echo '#!/bin/bash' >> ../$execname-lin
echo '# Generated launcher script for PyORPG' >> ../$execname-lin
echo "cd bin" >> ../$execname-lin
echo "./$execname" >> ../$execname-lin

echo "Setting permissions for launcher..."
chmod +x ../$execname-lin

echo "Done!"
echo "--------------------------------------------------------"
