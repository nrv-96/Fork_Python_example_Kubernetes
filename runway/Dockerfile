ARG BASE_INFRA_IMAGE=290503755741.dkr.ecr.us-east-1.amazonaws.com/ccplatbuild/base-infra-container
FROM $BASE_INFRA_IMAGE
# Copy Infra Code into container
RUN mkdir -p /runway
COPY . /runway
WORKDIR /runway

ENTRYPOINT ["/runway/entrypoint.sh"]

CMD ["runway", "takeoff"]