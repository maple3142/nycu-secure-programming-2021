FROM ubuntu:20.04
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update --fix-missing
RUN apt-get upgrade -y
RUN apt-get install socat sagemath -y
COPY chal.sage /chal.sage
COPY secret.py /secret.py
COPY run.sh /run.sh
CMD ["socat", "TCP-LISTEN:7122,fork,reuseaddr", "EXEC:/run.sh"]
