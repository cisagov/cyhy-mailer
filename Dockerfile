FROM python:3.6.3-alpine3.6
MAINTAINER Shane Frasier <jeremy.frasier@beta.dhs.gov>

# Install shadow, so we have adduser and addgroup
RUN apk update && \
    apk add shadow

# Dependencies
RUN pip3 install pymongo pyyaml

# Create unprivileged user
ENV SCANNER_HOME=/home/scanner
RUN addgroup -S scanner \
    && adduser -S -g "Scanner user" -G scanner scanner

# Prepare to Run
WORKDIR $SCANNER_HOME
ENTRYPOINT ["./save_to_db.sh"]

# This goes at the end because docker will always rerun the copy
# command (and anything that goes after it)
COPY . $SCANNER_HOME
RUN chown -R scanner:scanner ${SCANNER_HOME}
