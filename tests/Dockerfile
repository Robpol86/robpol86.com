FROM httpd:alpine
MAINTAINER Robpol86 <robpol86@gmail.com>

RUN sed -i -e "s/Options Indexes FollowSymLinks/Options -Indexes +FollowSymLinks/" \
    -e '\|<Directory "/usr/local/apache2/htdocs">|,\|</Directory>| s|AllowOverride None|AllowOverride All|' \
    -e 's/#LoadModule rewrite_module/LoadModule rewrite_module/' /usr/local/apache2/conf/httpd.conf

COPY htdocs /usr/local/apache2/htdocs/
