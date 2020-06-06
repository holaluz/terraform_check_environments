FROM python:3
ENV TERRAFORM_VERSION="0.12.26"
RUN pip install --upgrade pip && \
  pip install --no-cache-dir termcolor pathlib
RUN curl https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip > terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
  unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /bin && \
  rm -f terraform_${TERRAFORM_VERSION}_linux_amd64.zip
RUN pip install --no-cache-dir awscli boto3
RUN echo "UserKnownHostsFile=/dev/null" >> /etc/ssh/ssh_config && \
  echo "StrictHostKeyChecking=no" >> /etc/ssh/ssh_config
ADD ./ /checker/



WORKDIR /workdir

CMD ["python3","/checker/terraform_check_environments.py"]
