.PHONY: dev clean gdal gdal-travis

clean:
	rm -rf env target src/main/webapp/node_modules src/main/webapp/bower_components

dev: gdal
	scripts/install_dev.sh

gdal:
	sudo apt-get install libkml0 libkml-dev libxerces-c-dev libxerces-c3.1 libproj0 libproj-dev proj-bin -y && \
	curl -L http://download.osgeo.org/gdal/1.10.1/gdal-1.10.1.tar.gz -s -o - | tar xz -C . -f - && \
	cd gdal-* && \
	./configure --with-pcraster=no \
		--with-jasper=no \
		--with-grib=no \
		--with-vfk=no \
		--with-hide-internal-symbols \
		--with-xerces \
		--with-libkml && \
	sudo rm -f /usr/local/lib/libgdal.so* && \
	sudo make install && \
	sudo ldconfig
