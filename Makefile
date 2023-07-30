export MAYA_BIN = C:\Program Files\Autodesk\Maya2022\bin
export MAYA_PY = ${MAYA_BIN}/mayapy.exe

.PHONY: clean build docs install_package publish demo_thumbnail demo

clean:
	rm -rf "build"

build: clean
	echo "Build Start"
	pyeal build
	echo "Build End"

install_package: build
	7z -tzip a ./build/build.zip ./build/out/*

docs: README.md
	pandoc -f markdown -t html README.md -o README.html --css=README.css --self-contained
