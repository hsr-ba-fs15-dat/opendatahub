.PHONY: dev clean gdal gdal-travis

clean:
	rm -rf env target src/main/webapp/node_modules src/main/webapp/bower_components

dev: gdal
	scripts/install_dev.sh

gdal:
	sudo apt-get install libxerces-c-dev libxerces-c3.1 -y && \
	curl -L http://download.osgeo.org/gdal/1.11.1/gdal-1.11.1.tar.gz -s -o - | tar xz -C . -f - && \
	cd gdal-1.11.1 && \
	./configure --with-pcraster=no \
		--with-jasper=no \
		--with-grib=no \
		--with-vfk=no \
		--with-hide-internal-symbols \
		--with-xerces && \
	sudo make install

gdal-travis:
	sudo apt-get install libxerces-c-dev libxerces-c3.1 -y && \
	curl -L https://www.dropbox.com/s/i9oxqzjgmmz3ba9/precise64-gdal-1.11.1.tar.tgz?dl=1 -s -o - | tar xz -C . -f - && \
	cd gdal-1.11.1 && \
	sudo make install
