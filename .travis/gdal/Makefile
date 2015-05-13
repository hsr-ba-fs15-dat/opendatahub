.PHONY: gdal vagrant

gdal:
	sudo apt-get install --ignore-missing -y subversion python-numpy python-dev postgis postgresql-server-dev-9.1 postgresql-9.1-postgis libpq-dev libpng12-dev libjpeg-dev libgif-dev liblzma-dev libgeos-dev libcurl4-gnutls-dev libproj-dev libxml2-dev libexpat-dev libxerces-c-dev libxerces-c3.1 libnetcdf-dev netcdf-bin libpoppler-dev libspatialite-dev gpsbabel swig libhdf4-alt-dev libhdf5-serial-dev libpodofo-dev poppler-utils libfreexl-dev unixodbc-dev libwebp-dev openjdk-7-jdk libepsilon-dev liblcms2-2 libpcre3-dev libjasper-dev libarmadillo-dev make g++ autoconf cmake bison flex libkml0 libkml-dev vim && \
	sudo ldconfig && \
	curl -L http://download.osgeo.org/gdal/1.11.1/gdal-1.11.1.tar.gz -s -o - | tar xz -C . -f - && \
	cd gdal-1.11.1 && \
	sudo mkdir -p /home/travis/build/gdal && \
	sudo ./configure --prefix=/home/travis/build/gdal \
		--with-pcraster=no \
		--with-jasper=no \
		--with-grib=no \
		--with-vfk=no \
		--with-hide-internal-symbols \
		--with-xerces && \
	sudo make install && \
	cd /home/travis/build/gdal && \
	sudo cp /usr/lib/libxerces* ./lib && \
	sudo cp /usr/lib/libicu* ./lib && \
	tar zcf /vagrant/gdal-1.11.1-precise64.tar.gz .

vagrant:
	vagrant init precise64 && \
	vagrant up && \
	vagrant ssh
