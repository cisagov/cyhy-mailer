FROM python:3.11.0a5-alpine3.15
MAINTAINER Shane Frasier <jeremy.frasier@trio.dhs.gov>

# Install shadow so we have adduser and addgroup.  This is a build
# dependency that will be removed at the end.
#
# I also reinstall wget with openssl, since otherwise wget does not
# seem to know how to HTTPS.
RUN apk --no-cache add openssl shadow wget

# Update pip, setuptools, and wheel
RUN pip3 install --upgrade pip setuptools wheel

# Install cyhy-mailer
RUN mkdir cyhy-mailer
RUN wget -q -O - https://github.com/cisagov/cyhy-mailer/tarball/develop | tar xz --strip-components=1 -C cyhy-mailer
RUN pip3 install --upgrade ./cyhy-mailer

# Create unprivileged user
ENV MAILER_HOME=/home/mailer
RUN mkdir ${MAILER_HOME} \
    && addgroup -S mailer \
    && adduser -S -g "Mailer user" -G mailer mailer \
    && chown -R mailer:mailer ${MAILER_HOME}

# Remove build dependencies
RUN apk --no-cache del shadow

# Prepare to Run
WORKDIR ${MAILER_HOME}
USER mailer:mailer
ENTRYPOINT ["cyhy-mailer"]
CMD ["--help"]
