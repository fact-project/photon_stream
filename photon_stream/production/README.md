# Production

## Install Java 8 

```bash
mkdir java8
cd java8
```

go to [oracle java downloads](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)

and download:

- jdk-8u144-linux-x64.tar.gz for Linux x64

go to [maven](https://maven.apache.org/download.cgi)

and download:

- apache-maven-3.5.0-bin.tar.gz

```bash
ls
apache-maven-3.5.0-bin.tar.gz    jdk-8u144-linux-x64.tar.gz
```

untar both files:

```bash
tar -zxvf apache-maven-3.5.0-bin.tar.gz
tar -zxvf jdk-8u144-linux-x64.tar.gz
```

now the java8 directory looks like this

```bash
ls
apache-maven-3.5.0  apache-maven-3.5.0-bin.tar.gz  jdk1.8.0_144  jdk-8u144-linux-x64.tar.gz
```

Now set the java and maven path in your .bashrc

```bash
# JAVA HOME
#----------
export JAVA_HOME='/net/big-tank/POOL/projects/fact/smueller/java8/jdk1.8.0_144'
export PATH=$JAVA_HOME/bin/:$PATH

export MVN_HOME='/net/big-tank/POOL/projects/fact/smueller/java8/apache-maven-3.5.0'
export PATH=$MVN_HOME/bin:$PATH
```

## Install fact-tools

Download from github:

```bash
git clone https://github.com/fact-project/fact-tools.git
```

```bash
cd fact-tools
```

Checkout the photon-stream pass4 vesion of fact-tools:

```bash
git checkout 8a96abd8dc9e54ebfaedff97b093be72255d5b1f
```

Build fact-tools:

```bash
mvn package
```

This also runs the unit tests and should end with:

```bash
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
```


## Install photo-stream

```bash
git clone https://github.com/fact-project/photon_stream.git
pip install -e photon_stream/
```

# Publish on web server

https://ihp-pc41.ethz.ch/public/phs/

login to ihp-pc41 as user: factshifthelper

stop the running nginx webserver docker container

```bash
docker stop data_nginx
```

remove the former container

```bash
docker rm data_nginx
```

apply changes as needed to the config files in:

- index.html
- start_nginx.sh
- default.conf

build the updated docker container:

```bash
./start_nginx.sh
```
