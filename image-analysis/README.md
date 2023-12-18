
# LibSSL1.1 dependency

To install 

``` BASH
wget -O - https://www.openssl.org/source/openssl-1.1.1w.tar.gz | tar zxf -
cd openssl-1.1.1w
./config --prefix=/usr/local
make -j $(nproc)
sudo make install_sw install_ssldirs
sudo ldconfig -v
```

# Export SSL CERT 
Make sure to habe the env variable in the terminal session launching python script to connect to Azure vision-ai 

```BASH
export SSL_CERT_DIR=/etc/ssl/certs # Must be in Environment
```

# Azure Api Keys

Store in .env file with 

AI_SERVICE_ENDPOINT=https://<EndpointURL>
AI_SERVICE_KEY=<YourKey>
