FROM python:3.6.3-alpine3.6
MAINTAINER Shane Frasier <jeremy.frasier@beta.dhs.gov>

# Install git so we can checkout the cyhy-mailer got repo.  Install
# shadow, so we have adduser and addgroup.  These are all build
# dependencies that will be removed at the end.
RUN apk update && \
    apk add git shadow

# Install mailer
RUN pip install git+https://github.com/jsf9k/cyhy-mailer.git

# Create unprivileged user
ENV MAILER_HOME=/home/mailer
RUN mkdir ${MAILER_HOME} \
    && addgroup -S mailer \
    && adduser -S -g "Mailer user" -G mailer mailer \
    && chown -R mailer:mailer ${MAILER_HOME}

# Remove build dependencies
RUN apk del git shadow

# Prepare to Run
WORKDIR MAILER_HOME
USER mailer:mailer
ENTRYPOINT ["cyhy-mailer"]
CMD ["--help"]
