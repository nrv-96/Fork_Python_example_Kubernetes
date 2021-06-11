FROM 290503755741.dkr.ecr.us-east-1.amazonaws.com/ccplatbuild/base-infra-container

WORKDIR /stacks

COPY stacker.yaml local-setup.sh requirements.tx[t] hook[s] lambda[s] lookup[s] stacke[r] /stacks/

RUN [ -f "requirements.txt" ] && pip install -r requirements.txt

ENTRYPOINT [ "/bin/sh", "-c", "sh local-setup.sh && stacker" ]
