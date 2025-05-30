# Onos Controller Installations

## Requirements

- Install Ubuntu 22.04
- `sudo apt update`
- sudo apt install openjdk-11-jdk
- nano /etc/envinronment, add `JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64` to the end of line.
- sudo mkdir /opt ; cd /opt
- sudo wget -c https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.7.0/onos-2.7.0.tar.gz
- sudo tar -xvf onos-2.7.0.tar.gz
- sudo mv onos-2.7.0 onos
- sudo /opt/onos/bin/onos-service start
- sudo /opt/onos/bin/onos-service start
